# 🤖 Rudra 2.0 Robot Command Center
> End-to-End DevOps Pipeline for ROS2 Applications | Production-ready FastAPI + ROS2 Jazzy dashboard

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![ROS2](https://img.shields.io/badge/ROS2-Jazzy-green?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square)
![Kubernetes](https://img.shields.io/badge/Kubernetes-manifest-326CE5?style=flat-square)
![Terraform](https://img.shields.io/badge/Terraform-Azure-purple?style=flat-square)
![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-red?style=flat-square)

---

## 📋 Table of Contents
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Azure Infrastructure (Terraform)](#azure-infrastructure)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Docker Container                  │
│                                                      │
│  ┌──────────────┐     ┌──────────────────────────┐  │
│  │  FastAPI App │     │      ROS2 Node           │  │
│  │              │────▶│  Publisher:/robot_command │  │
│  │  /login      │     │  Subscriber:/robot_status │  │
│  │  /dashboard  │◀────│  Heartbeat timer (5s)    │  │
│  │  /api/*      │     │                          │  │
│  └──────┬───────┘     └──────────────────────────┘  │
│         │                                            │
│  ┌──────▼───────┐                                   │
│  │  Simulation  │  (auto-fallback when no real robot)│
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
```

### Infrastructure Stack
```
┌─────────────────────────────────────────────┐
│            Azure Cloud (Terraform)          │
├─────────────────────────────────────────────┤
│ • Azure Kubernetes Service (AKS)            │
│ • Azure Container Registry (ACR)            │
│ • Azure Networking (VNet, NSG)              │
│ • Application Gateway / Ingress Nginx       │
│ • Key Vault for secrets                     │
│ • Log Analytics / Application Insights      │
└─────────────────────────────────────────────┘
         ↓
    Helm Charts
         ↓
┌─────────────────────────────────────────────┐
│  Kubernetes Cluster (Dev/Prod/Staging)      │
├─────────────────────────────────────────────┤
│ • Prometheus + Grafana (Monitoring)         │
│ • Loki (Log Aggregation)                    │
│ • ArgoCD (GitOps Deployment)                │
│ • Application Pods                          │
└─────────────────────────────────────────────┘
```

## Features

| Feature | Details |
|---|---|
| **Authentication** | Session cookies (itsdangerous signed tokens, SHA-256 hashed passwords) |
| **Dashboard** | Real-time robot status ring, command buttons, telemetry log, metrics |
| **ROS2 Integration** | rclpy publisher + subscriber on `/robot_command` & `/robot_status` |
| **Simulation Mode** | Full fallback when `ROS2_ENABLED=false` — no real robot needed |
| **Structured Logging** | JSON log entries with timestamps, streamed to dashboard |
| **Metrics** | Command count, uptime, last command, per-session bar chart |
| **Health Endpoint** | `/api/health` — ready for k8s liveness / readiness probes |
| **API Docs** | Auto-generated at `/api/docs` (Swagger UI) |
| **Multi-Environment** | Dev, Staging, Prod with separate Terraform configs |
| **GitOps** | ArgoCD auto-deployment from Git |
| **Monitoring** | Prometheus ServiceMonitor, Grafana dashboards, Loki logs |

---

## 🚀 Quick Start

### Option A — Pure Python (no ROS2 installed)

```bash
# Clone repo
git clone <repo-url>
cd End-to-End-DevOps-Pipeline-for-ROS2-Applications

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in simulation mode
ROS2_ENABLED=false uvicorn app.main:app --host 0.0.0.0 --port 8000

# Open http://localhost:8000
# Login: admin / r0b0t123
```

### Option B — Docker (recommended)

```bash
# Build image
docker build -t ros2-robot-dashboard:latest .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e ROS2_ENABLED=false \
  ros2-robot-dashboard:latest

# Access: http://localhost:8000
```

### Option C — Docker Compose (full stack with monitoring)

```bash
docker compose up --build -d

# Access application: http://localhost:8000
# Access Grafana: http://localhost:3000
# Access Prometheus: http://localhost:9090
# Access Loki: http://localhost:3100
```

---

## 📌 Local Development

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional)
- Kubernetes cluster (kind/minikube for testing)
- Terraform 1.5+ (for Azure infrastructure)

### Environment Variables

Create `.env` file in project root:

```bash
# Application
SECRET_KEY=your-secret-key-here
ROS2_ENABLED=false  # Set to true if ROS2 is installed
DEBUG=true
LOG_LEVEL=INFO

# Optional: ROS2 Settings
ROS_DOMAIN_ID=0
ROS_LOCALHOST_ONLY=1

# Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_STORAGE_ACCOUNT=your-storage-account
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov fastapi httpx

# Run tests
pytest tests/ -v --cov=app

# With HTML coverage report
pytest tests/ --cov=app --cov-report=html
```

---

## 🐳 Docker Deployment

### Build Image

```bash
# Development image
docker build -t ros2-robot-dashboard:dev --target development .

# Production image (multi-stage)
docker build -t ros2-robot-dashboard:latest .

# Push to Azure Container Registry
az acr login --name <your-acr-name>
docker tag ros2-robot-dashboard:latest <your-acr>.azurecr.io/ros2-robot-dashboard:latest
docker push <your-acr>.azurecr.io/ros2-robot-dashboard:latest
```

### Docker Compose Services

```yaml
Services included:
- app (FastAPI + ROS2)
- prometheus (metrics collection)
- grafana (visualization)
- loki (log aggregation)
- promtail (log shipper)
```

---

## ☸️ Kubernetes Deployment

### Prerequisites
- kubectl configured
- Helm 3+
- AKS cluster or similar

### Deploy with Helm

```bash
# Add Helm repository (if using external charts)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install application
helm install rudra-app ./helm/rudra-app \
  -f ./envs/dev/values.yaml \
  -n default

# Verify deployment
kubectl get pods
kubectl logs -f deployment/rudra-app

# Port forward for testing
kubectl port-forward svc/rudra-app 8000:8000
```

### Manual Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Monitor
kubectl get all
kubectl describe pod <pod-name>
```

### ArgoCD GitOps Deployment

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Create Application resource
kubectl apply -f argocd/dev-app.yaml  # or prod-app.yaml

# Get ArgoCD admin password
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d

# Port forward to ArgoCD UI
kubectl port-forward -n argocd svc/argocd-server 8080:443
```

---

## 🏗️ Azure Infrastructure (Terraform)

### Prerequisites
- Azure CLI installed and configured
- Terraform 1.5+
- Azure subscription with permissions

### Initialize Terraform

```bash
# Setup Azure backend (one-time)
cd infra/envs/dev

# Login to Azure
az login
az account set --subscription <your-subscription-id>

# Initialize Terraform backend
terraform init \
  -backend-config="resource_group_name=Do_not_delete_rg" \
  -backend-config="storage_account_name=donotdelete2026" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=dev.tfstate"

# Plan infrastructure
terraform plan -var-file=terraform.tfvars

# Apply changes
terraform apply -var-file=terraform.tfvars
```

### Terraform Modules

| Module | Purpose |
|--------|---------|
| `resource_group` | Azure Resource Group creation |
| `networking` | VNet, Subnets, Network Security Groups |
| `aks` | Azure Kubernetes Service cluster |
| `acr` | Azure Container Registry |
| `key_vault` | Secrets management |
| `log_analytics` | Monitoring & diagnostics |
| `ingress_nginx` | Ingress controller |
| `dns` | Azure DNS zones |

### Terraform Variables (terraform.tfvars)

```hcl
location                = "eastus"
environment             = "dev"
aks_vm_size             = "Standard_B2s"
aks_node_count          = 1
acr_sku                 = "Standard"
log_analytics_retention = 30
```

---

## 📊 Monitoring & Logging

### Prometheus Configuration

Access Prometheus at `http://localhost:9090` or via Kubernetes port-forward.

Scrape configs defined in `monitoring/prometheus/prometheus.yml`

### Grafana Dashboards

```bash
# Access Grafana
http://localhost:3000
# Default: admin / admin
```

Dashboards included:
- Kubernetes cluster metrics
- Application performance
- Pod resource usage
- Request latency

### Loki Log Aggregation

```bash
# Query logs via Grafana or Loki API
curl http://localhost:3100/loki/api/v1/query_range \
  -G -d 'query={job="docker-compose"}' \
  -d 'start=<timestamp>' \
  -d 'end=<timestamp>'
```

---

## 🔄 CI/CD Pipeline

### Azure DevOps Pipeline

Pipeline stages:
1. **Terraform_Plan** - Initialize and plan infrastructure
   - Validates Terraform configuration
   - Generates plan file

2. **Terraform_Scan** - Security scanning
   - TFLint: Terraform linting
   - Checkov: Security compliance checks
   - All-continue-on-error for visibility

3. **Terraform_Cost** - Cost estimation
   - Infracost: Breakdown infrastructure costs

4. **Approval** - Manual approval gate
   - Notifies stakeholder for review
   - 1 day timeout

5. **Terraform_Apply** - Infrastructure deployment
   - Applies Terraform changes
   - Auto-approve for CI/CD

### Trigger Pipeline

```bash
# Manually trigger (pipeline currently set to manual trigger)
# Via Azure DevOps UI: Queue new build

# Or push to trigger (once branches are enabled)
git push origin main
```

### View Pipeline Status

```bash
# Via Azure CLI
az pipelines run list --project <project-name> --pipeline-id <pipeline-id>

# View logs
az pipelines run show --id <run-id> --project <project-name>
```

---

## 📚 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/login` | ✗ | Login page |
| `POST` | `/login` | ✗ | Authenticate (form) |
| `GET` | `/dashboard` | ✓ | Mission control UI |
| `POST` | `/logout` | ✓ | Clear session |
| `POST` | `/api/command` | ✓ | Send robot command |
| `GET` | `/api/status` | ✓ | Robot status + count |
| `GET` | `/api/logs` | ✓ | Telemetry log entries |
| `GET` | `/api/metrics` | ✓ | Operational metrics |
| `GET` | `/api/health` | ✗ | Health check |
| `GET` | `/api/docs` | ✗ | Swagger UI |

### Commands

```json
POST /api/command
{ "command": "MOVE_FORWARD" }

Valid commands: MOVE_FORWARD | TURN_LEFT | TURN_RIGHT | STOP | RESET
```

### Health response

```json
{
  "status": "healthy",
  "app": "ROS2 Robot Command Center",
  "version": "1.0.0",
  "robot_status": "Idle",
  "uptime_seconds": 42.1,
  "timestamp": 1714000000.0
}
```

---

## Project Structure

```
ros2-robot-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app factory, logging, lifecycle
│   ├── auth.py          # Session tokens, password verification
│   ├── config.py        # Pydantic settings (env vars)
│   ├── ros_node.py      # ROS2 node + simulation fallback + shared state
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── web.py       # HTML page routes (login, dashboard, logout)
│   │   └── api.py       # REST JSON endpoints
│   ├── templates/
│   │   ├── login.html   # Industrial ops-center login UI
│   │   └── dashboard.html  # Mission control dashboard
│   └── static/
│       └── style.css
├── Dockerfile            # Multi-stage build (builder + ros:jazzy-ros-base)
├── docker-compose.yml    # Local dev
├── k8s-deployment.yaml   # Namespace, Deployment, Service, Ingress
├── requirements.txt
└── README.md
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (insecure default) | Session signing key — **change in prod** |
| `ROS2_ENABLED` | `true` | Set `false` for simulation-only mode |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listen port |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LOG_FORMAT` | `json` | `json` for prod, `text` for human dev |
| `MAX_LOG_ENTRIES` | `200` | Rolling log buffer size |
| `ROS_DOMAIN_ID` | `0` | ROS2 DDS domain |
| `SESSION_MAX_AGE` | `86400` | Cookie lifetime in seconds |

---

## Kubernetes Deployment

```bash
# Apply all manifests (Namespace, ConfigMap, Secret, Deployment, Service, Ingress)
kubectl apply -f k8s-deployment.yaml

# Watch rollout
kubectl rollout status deployment/robot-dashboard -n robotics

# Check health
kubectl port-forward svc/robot-dashboard-svc 8000:80 -n robotics
curl http://localhost:8000/api/health

# View logs
kubectl logs -f deployment/robot-dashboard -n robotics
```

The deployment is configured with:
- **Liveness probe** — restarts pod if `/api/health` fails 3× 
- **Readiness probe** — removes pod from load balancer during startup
- **Resource limits** — 1 CPU / 512 MB RAM
- **Non-root user** — runs as UID 1000
- **Privilege escalation disabled**

---

## ROS2 Topics

```bash
# From host (if container shares host network)
source /opt/ros/jazzy/setup.bash

ros2 topic echo /robot_command
ros2 topic echo /robot_status
ros2 topic pub /robot_command std_msgs/String "data: 'MOVE_FORWARD'"
```

---

## Demo Credentials

| Username | Password |
|---|---|
| `admin` | `r0b0t123` |
| `devops` | `demo2024` |

---

## What This Demonstrates

- **ROS2 integration** — rclpy publisher/subscriber, lifecycle management, DDS config
- **FastAPI design** — Pydantic models, dependency injection, middleware, lifecycle hooks
- **Containerization** — Multi-stage Docker build, non-root user, health checks
- **Kubernetes-ready** — Probes, ConfigMaps, Secrets, resource limits, Ingress
- **Observability** — Structured JSON logging, metrics endpoint, real-time log streaming
- **Security** — HMAC-signed sessions, SHA-256 password hashing, HttpOnly cookies
- **Graceful degradation** — Full simulation mode when no real robot is present

---

## 🔧 Troubleshooting

### Application Issues

**Q: App won't start — "ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

**Q: Login page works but dashboard shows "Unauthorized"**
```bash
# Check if session cookie is being set
# Browser DevTools → Application → Cookies → session

# Try logging out and clearing cookies
# Then login again with: admin / r0b0t123
```

**Q: "ROS2 node failed to initialize" error**
```bash
# Run in simulation mode if ROS2 is not installed
ROS2_ENABLED=false uvicorn app.main:app --reload

# Or install ROS2 Jazzy following official guide:
# https://docs.ros.org/en/jazzy/Installation.html
```

**Q: Metrics/Logs endpoint returns 404**
```bash
# Check if endpoint is exposed at /api/metrics and /api/logs
curl http://localhost:8000/api/health

# View full API docs
# http://localhost:8000/api/docs
```

### Docker Issues

**Q: "docker: command not found"**
```bash
# Install Docker
# https://docs.docker.com/engine/install/

# On Windows/Mac, use Docker Desktop
# https://www.docker.com/products/docker-desktop
```

**Q: Port 8000 already in use**
```bash
# Find process using port 8000
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -i :8000

# Use different port
docker run -p 9000:8000 ros2-robot-dashboard:latest
```

**Q: "permission denied" running Docker**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo docker build -t ros2-robot-dashboard:latest .
```

**Q: Docker image build fails**
```bash
# Check Docker logs
docker build --no-cache -t ros2-robot-dashboard:latest . 2>&1 | tail -20

# Verify Dockerfile exists
ls -la Dockerfile

# Try building with verbose output
docker build -t ros2-robot-dashboard:latest --progress=plain .
```

### Kubernetes Issues

**Q: Pod stuck in "Pending" state**
```bash
# Check resource availability
kubectl describe pod <pod-name>

# Check node resources
kubectl top nodes

# Scale down if needed
kubectl scale deployment rudra-app --replicas=1
```

**Q: "ImagePullBackOff" error**
```bash
# Verify image exists in registry
az acr repository list --name <your-acr-name>

# Check image pull secret
kubectl get secrets -n default

# Re-create secret if needed
kubectl create secret docker-registry <secret-name> \
  --docker-server=<your-acr>.azurecr.io \
  --docker-username=<username> \
  --docker-password=<password>
```

**Q: Service won't get external IP / LoadBalancer pending**
```bash
# On minikube/kind, use port-forward instead
kubectl port-forward svc/rudra-app 8000:8000

# Check service status
kubectl describe svc rudra-app
```

**Q: Pod logs show connection refused**
```bash
# View full logs
kubectl logs <pod-name> -f

# Check if service is reachable from pod
kubectl exec <pod-name> -- curl http://localhost:8000/api/health
```

### Terraform Issues

**Q: "Error: Error acquiring the lease for this backend"**
```bash
# Terraform state is locked, likely from a crashed previous run
# Force unlock (use with caution!)
terraform force-unlock <lock-id>

# Or remove old lock manually
az storage blob delete \
  --account-name donotdelete2026 \
  --container-name tfstate \
  --name dev.tfstate.lock
```

**Q: "insufficient permissions" when applying Terraform**
```bash
# Check current Azure account
az account show

# Verify subscription access
az account list

# Set correct subscription
az account set --subscription <subscription-id>
```

**Q: "Variable file not found: terraform.tfvars"**
```bash
# Create terraform.tfvars in infra/envs/dev/
cat > infra/envs/dev/terraform.tfvars << EOF
location    = "eastus"
environment = "dev"
aks_vm_size = "Standard_B2s"
aks_node_count = 1
EOF

terraform plan -var-file=terraform.tfvars
```

**Q: "Module not found" error**
```bash
# Reinitialize Terraform
rm -rf .terraform
terraform init

# Or update modules
terraform get -update
```

### Pipeline Issues

**Q: Azure DevOps pipeline fails with "error"**
```bash
# Check pipeline run details in Azure DevOps UI
# Pipeline → Run → View logs

# Common issues:
# - TerraformTask@5 version too new/old
# - Terraform backend not accessible
# - Missing service principal credentials
```

**Q: "TFLint docker image not found"**
```bash
# Ensure Docker is running
docker ps

# Pre-pull images locally
docker pull ghcr.io/terraform-linters/tflint:latest
docker pull bridgecrew/checkov:latest
docker pull infracost/infracost:latest
```

**Q: Manual approval times out**
```bash
# Check notification email was sent to: chandanjataha@gmail.com
# Update email in pipeline if different

# Re-queue pipeline to try again
# Pipeline → Run → Queue
```

### Monitoring Issues

**Q: Prometheus not scraping metrics**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify ServiceMonitor exists (Kubernetes)
kubectl get servicemonitor -A

# Check app is exposing metrics
curl http://<app-ip>:8000/metrics
```

**Q: Grafana dashboards empty**
```bash
# Verify Prometheus data source is configured
# Grafana UI → Configuration → Data Sources → Prometheus

# Check Prometheus query works
# http://localhost:9090/graph
# Query: up{job="prometheus"}
```

**Q: Loki shows "no data"**
```bash
# Verify Loki is running and accessible
curl http://localhost:3100/api/v1/label/job/values

# Check promtail is shipping logs
docker logs <promtail-container> | tail -20

# Verify log label format in loki-config.yml
```

### General Debugging

**Enable verbose logging:**
```bash
# Application
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Docker Compose
docker compose --verbose up

# Terraform
TF_LOG=DEBUG terraform apply

# Kubernetes
kubectl get events -A
kubectl describe node
```

**Check system resources:**
```bash
# Python process memory
ps aux | grep uvicorn

# Docker resource usage
docker stats

# Kubernetes resources
kubectl top pods
kubectl top nodes
```

**Network connectivity test:**
```bash
# Test app connectivity
curl -v http://localhost:8000/api/health

# Test Kubernetes service DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://rudra-app:8000/api/health
```

---

## 📞 Support & Links

- **ROS2 Docs**: https://docs.ros.org/en/jazzy/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Terraform Azure**: https://registry.terraform.io/providers/hashicorp/azurerm/
- **Azure DevOps**: https://dev.azure.com/
- **ArgoCD**: https://argo-cd.readthedocs.io/
- **Prometheus**: https://prometheus.io/
- **Grafana**: https://grafana.com/

---

## 📝 License

MIT License — See LICENSE file for details

---

**Made for DevOps & Kubernetes interviews** 🚀  
**Last updated**: April 2026
