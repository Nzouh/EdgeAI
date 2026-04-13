import pandas as pd
import kagglehub
import os
import shutil

# 1. Download
print("Downloading from Kaggle...")
path = kagglehub.dataset_download("palbha/cmapss-jet-engine-simulated-data")

# 2. Find file
# Dataset has subfolders. Search for train_FD001.txt
target_file = "train_FD001.txt"
found_path = None
for root, dirs, files in os.walk(path):
    if target_file in files:
        found_path = os.path.join(root, target_file)
        break

if found_path:
    print(f"Found: {found_path}")
    cols = ['id', 'cycle', 'setting1', 'setting2', 'setting3'] + [f's{i}' for i in range(1, 22)]
    df = pd.read_csv(found_path, sep=r'\s+', header=None, names=cols)
    df.to_csv("nasa_train.csv", index=False)
    print(f"SUCCESS: nasa_train.csv created. Rows: {len(df)}")
else:
    print("FAILED: train_FD001.txt not found in Kaggle download.")


test_file = "test_FD001.txt"
path_found = None
