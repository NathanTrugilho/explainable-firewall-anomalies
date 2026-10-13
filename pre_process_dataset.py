import os
import re

import pandas as pd

log_files = [
    {"path": "log_dataset_raw/anomaly_external_logs.log", "label": 1},
    {"path": "log_dataset_raw/legit_external_logs.log", "label": 0},
    {"path": "log_dataset_raw/legit_internal_logs.log", "label": 0},
]


def extract_pfsense_features(file_path, label):
    processed_data = []

    log_pattern = re.compile(r"filterlog(?:\[\d+\])?: (.*)")

    if not os.path.exists(file_path):
        print(f"Warning: File not found - {file_path}")
        return processed_data

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = log_pattern.search(line)

            if not match:
                continue

            csv_data = match.group(1).split(",")

            if len(csv_data) < 20 or csv_data[8] != "4":
                continue

            try:
                entry = {
                    "action": csv_data[6],
                    "direction": csv_data[7],
                    "ttl": int(csv_data[11]) if csv_data[11] else 0,
                    "protocol": csv_data[16],
                    "length": int(csv_data[17]),
                }

                if entry["protocol"] in ["tcp", "udp"] and len(csv_data) >= 23:
                    entry["dst_port"] = int(csv_data[21])
                    entry["data_length"] = int(csv_data[22]) if csv_data[22] else 0
                else:
                    entry["dst_port"] = 0
                    entry["data_length"] = 0

                if entry["protocol"] == "tcp" and len(csv_data) >= 24:
                    entry["tcp_flags"] = csv_data[23]
                else:
                    entry["tcp_flags"] = "none"

                entry["anomaly"] = label
                processed_data.append(entry)

            except (ValueError, IndexError):
                continue

    return processed_data


all_logs = []

for item in log_files:
    print(f"Processing: {item['path']}...")
    all_logs.extend(
        extract_pfsense_features(item["path"], item["label"])
    )

columns = [
    "action",
    "direction",
    "ttl",
    "protocol",
    "length",
    "dst_port",
    "data_length",
    "tcp_flags",
    "anomaly",
]

df_logs = pd.DataFrame(all_logs, columns=columns)

output_filename = "full_logs_dataset.csv"
df_logs.to_csv(output_filename, index=False)

print(f"\nDataset saved to: {output_filename}")
print(f"Total records: {len(df_logs)}")

print("\nClass distribution (0 = Legit, 1 = Anomaly):")
print(df_logs["anomaly"].value_counts().sort_index())

print("\nDataset columns:")
print(df_logs.columns.tolist())