"""
config.py
---------
Centralised settings loaded from environment variables.
All secrets / tunables live here — never hardcoded in business logic.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Rudra 2.0"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    SESSION_COOKIE_NAME: str = "ros2_session"
    SESSION_MAX_AGE: int = 86_400  # 24 hours

    # ROS2
    ROS2_NODE_NAME: str = "robot_dashboard_node"
    COMMAND_TOPIC: str = "/robot_command"
    STATUS_TOPIC: str = "/robot_status"
    ROS2_ENABLED: bool = True          # Set False in pure-Python environments

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"           # "json" | "text"

    # Metrics
    MAX_LOG_ENTRIES: int = 200         # Rolling buffer size

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
