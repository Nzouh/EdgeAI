import torch
from torch.ao.quantization.fx._decomposed import dequantize_per_tensor
import torch
import struct
import numpy as np

def export_model(weights, scale, zero_point, filename="model.bin"):
    rows, cols = weights.shape
    with open(filename, "wb") as f:
        # 'i' = int32, 'f' = float32, B=uint8
        f.write(struct.pack("iifi", rows, cols, scale, zero_point))
        f.write(weights.numpy().tobytes())
        print(f"Exported to {filename}")

def get_symmetric_scale(x):

    """
    Ex: If weights range from -2 to 2, scale is 2/127 = 0.0157
    """

    max_val = torch.max(torch.abs(x))
    scale = max_val / 127
    return scale

def quantize_symmetric(x, scale):
    """
    Float32 -> Int8
    """

    quantized = torch.round(x / scale)

    quantized = torch.clamp(quantized, -128, 127)
    return quantized.to(torch.int8)

def dequantize_symmetric(x, scale):
    """
    Int8 -> Float32
    """

    return x.to(torch.float32) * scale

def get_asymmetric_params(x):
    #Used for ReLU-like functions
    #Data might be skewed, so normal quantization changes data too much
    #this method "shifts" the range from 0 to 255 (min and max)

    min_val = x.min()
    max_val = x.max()

    scale = (max_val - min_val) / 255

    zero_point = torch.round(-min_val / scale)
    zero_point = torch.clamp(zero_point, 0, 255).to(torch.int32)

    return scale, zero_point


def quantize_asymmetric(x, scale, zero_point):
    """
    Float32 -> Int8
    """

    quantized = torch.round(x / scale) + zero_point
    return quantized.clamp(0, 255).to(torch.uint8)

def dequantize_asymmetric(quantized, scale, zero_point):
    return (quantized.to(torch.float32) - zero_point) * scale





if __name__ == "__main__":
    #Create a random weight matrix (to represent MLP)
    torch.manual_seed(42)
    weights = torch.randn(4, 4)
    print(f"Original Weights : {weights}")

    s_scale = get_symmetric_scale(weights)

    print(f"\nscale: {s_scale.item():.7f}")

    quantized_weight = quantize_symmetric(weights, s_scale)

    print(f"\nQuantized Weights: {quantized_weight}")

    dequantized_weight = dequantize_symmetric(quantized_weight, s_scale)
    print(f"Dequantized Weights: {dequantized_weight}")


    #Measuring Quantization Error
    error = torch.mean((weights - dequantized_weight)**2)
    print(f"MSE: {error.item():.8f}")

    export_model(quantized_weight, s_scale, 0,"symmetric_model.bin")

    asymmetric_weights = torch.randn(4, 4).relu()
    print(f"Original Weights : {asymmetric_weights}")


    a_scale, zero_point = get_asymmetric_params(asymmetric_weights)
    print(f"\nscale: {a_scale.item():.7f}")
    print(f"\nzero_point: {zero_point.item():.7f}")
    quantized_asymmetric = quantize_asymmetric(asymmetric_weights, a_scale, zero_point)
    print(f"\nQuantized Weights: {quantized_asymmetric}")
    dequantized_asymmetric = dequantize_asymmetric(quantized_asymmetric, a_scale, zero_point)
    print(f"Dequantized Weights: {dequantized_asymmetric}")

    error  = torch.mean((asymmetric_weights - dequantized_asymmetric) ** 2)
    print(f"MSE: {error.item():.8f}")

    export_model(quantized_asymmetric, a_scale, zero_point, "asymmetric_model.bin")
    






