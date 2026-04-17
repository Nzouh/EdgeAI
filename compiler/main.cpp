#include "engine.h"
#include "httplib.h"
#include <cmath>
#include <iostream>
#include <sstream>
#include <vector>

int main() {
  InferenceEngine engine;

  // 1. Load the Sentinel Brain
  if (!engine.load("sentinel_model.bin")) {
    std::cerr << "CRITICAL ERROR: sentinel_model.bin missing!" << std::endl;
    return 1;
  }

  httplib::Server svr;

  // Enabling CORS so our frontend can talk to the C++ server
  svr.set_post_routing_handler([](const auto &req, auto &res) {
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
    res.set_header("Access-Control-Allow-Headers", "Content-Type");
  });

  // Prediction Endpoint
  svr.Post("/predict", [&](const httplib::Request &req,
                           httplib::Response &res) {
    try {
      std::stringstream ss(req.body);
      std::string item;
      std::vector<float> sensors;

      // Expecting 17 comma-separated floats
      while (std::getline(ss, item, ',')) {
        sensors.push_back(std::stof(item));
      }

      if (sensors.size() != 17) {
        res.status = 400;
        res.set_content("{\"error\": \"Expected 17 sensors\"}",
                        "application/json");
        return;
      }

      std::cout << "DEBUG: Received sensor data, processing..." << std::endl;
      auto result = engine.predict(sensors);
      float prob = 1.0f / (1.0f + std::exp(-result[0]));
      
      std::string status = (prob > 0.5f) ? "DANGER" : "NOMINAL";

      std::cout << "DEBUG: Prediction: " << prob << " (" << status << ")" << std::endl;

      std::string json = "{\"probability\": " + std::to_string(prob) +
                         ", \"status\": \"" + status + "\"}";

      res.set_content(json, "application/json");
    } catch (...) {
      res.status = 500;
      res.set_content("{\"error\": \"Inference failed\"}", "application/json");
    }
  });

  // Handle Pre-flight OPTIONS requests (Standard Web Browser security)
  svr.Options(R"(/.*)", [](const httplib::Request &, httplib::Response &res) {
    res.status = 200;
  });

  // Serve web dashboard from ./web directory
  if (!svr.set_mount_point("/", "./web")) {
    std::cerr << "WARNING: ./web directory not found. Dashboard disabled." << std::endl;
  }

  std::cout << "NASA Sentinel Edge AI Active on port 8080..." << std::endl;
  std::cout << "Dashboard: http://localhost:8080" << std::endl;
  svr.listen("0.0.0.0", 8080);

  return 0;
}
