# ---------- BUILD STAGE ----------
FROM ros:jazzy AS builder

WORKDIR /workspace

# WHY: Copy only required files first (better caching)
COPY app/ros2_ws/src ./src

RUN apt-get update && apt-get install -y python3-pip

# Install dependencies
RUN . /opt/ros/jazzy/setup.sh && colcon build

# ---------- RUNTIME STAGE ----------
FROM ros:jazzy

# WHY: Non-root user for security
RUN useradd -m rosuser
USER rosuser

WORKDIR /home/rosuser

COPY --from=builder /workspace/install ./install
COPY docker/entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]