import pandas as pd
import numpy as np 
import torch
import torch.nn as nn
import struct
import lab










# Load data

df = pd.read_csv("nasa_train.csv")

max_cycles = df.groupby('id')['cycle'].max().reset_index()
max_cycles.columns = ['id', 'max_cycle']

df = df.merge(max_cycles, on="id")

df['RUL'] = df['max_cycle'] - df['cycle']


# 30 cycles is danger zone

df['label'] = (df['RUL'] <= 30).astype(int)

#verify

print(df[['id', 'cycle', 'RUL', 'label']].tail(20))

sensor_cols = [f's{i}' for i in range(1, 22)]
X_raw = df[sensor_cols].values
# Find columns where values change
stds = X_raw.std(axis=0)
valid_idx = np.where(stds > 0)[0]
X_filtered = X_raw[:, valid_idx]
print(f"Kept {len(valid_idx)} sensors.")

# 1. Targets
Y_raw = df['label'].values.reshape(-1,1)

X_min = X_filtered.min(axis=0)
X_max = X_filtered.max(axis=0)

X_norm = (X_filtered - X_min) / (X_max - X_min + 1e-9)

X_tensor = torch.tensor(X_norm, dtype=torch.float32)
model = nn.Sequential(
    nn.Linear(len(valid_idx),16),
    nn.ReLU(),
    nn.Linear(16, 8),
    nn.ReLU(),
    nn.Linear(8,1)
)


print(f"Data ready. Input size: {len(valid_idx)}")

Y_tensor = torch.tensor(Y_raw, dtype = torch.float32)

criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

print("Training Sentinel Brain")
for epoch in range(1001):
    optimizer.zero_grad()

    #Forward pass
    logits = model(X_tensor)
    loss = criterion(logits, Y_tensor)

    #Backward Pass
    loss.backward()
    optimizer.step()

    if epoch % 200 == 0:
        #Calculate the Accuracy every 200 epoch
        preds = (torch.sigmoid(logits) > 0.5).float()

        acc = (preds == Y_tensor).float().mean()

        print(f"Epoch {epoch} | Loss: {loss.item():.4f} | Acc: {acc.item():.4f}")
print("Training Complete")

filename = "sentinel_model.bin"
num_linear = sum(1 for m in model if isinstance(m, nn.Linear))

with open(filename, "wb") as f:
    # 1. Header (for c++)
    f.write(struct.pack("i", num_linear))
    f.write(struct.pack("i", len(valid_idx)))
    f.write(X_min.astype(np.float32).tobytes())
    f.write(X_max.astype(np.float32).tobytes())

    #Loops and Quantize
    for layer in model:
        if isinstance(layer, nn.Linear):

            scale, zero_point = lab.get_asymmetric_params(layer.weight.data)
            quantized_weight = lab.quantize_asymmetric(layer.weight.data, scale, zero_point)
            bias = layer.bias.data
            rows, cols = quantized_weight.shape

            f.write(struct.pack("iifi", rows, cols, float(scale), zero_point.item()))
            f.write(quantized_weight.numpy().tobytes())
            f.write(bias.numpy().tobytes())

            

            






