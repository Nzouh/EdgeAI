import torch
from torch.ao.quantization.fx._decomposed import dequantize_per_tensor
import torch

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






if __name__ == "__main__":
    #Create a random weight matrix (to represent MLP)
    torch.manual_seed(42)
    weights = torch.randn(4, 4)
    print(f"Original Weights : {weights}")

    scale = get_symmetric_scale(weights)

    print(f"\nscale: {scale.item():.7f}")

    quantized_weight = quantize_symmetric(weights, scale)

    print(f"\nQuantized Weights: {quantized_weight}")

    dequantized_weight = dequantize_symmetric(quantized_weight, scale)
    print(f"Dequantized Weights: {dequantized_weight}")


    #Measuring Quantization Error
    error = torch.mean((weights - dequantized_weight)**2)
    print(f"MSE: {error.item():.8f}")



