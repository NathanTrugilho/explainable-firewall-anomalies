import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

dataset_filename = "full_logs_dataset.csv"
dataframe = pd.read_csv(dataset_filename)

target_column = "is_anomaly"
feature_columns = [
    "action",
    "direction",
    "ttl",
    "protocol",
    "length",
    "src_port",
    "dst_port",
    "data_length",
    "tcp_flags",
]

input_features = dataframe[feature_columns]
target_labels = dataframe[target_column]

# Convert categorical string columns to numeric representation
encoded_features = pd.get_dummies(input_features)

training_features, testing_features, training_labels, testing_labels = (
    train_test_split(
        encoded_features,
        target_labels,
        test_size=0.30,
        shuffle=True,
        random_state=42,
    )
)

classifier = RandomForestClassifier(random_state=42)
classifier.fit(training_features, training_labels)

predictions = classifier.predict(testing_features)

accuracy = accuracy_score(testing_labels, predictions)
precision = precision_score(testing_labels, predictions, zero_division=0)
sensitivity = recall_score(testing_labels, predictions, zero_division=0)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Sensitivity (Recall): {sensitivity:.4f}\n")
print("Classification Report:")
print(classification_report(testing_labels, predictions, zero_division=0))