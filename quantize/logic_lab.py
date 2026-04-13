import torch
import torch.nn as nn
import struct

# XOR Data
X = torch.tensor([[0,0], [0,1], [1,0], [1,1]], dtype=torch.float32)
Y = torch.tensor([[0], [1], [1], [0]], dtype=torch.float32)

# Multi-Layer Architecture
model = nn.Sequential(
    nn.Linear(2, 8), # Layer 0: Hidden (Increased to 8)
    nn.ReLU(),
    nn.Linear(8, 1)  # Layer 2: Output
)

# Use Adam for faster convergence on XOR
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = nn.MSELoss()

print("Training Multi-Layer XOR model...")
for epoch in range(3000):
    optimizer.zero_grad()
    out = model(X)
    loss = criterion(out, Y)
    loss.backward()
    optimizer.step()
    if epoch % 500 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

# Export Logic
filename = "logic_model.bin"
with open(filename, "wb") as f:
    # 1. Total actual linear layers (2)
    f.write(struct.pack("i", 2))
    
    # 2. Iterate through layers
    for layer in model:
        if isinstance(layer, nn.Linear):
            weight = layer.weight.data
            bias = layer.bias.data
            
            # Per-layer quantization params
            scale = (weight.max() - weight.min()) / 255
            zp = torch.round(-weight.min() / scale).to(torch.int32)
            q_weight = torch.clamp(torch.round(weight / scale) + zp, 0, 255).to(torch.uint8)
            
            rows, cols = q_weight.shape
            
            # Save: Rows, Cols, Scale, ZP, QuantizedWeights, FloatBias
            f.write(struct.pack("iifi", rows, cols, scale.item(), zp.item()))
            f.write(q_weight.numpy().tobytes())
            f.write(bias.numpy().tobytes())

print(f"Multi-Layer XOR Model Exported: {filename}")