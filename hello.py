#!/usr/bin/env python3
"""
Tornado web application with Redis integration for counting page visits.
Includes health and readiness checks for Kubernetes compatibility.
"""
import os
import sys
import time
# pylint: disable=import-error
import redis
import tornado.ioloop
import tornado.web
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError
)

# Constants
MAX_ATTEMPTS = 30
RETRY_INTERVAL = 1

def connect_redis():
    """
    Establish connection to Redis with retry mechanism.
    
    Returns:
        Redis client instance.
    
    Raises:
        SystemExit: If unable to connect after MAX_ATTEMPTS.
    """
    redis_host = os.getenv("REDIS_HOST")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "0"))
    redis_password = os.getenv("REDIS_PASSWORD")

    attempt = 0
    while attempt < MAX_ATTEMPTS:
        try:
            print(f"Connecting to Redis at {redis_host}:{redis_port}...")
            redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            redis_client.set("counter", 0)
            print("Successfully connected to Redis")
            return redis_client
        except (RedisConnectionError, RedisTimeoutError) as e:
            attempt += 1
            print(f"Redis connection attempt {attempt}/{MAX_ATTEMPTS} failed: {str(e)}")
            if attempt >= MAX_ATTEMPTS:
                print("Max connection attempts reached. Exiting...")
                sys.exit(1)
            time.sleep(RETRY_INTERVAL)
    return None  # This line is never reached but satisfies pylint


# Connect to Redis with retry
REDIS_CLIENT = connect_redis()

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "PROD")
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8000"))


class MainHandler(tornado.web.RequestHandler):
    """Handler for the main page that displays visit counter."""

    def data_received(self, chunk):
        """
        Handle streamed request data.

        Args:
            chunk: Chunk of request data
        """
        # Not used in this implementation but required by ABC

    def get(self):
        """Handle HTTP GET request to the main page."""
        try:
            counter = REDIS_CLIENT.incr("counter", 1)
        except (RedisConnectionError, RedisTimeoutError):
            counter = "unavailable (Redis connection error)"

        self.render(
            "index.html",
            dict={"environment": ENVIRONMENT, "counter": counter},
        )


class HealthHandler(tornado.web.RequestHandler):
    """Handler for Kubernetes health checks."""

    def data_received(self, chunk):
        """
        Handle streamed request data.

        Args:
            chunk: Chunk of request data
        """

    def get(self):
        """Handle HTTP GET request to the health endpoint."""
        self.write({"status": "healthy"})


class ReadinessHandler(tornado.web.RequestHandler):
    """Handler for Kubernetes readiness checks that verify Redis connectivity."""

    def data_received(self, chunk):
        """
        Handle streamed request data.

        Args:
            chunk: Chunk of request data
        """

    def get(self):
        """Handle HTTP GET request to the readiness endpoint."""
        try:
            # Try to ping Redis to check connectivity
            REDIS_CLIENT.ping()
            self.write({"status": "ready"})
        except (RedisConnectionError, RedisTimeoutError):
            self.set_status(503)
            self.write({"status": "not ready - Redis connection error"})


class Application(tornado.web.Application):
    """Main Tornado web application."""

    def __init__(self):
        """Initialize the application with handlers and settings."""
        handlers = [
            (r"/", MainHandler),
            (r"/health", HealthHandler),
            (r"/ready", ReadinessHandler),
        ]
        settings = {
            "template_path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "templates"
            ),
            "static_path": os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "static"
            ),
        }
        super().__init__(handlers, **settings)


if __name__ == "__main__":
    app = Application()
    app.listen(PORT)
    print(f"App running: http://{HOST}:{PORT}")
    tornado.ioloop.IOLoop.current().start()
