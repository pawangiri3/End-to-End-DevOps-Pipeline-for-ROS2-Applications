#!/bin/bash

echo "Creating full DevOps project structure..."

# App structure
mkdir -p app/ros2_ws/src/hello_ros2/{hello_ros2,test,resource}

# Docker
mkdir -p docker

# Kubernetes
mkdir -p k8s

# Monitoring
mkdir -p monitoring/{prometheus,grafana,loki}

# GitHub Actions
mkdir -p .github/workflows

# Scripts
mkdir -p scripts

# App files
touch app/ros2_ws/src/hello_ros2/package.xml
touch app/ros2_ws/src/hello_ros2/setup.py
touch app/ros2_ws/src/hello_ros2/setup.cfg

touch app/ros2_ws/src/hello_ros2/hello_ros2/__init__.py
touch app/ros2_ws/src/hello_ros2/hello_ros2/talker.py
touch app/ros2_ws/src/hello_ros2/hello_ros2/listener.py

touch app/ros2_ws/src/hello_ros2/test/test_talker.py

# Docker files
touch docker/Dockerfile
touch docker/entrypoint.sh

# Kubernetes files
touch k8s/{namespace.yaml,deployment.yaml,service.yaml,ingress.yaml}

# Monitoring files
touch monitoring/prometheus/prometheus.yml
touch monitoring/grafana/datasource.yml
touch monitoring/loki/loki-config.yml

# CI/CD
touch .github/workflows/ci.yml

# Misc
touch README.md
touch scripts/run_local.sh

echo "Project structure created successfully 🚀"