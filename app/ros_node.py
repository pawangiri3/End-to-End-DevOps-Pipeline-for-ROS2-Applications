"""
ros_node.py
-----------
ROS2 integration layer.

• Publishes commands to /robot_command (std_msgs/String)
• Subscribes to   /robot_status  (std_msgs/String)
• Simulates robot state internally when a real robot is absent
• Gracefully degrades when rclpy is not available (ROS2_ENABLED=False)
"""

from __future__ import annotations

import json
import logging
import random
import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Try to import ROS2 — fall back gracefully when unavailable
# ---------------------------------------------------------------------------
_ROS2_AVAILABLE = False
if settings.ROS2_ENABLED:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String

        _ROS2_AVAILABLE = True
        logger.info("rclpy imported successfully — ROS2 mode ACTIVE")
    except ImportError:
        logger.warning("rclpy not found — running in SIMULATION mode")
else:
    logger.info("ROS2_ENABLED=False — running in SIMULATION mode")


# ---------------------------------------------------------------------------
# Shared application state (singleton, thread-safe primitives)
# ---------------------------------------------------------------------------
class RobotState:
    """Thread-safe container for robot metrics and status."""

    VALID_STATUSES = {"Idle", "Moving", "Turning Left", "Turning Right", "Stopped"}

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.status: str = "Idle"
        self.command_count: int = 0
        self.log_buffer: Deque[Dict[str, Any]] = deque(maxlen=settings.MAX_LOG_ENTRIES)
        self.last_command: str = ""
        self.uptime_start: float = time.time()

    # -- Status ----------------------------------------------------------

    def set_status(self, new_status: str) -> None:
        if new_status not in self.VALID_STATUSES:
            logger.warning("Unknown status received: %s", new_status)
            return
        with self._lock:
            self.status = new_status

    def get_status(self) -> str:
        with self._lock:
            return self.status

    # -- Commands --------------------------------------------------------

    def record_command(self, command: str) -> None:
        with self._lock:
            self.command_count += 1
            self.last_command = command
        self._append_log("COMMAND", f"Received command: {command}", {"command": command})

    # -- Logs ------------------------------------------------------------

    def _append_log(self, level: str, message: str, extra: dict | None = None) -> None:
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
        }
        if extra:
            entry.update(extra)
        with self._lock:
            self.log_buffer.append(entry)

    def get_logs(self, limit: int = 50) -> list[dict]:
        with self._lock:
            entries = list(self.log_buffer)
        return entries[-limit:]

    # -- Metrics ---------------------------------------------------------

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "command_count": self.command_count,
                "current_status": self.status,
                "last_command": self.last_command,
                "uptime_seconds": round(time.time() - self.uptime_start, 2),
            }


# ---------------------------------------------------------------------------
# Module-level singleton — imported everywhere
# ---------------------------------------------------------------------------
robot_state = RobotState()


# ---------------------------------------------------------------------------
# Simulation helpers (used when ROS2 is unavailable)
# ---------------------------------------------------------------------------
_STATUS_TRANSITIONS: Dict[str, str] = {
    "MOVE_FORWARD": "Moving",
    "TURN_LEFT": "Turning Left",
    "TURN_RIGHT": "Turning Right",
    "STOP": "Stopped",
    "RESET": "Idle",
}

_SETTLE_DELAYS: Dict[str, float] = {
    "Moving": 3.0,
    "Turning Left": 2.0,
    "Turning Right": 2.0,
    "Stopped": 1.5,
}


def _simulate_robot_response(command: str) -> None:
    """Mimic robot behaviour in a background thread (no real ROS2 needed)."""
    new_status = _STATUS_TRANSITIONS.get(command, "Idle")
    robot_state.set_status(new_status)
    robot_state._append_log(
        "INFO",
        f"[SIM] Robot transitioned to '{new_status}'",
        {"command": command, "status": new_status},
    )

    settle_time = _SETTLE_DELAYS.get(new_status, 2.0)
    time.sleep(settle_time + random.uniform(0, 0.5))  # small jitter

    # Auto-return to Idle unless STOP was issued
    if new_status not in {"Stopped", "Idle"}:
        robot_state.set_status("Idle")
        robot_state._append_log(
            "INFO",
            f"[SIM] Robot returned to 'Idle' after completing '{command}'",
            {"command": command, "status": "Idle"},
        )


# ---------------------------------------------------------------------------
# ROS2 Node class (only instantiated when rclpy is available)
# ---------------------------------------------------------------------------
if _ROS2_AVAILABLE:

    class RobotCommandNode(Node):  # type: ignore[misc]
        """
        ROS2 node that bridges FastAPI ↔ ROS2 topics.

        Publisher : /robot_command  (std_msgs/String)
        Subscriber: /robot_status   (std_msgs/String)
        """

        def __init__(self) -> None:
            super().__init__(settings.ROS2_NODE_NAME)

            # Publisher
            self._pub = self.create_publisher(
                String,
                settings.COMMAND_TOPIC,
                qos_profile=10,
            )

            # Subscriber
            self._sub = self.create_subscription(
                String,
                settings.STATUS_TOPIC,
                self._status_callback,
                qos_profile=10,
            )

            # Timer: publish a heartbeat every 5 s
            self.create_timer(5.0, self._heartbeat_callback)

            self.get_logger().info(
                f"RobotCommandNode started — pub={settings.COMMAND_TOPIC} "
                f"sub={settings.STATUS_TOPIC}"
            )
            robot_state._append_log("INFO", "ROS2 node initialised", {"node": settings.ROS2_NODE_NAME})

        # -- Callbacks ---------------------------------------------------

        def _status_callback(self, msg: Any) -> None:
            """Handle incoming status messages from the robot."""
            status = msg.data.strip()
            robot_state.set_status(status)
            robot_state._append_log(
                "INFO",
                f"Status update received: {status}",
                {"topic": settings.STATUS_TOPIC, "status": status},
            )

        def _heartbeat_callback(self) -> None:
            robot_state._append_log(
                "DEBUG",
                "Heartbeat — node alive",
                {"uptime": robot_state.get_metrics()["uptime_seconds"]},
            )

        # -- Command API -------------------------------------------------

        def publish_command(self, command: str) -> None:
            """Publish a command string to /robot_command and simulate internally."""
            msg = String()
            msg.data = command
            self._pub.publish(msg)
            robot_state.record_command(command)
            robot_state._append_log(
                "INFO",
                f"Published command '{command}' to {settings.COMMAND_TOPIC}",
                {"topic": settings.COMMAND_TOPIC, "command": command},
            )
            # Also simulate the response (since we have no real subscriber loop here)
            thread = threading.Thread(
                target=_simulate_robot_response,
                args=(command,),
                daemon=True,
            )
            thread.start()


# ---------------------------------------------------------------------------
# Node manager — singleton that owns the rclpy spin thread
# ---------------------------------------------------------------------------
class ROS2Manager:
    """Lifecycle manager: start / stop the ROS2 node in a background thread."""

    def __init__(self) -> None:
        self._node: "RobotCommandNode | None" = None
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        if _ROS2_AVAILABLE:
            self._start_ros2()
        else:
            self._start_simulation()

    def _start_ros2(self) -> None:
        logger.info("Initialising ROS2 runtime …")
        rclpy.init()
        self._node = RobotCommandNode()
        self._running = True

        def _spin() -> None:
            try:
                rclpy.spin(self._node)
            except Exception as exc:
                logger.error("ROS2 spin error: %s", exc)

        self._thread = threading.Thread(target=_spin, daemon=True, name="ros2-spin")
        self._thread.start()
        logger.info("ROS2 spin thread started")

    def _start_simulation(self) -> None:
        logger.info("Starting in SIMULATION mode (no ROS2)")
        robot_state._append_log("INFO", "Running in simulation mode — no real robot connected")

    def stop(self) -> None:
        if _ROS2_AVAILABLE and self._node:
            try:
                self._node.destroy_node()
                rclpy.shutdown()
                logger.info("ROS2 shutdown complete")
            except Exception as exc:
                logger.warning("Error during ROS2 shutdown: %s", exc)

    def publish_command(self, command: str) -> None:
        """Entry point called by API routes."""
        robot_state.record_command(command)
        if _ROS2_AVAILABLE and self._node:
            self._node.publish_command(command)
        else:
            # Pure simulation path
            thread = threading.Thread(
                target=_simulate_robot_response,
                args=(command,),
                daemon=True,
            )
            thread.start()


# Module-level manager instance
ros2_manager = ROS2Manager()
