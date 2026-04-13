#include "engine.h"
#include <iostream>
#include <vector>
#include <cmath>

int main() {
    InferenceEngine engine;
    
    // 1. Load the Sentinel Brain
    if (!engine.load("sentinel_model.bin")) {
        std::cerr << "CRITICAL ERROR: sentinel_model.bin missing or corrupted." << std::endl;
        return 1;
    }

    std::cout << "--- NASA SENTINEL EDGE AI ACTIVATED ---" << std::endl;
    std::cout << "Monitoring sensor streams..." << std::endl;

    // 2. Mock Live Sensor Input (17 active NASA sensors)
    // In a real implementation, these would be read from a sensor bus (I2C/SPI)
    std::vector<float> live_sensors = {
        643.02f, 1585.29f, 1398.21f, 14.62f, 21.61f, 
        553.90f, 2388.04f, 9050.17f, 47.20f, 521.72f, 
        2388.03f, 8133.24f, 8.4195f, 0.03f, 392.0f, 
        38.86f, 23.3735f
    };

    // 3. Perform Edge Inference
    auto result = engine.predict(live_sensors);
    
    // Convert raw logit to probability
    float prob = 1.0f / (1.0f + std::exp(-result[0]));

    // 4. Alert Logic
    std::cout << "\nInference Results:" << std::endl;
    std::cout << ">> Raw Activation Signal: " << result[0] << std::endl;
    std::cout << ">> Failure Probability:   " << (prob * 100.0f) << "%" << std::endl;
    
    if (prob > 0.5f) {
        std::cout << ">> STATUS: [DANGER] FAILURE IMMINENT. SCHEDULE MAINTENANCE." << std::endl;
    } else {
        std::cout << ">> STATUS: [NOMINAL] SYSTEM STABLE." << std::endl;
    }

    return 0;
}
