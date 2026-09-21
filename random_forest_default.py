import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Load the dataset
firewall_data = pd.read_csv("database.csv")

target_column = "Action"

# Separate features and target
x_features = firewall_data.drop(columns=[target_column])
y_target = firewall_data[target_column]

# Convert categorical variables into dummy/indicator variables
x_features_encoded = pd.get_dummies(x_features)

# Encode target labels with value between 0 and n_classes-1
label_encoder = LabelEncoder()
y_target_encoded = label_encoder.fit_transform(y_target)

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    x_features_encoded, 
    y_target_encoded, 
    test_size=0.3, 
    random_state=28
)

# Initialize and train the Random Forest model
random_forest_model = RandomForestClassifier(class_weight="balanced", random_state=28)
random_forest_model.fit(x_train, y_train)

# Make predictions on the test set
predictions = random_forest_model.predict(x_test)

# Calculate overall weighted metrics
model_accuracy = accuracy_score(y_test, predictions)
model_precision = precision_score(y_test, predictions, average="weighted")
model_recall = recall_score(y_test, predictions, average="weighted")
model_f1 = f1_score(y_test, predictions, average="weighted")

# Print overall metrics
print("--- Overall Model Performance ---")
print(f"Accuracy:  {model_accuracy:.4f}")
print(f"Precision: {model_precision:.4f}")
print(f"Recall:    {model_recall:.4f}")
print(f"F1-Score:  {model_f1:.4f}")
print("---------------------------------\n")

# Print detailed metrics PER CLASS
print("--- Performance Metrics Per Class ---")
class_report = classification_report(
    y_test, 
    predictions,
    digits=6, 
    target_names=label_encoder.classes_
)
print(class_report)
print("-------------------------------------\n")

# Generate and plot the Confusion Matrix
model_confusion_matrix = confusion_matrix(y_test, predictions)

matrix_display = ConfusionMatrixDisplay(
    confusion_matrix=model_confusion_matrix, 
    display_labels=label_encoder.classes_
)

matrix_display.plot(cmap="Blues", values_format="d")
plt.title("Confusion Matrix - Firewall Actions")
plt.show()