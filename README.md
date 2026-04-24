# 🤖 ROS2 Robot Command Center

> Production-ready FastAPI + ROS2 Jazzy dashboard — built for DevOps & Kubernetes interviews.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)
![ROS2](https://img.shields.io/badge/ROS2-Jazzy-green?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square)
![Kubernetes](https://img.shields.io/badge/Kubernetes-manifest-326CE5?style=flat-square)

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

---

## Quickstart

### Option A — Pure Python (no ROS2 installed)

```bash
cd ros2-robot-dashboard

# Install deps
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run in simulation mode
ROS2_ENABLED=false uvicorn app.main:app --host 0.0.0.0 --port 8000

# Open http://localhost:8000
# Login: admin / r0b0t123
```

### Option B — Docker (recommended)

```bash
# Build
docker build -t ros2-robot-dashboard:latest .

# Run
docker run -p 8000:8000 \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -e ROS2_ENABLED=true \
  ros2-robot-dashboard:latest
```

### Option C — Docker Compose

```bash
docker compose up --build
```

---

## API Reference

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
