# 🚀 NASA Sentinel | Edge AI Predictive Maintenance

![Edge AI](https://img.shields.io/badge/Status-Production--Ready-brightgreen)
![C++](https://img.shields.io/badge/Engine-C%2B%2B-blue)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)
![NASA](https://img.shields.io/badge/Dataset-NASA%20CMAPSS-orange)

**Sentinel** is a high-performance Edge AI inference system designed for real-time predictive maintenance of NASA turbofan engines. Built with an ultra-lightweight C++ core and a stunning glassmorphism-styled dashboard, it provides instantaneous health diagnostics for complex aerospace systems.

---

## ✨ Key Features

-   **⚡ Ultra-Fast C++ Engine**: A custom inference engine built for speed and efficiency, capable of running on low-power edge devices.
-   **📊 Real-Time Dashboard**: A premium, interactive web interface for monitoring fleet health and simulating sensor failure states.
-   **📡 RESTful API**: Seamlessly integrate with external sensors via the `/predict` endpoint.
-   **🐳 Containerized Deployment**: Multi-stage Docker builds ensure a tiny footprint and "run anywhere" capability.
-   **🛠️ Diagnostic Simulator**: Full 17-axis sensor override using real NASA CMAPSS data ranges.

---

## 🏗️ Architecture

The system is split into three primary layers:

1.  **The Brain (`sentinel_model.bin`)**: Quantized weights and inference logic optimized for edge performance.
2.  **The Engine (`compiler/main.cpp`)**: A C++ service that loads the model, provides the REST API, and serves the static dashboard.
3.  **The Interface (`web/`)**: A modern, responsive dashboard built with vanilla CSS and JS, utilizing glassmorphism for a premium look and feel.

---

## 🚀 Quick Start

### Running with Docker (Recommended)
The fastest way to get Sentinel up and running is via Docker:

```bash
# Build the production image
docker build -t sentinel-edge-ai .

# Run the engine
docker run -p 8080:8080 sentinel-edge-ai
```
Once running, navigate to `http://localhost:8080` to access the dashboard.

### Local Development
To compile and run locally, ensure you have a C++ compiler and the necessary headers:

1.  **Compile the engine**:
    ```bash
    g++ -O3 -o sentinel_engine compiler/main.cpp
    ```
2.  **Start the server**:
    ```bash
    ./sentinel_engine
    ```

---

## 🛠️ API Reference

### POST `/predict`
Submit sensor data for real-time analysis.

**Payload**: A comma-separated string of 17 sensor values.
**Example**:
```bash
curl -X POST -d "642.68,1590,1409,553.4,2388.1,9065,47.5,521.4,2388.1,8144,8.44,393,38.8,23.29,..." http://localhost:8080/predict
```

**Response**:
```json
{
  "probability": 0.012,
  "status": "NOMINAL"
}
```

---

## 📁 Repository Structure

```text
.
├── compiler/           # C++ Inference Engine source code
├── web/                # Glassmorphism Dashboard (HTML/CSS/JS)
├── data/               # NASA CMAPSS dataset samples
├── kernels/            # (Future) Optimized CUDA kernels
├── Dockerfile          # Multi-stage production build script
├── sentinel_model.bin  # Compiled model weights
└── README.md           # You are here
```

---

## 🛡️ License
This project is for educational and research purposes, utilizing publicly available NASA datasets.

---
<p align="center">
  <i>Developed for the Edge of Tomorrow — "Silicon to Synapse"</i>
</p>
