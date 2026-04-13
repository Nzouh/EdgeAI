#ifndef ENGINE_H
#define ENGINE_H

#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <cmath>

struct Layer {
    int rows, cols, zp;
    float scale;
    unsigned char* weights;
    float* bias;

    Layer() : weights(nullptr), bias(nullptr) {}

    ~Layer() {
        delete[] weights;
        delete[] bias;
    }
};

class InferenceEngine {
private:
    std::vector<Layer*> layers;
    float* sensor_min;
    float* sensor_max;
    int num_sensors;

public:
    InferenceEngine() : sensor_min(nullptr), sensor_max(nullptr), num_sensors(0) {}

    ~InferenceEngine() {
        for (Layer* l : layers) delete l;
        delete[] sensor_min;
        delete[] sensor_max;
    }

    bool load(const std::string& filename) {
        std::ifstream file(filename, std::ios::binary);
        if (!file) return false;

        int num_layers;
        file.read((char*)&num_layers, sizeof(int));
        file.read((char*)&num_sensors, sizeof(int));

        sensor_min = new float[num_sensors];
        sensor_max = new float[num_sensors];
        file.read((char*)sensor_min, num_sensors * sizeof(float));
        file.read((char*)sensor_max, num_sensors * sizeof(float));

        for (int i = 0; i < num_layers; i++) {
            Layer* l = new Layer();
            file.read((char*)&l->rows, sizeof(int));
            file.read((char*)&l->cols, sizeof(int));
            file.read((char*)&l->scale, sizeof(float));
            file.read((char*)&l->zp, sizeof(int));

            l->weights = new unsigned char[l->rows * l->cols];
            file.read((char*)l->weights, l->rows * l->cols);

            l->bias = new float[l->rows];
            file.read((char*)l->bias, sizeof(float) * l->rows);

            layers.push_back(l);
        }
        return true;
    }

    std::vector<float> predict(const std::vector<float>& raw_input) {
        if (raw_input.size() != (size_t)num_sensors) return { -100.0f }; // Error signal

        std::vector<float> current(num_sensors);
        for (int i = 0; i < num_sensors; i++) {
            current[i] = (raw_input[i] - sensor_min[i]) / (sensor_max[i] - sensor_min[i] + 1e-9f);
        }

        for (size_t l_idx = 0; l_idx < layers.size(); l_idx++) {
            Layer* l = layers[l_idx];
            std::vector<float> next(l->rows, 0.0f);

            for (int i = 0; i < l->rows; i++) {
                float sum = l->bias[i];
                for (int j = 0; j < l->cols; j++) {
                    float w = (l->weights[i * l->cols + j] - l->zp) * l->scale;
                    sum += current[j] * w;
                }
                if (l_idx < layers.size() - 1) sum = std::max(0.0f, sum);
                next[i] = sum;
            }
            current = next;
        }
        return current;
    }
};

#endif
