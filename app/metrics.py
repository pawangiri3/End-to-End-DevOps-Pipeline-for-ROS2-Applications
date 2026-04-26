"""
app/metrics.py
--------------
Centralised Prometheus metrics registry.

Rules enforced here:
  • NO imports from app.main, app.ros_node, or app.config
  • All other modules import FROM here — never the other way around
  • This guarantees zero circular-import risk across the entire codebase

Prometheus scrape endpoint:  GET /metrics  (registered in main.py)
Kubernetes ServiceMonitor:   points at /metrics, port 8000
"""

from prometheus_client import Counter, Histogram, Gauge, Info

# ── Counters ──────────────────────────────────────────────────────────────
command_counter = Counter(
    "rudra_command_total",
    "Total robot commands executed",
    ["command"],          # label lets Grafana break down by command type
)

http_requests_total = Counter(
    "rudra_http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status_code"],
)

# ── Histograms ─────────────────────────────────────────────────────────────
request_duration_seconds = Histogram(
    "rudra_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

# ── Gauges ─────────────────────────────────────────────────────────────────
robot_status_gauge = Gauge(
    "rudra_robot_status",
    "Current robot status encoded as integer (0=Idle 1=Moving 2=TurnLeft 3=TurnRight 4=Stopped)",
)

uptime_seconds_gauge = Gauge(
    "rudra_uptime_seconds",
    "Application uptime in seconds",
)

# ── Info ────────────────────────────────────────────────────────────────────
app_info = Info(
    "rudra_app",
    "Static application metadata",
)
app_info.info({
    "name":    "Rudra 2.0",
    "version": "2.0.0",
    "stack":   "FastAPI + ROS2 Jazzy",
})

# ── Helper: keep robot_status_gauge in sync ────────────────────────────────
_STATUS_CODES: dict[str, int] = {
    "Idle":          0,
    "Moving":        1,
    "Turning Left":  2,
    "Turning Right": 3,
    "Stopped":       4,
}


def update_robot_status_gauge(status: str) -> None:
    """Call this whenever robot status changes."""
    robot_status_gauge.set(_STATUS_CODES.get(status, 0))