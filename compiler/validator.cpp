#include "engine.h"
#include <sstream>

int main() {
  InferenceEngine engine;
  engine.load("sentinel_model.bin");

  std::ifstream file("nasa_test_labeled.csv");
  std::string line, word;
  int total = 0, correct = 0;
  std::getline(file, line); // Skip header
  while (std::getline(file, line)) {
    std::stringstream ss(line);
    std::vector<float> row;
    float label;
    // 1. Parse CSV (17 sensors + 1 label)
    while (std::getline(ss, word, ',')) {
      row.push_back(std::stof(word));
    }

    label = row.back();
    row.pop_back();
    // 2. Predict
    auto res = engine.predict(row);
    float prob = 1.0f / (1.0f + std::exp(-res[0]));
    int pred = (prob > 0.5f) ? 1 : 0;
    if (pred == (int)label)
      correct++;
    total++;
  }
  std::cout << "Accuracy: " << (float)correct / total * 100 << "%" << std::endl;
  return 0;
}
