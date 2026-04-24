# -------- Stage 1: Builder --------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -------- Stage 2: Runtime (ROS2) --------
FROM ros:jazzy

WORKDIR /app

# Copy python deps
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy app
COPY app/ /app/app

ENV PYTHONUNBUFFERED=1
ENV ROS2_ENABLED=false  
EXPOSE 8000

CMD ["python3", "-m", "app.main"]