import pandas as pd
import kagglehub
import os

# 1. Download
print("Acquiring NASA Test Data and RUL Targets...")
path = kagglehub.dataset_download("palbha/cmapss-jet-engine-simulated-data")

# 2. Setup Paths
test_path = None
rul_path = None
for root, dirs, files in os.walk(path):
    if "test_FD001.txt" in files: test_path = os.path.join(root, "test_FD001.txt")
    if "RUL_FD001.txt" in files: rul_path = os.path.join(root, "RUL_FD001.txt")

# 3. Load & Process Ground Truth
cols = ['id', 'cycle', 'setting1', 'setting2', 'setting3'] + [f's{i}' for i in range(1, 22)]
test_df = pd.read_csv(test_path, sep=r'\s+', header=None, names=cols)

# RUL_FD001.txt gives the RUL at the LAST cycle recorded in test_FD001.txt
rul_values = pd.read_csv(rul_path, sep=r'\s+', header=None, names=['true_rul_at_end'])
rul_values['id'] = range(1, len(rul_values) + 1)

# Find last cycle for each engine in test
max_cycles = test_df.groupby('id')['cycle'].max().reset_index()
max_cycles = max_cycles.merge(rul_values, on='id')

# Failure Cycle = Current Max Cycle + True RUL remaining
max_cycles['fail_cycle'] = max_cycles['cycle'] + max_cycles['true_rul_at_end']

# 4. Apply Labels to every row in test set
test_df = test_df.merge(max_cycles[['id', 'fail_cycle']], on='id')
test_df['current_rul'] = test_df['fail_cycle'] - test_df['cycle']
test_df['label'] = (test_df['current_rul'] <= 30).astype(int)

# 5. Extract ONLY the 17 sensors and label
# Get same valid sensors used in training
train_df = pd.read_csv("nasa_train.csv")
sensor_cols = [f's{i}' for i in range(1, 22)]
stds = train_df[sensor_cols].std()
valid_cols = stds[stds > 0].index.tolist()

final_test = test_df[valid_cols + ['label']]
final_test.to_csv("nasa_test_labeled.csv", index=False)
print(f"SUCCESS: nasa_test_labeled.csv created | {len(final_test)} rows.")
