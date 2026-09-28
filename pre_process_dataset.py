import pandas as pd
import re
import os

# Map raw log files to labels (1: Anomaly, 0: Legit) for supervised learning
log_files = [
    {"path": "log_dataset_raw/anomaly_external_logs.log", "label": 1},
    {"path": "log_dataset_raw/legit_external_logs.log", "label": 0},
    {"path": "log_dataset_raw/legit_internal_logs.log", "label": 0}
]

def extract_pfsense_features(file_path, label):
    processed_data = []
    
    # Regex to isolate the CSV payload from syslog headers
    log_pattern = re.compile(r'filterlog(?:\[\d+\])?: (.*)')
    
    if not os.path.exists(file_path):
        print(f"Warning: File not found - {file_path}")
        return processed_data

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = log_pattern.search(line)
            if match:
                csv_data = match.group(1).split(',')
                
                # Restrict to IPv4 traffic to maintain feature consistency
                if len(csv_data) >= 20 and csv_data[8] == '4':
                    try:
                        # Extract network behavior features
                        # Removed interfaces, IPs, and IP flags to prevent model bias/overfitting
                        entry = {
                            'action': csv_data[6],
                            'direction': csv_data[7],
                            'ttl': int(csv_data[11]) if csv_data[11] else 0,
                            'protocol': csv_data[16],
                            'length': int(csv_data[17]),
                            'label': label
                        }
                        
                        # Port and payload extraction for TCP/UDP
                        if entry['protocol'] in ['tcp', 'udp'] and len(csv_data) >= 23:
                            entry['src_port'] = int(csv_data[20])
                            entry['dst_port'] = int(csv_data[21])
                            entry['data_length'] = int(csv_data[22]) if csv_data[22] else 0
                        else:
                            entry['src_port'] = 0
                            entry['dst_port'] = 0
                            entry['data_length'] = 0
                            
                        # Specific TCP flags extraction for scan/flood detection
                        if entry['protocol'] == 'tcp' and len(csv_data) >= 24:
                            entry['tcp_flags'] = csv_data[23]
                        else:
                            entry['tcp_flags'] = 'none'
                            
                        processed_data.append(entry)
                    except (ValueError, IndexError):
                        # Skip malformed logs to ensure dataset integrity
                        continue
                        
    return processed_data

# Main execution flow
all_logs = []
for item in log_files:
    print(f"Processing: {item['path']}...")
    all_logs.extend(extract_pfsense_features(item['path'], item['label']))

# Convert to DataFrame for easier manipulation with scikit-learn later
df_logs = pd.DataFrame(all_logs)

output_filename = 'full_logs_dataset.csv'
df_logs.to_csv(output_filename, index=False)

print(f"\nDataset saved to: {output_filename}")
print(f"Total records: {len(df_logs)}")
print("\nClass distribution (0 = Legit, 1 = Anomaly):")
print(df_logs['label'].value_counts())