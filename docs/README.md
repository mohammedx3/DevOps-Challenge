# Tornado App

## Key Additions
### 1. **Dockerfile**
- **Purpose:** Builds a lightweight Docker image for the Tornado app.
- **Key Features:**
  - Based on `python:3.12-alpine` for minimal size and performance.
  - Installs only necessary Python dependencies listed in `requirements.txt`.
  - Copies application files (`hello.py`, `static/`, `templates/`).
  - Adds a non-root user (`appuser`) for improved security.
  - Exposes port `8000` for the application.
  - Entry point runs the Tornado application (`hello.py`).

**Benefits:**  
- Creates a secure, production-ready image.
- Optimized for Kubernetes deployment.

---

### 2. **Helm Chart (`deploy/helm`)**
- **Purpose:** Simplifies the deployment of the Tornado app on Kubernetes.
- **Structure:**
  - **`values.yaml`:** Configures default settings (e.g., Redis connection details, app environment).
  - **`templates/`:** Includes Kubernetes manifests for:
    - **Deployment:** Configures app replicas, container image, environment variables, and readiness probes.
    - **Service:** Exposes the app to other services or external traffic.
    - **ConfigMap:** Manages app configuration (optional).
  - **`values-dev.yaml` and `values-prod.yaml`:** Environment-specific configurations.

**Benefits:**  
- Enables flexible, parameterized deployments.
- Integrates readiness and health checks for Kubernetes compatibility.


## Enhancements and changes
### 1. **Redis Connection Handling**
- Added a `connect_redis()` function with retry logic (30 attempts, 1-second intervals).
- Added support for Redis authentication via `REDIS_PASSWORD`.
- Configured connection options (timeouts, retries, health checks).

**Reason:** Improves fault tolerance and handles Redis startup delays in distributed environments.

---

### 2. **Kubernetes Health and Readiness Endpoints**
- Added `/health` (basic health check) and `/ready` (verifies Redis connection).
- `/ready` returns HTTP `503` if Redis is unreachable.

**Reason:** Enables Kubernetes to monitor app health and readiness during deployments.

---

### 3. **Environment Variables with Defaults**
- Added defaults for `ENVIRONMENT`, `HOST`, `PORT`, `REDIS_PORT`, and `REDIS_DB`.

**Reason:** Makes the app flexible for different environments and prevents missing-variable errors.

---

### 4. **Enhanced Error Handling**
- Improved `MainHandler` to handle Redis errors gracefully (e.g., fallback message on failure).

**Reason:** Provides better user feedback and error resilience.

---

### 5. **Improved Observability**
- Added detailed logs for Redis connection attempts and app startup.

**Reason:** Simplifies debugging and monitoring.

---

### 6. **Kubernetes-Friendly Updates**
- Added a retry mechanism for Redis connectivity to handle initialization delays.
- Included `/health` and `/ready` endpoints for smoother integration with Kubernetes.

---

### Benefits
- **Reliability**: Handles Redis connection issues with retries and graceful error messages.
- **Kubernetes Compatibility**: Health and readiness checks ensure seamless deployments.
- **Flexibility**: Environment variable defaults simplify configuration.
- **Production-Ready**: Improved logging, security (Redis password), and error handling.

## Workflow Overview
### 1. **Triggering Events**
The pipeline is triggered on the following events:
- **Push Events**:
  - Direct pushes to the `master` branch.
  - Tags matching the pattern `v*` (e.g., `v1.0.0`).

### 2. **Pipeline Stages**
#### **Tests**
- Executes unit tests, linting, and security checks for both Helm charts and Python code.
- Runs tools like `pytest`, `flake8`, `pylint`, `bandit`, and `safety` to ensure code quality and security.
- Verifies Helm charts using `helm lint` and `helm unittest`.
- Uploads security reports as artifacts.

#### **Build**
- Builds a Docker image for the application.
- Dynamically tags the Docker image based on the branch or tag:
  - Commits to `master`: Tagged as `dev`.
  - Tags matching `v*`: Tagged as `prod`, `latest`, and the version (e.g., `v1.0.0`).
- Scans the Docker image for vulnerabilities using Trivy.
- Publishes the Docker image to DockerHub.

## Key Details
### Ingress Configuration
- The application is currently running using a **dummy ingress host** for demonstration purposes.
- **Production Consideration:** In a real-world scenario, the ingress should be linked to a proper DNS record, which can be automatically created based on the cloud or cluster setup (e.g., using external-dns in Kubernetes).

### HTTP vs HTTPS
- The application is configured to run on **HTTP** for simplicity.
- **Production Consideration:** The app should be secured with **HTTPS** by:
  - Using a TLS certificate managed by tools like **Cert-Manager**.
  - Configuring the ingress to terminate HTTPS connections based on the cluster/cloud provider's capabilities.

---

## Benefits
This configuration demonstrates how the app can be deployed to Kubernetes with basic ingress routing. However, production deployments should implement DNS integration and HTTPS for security and reliability.
