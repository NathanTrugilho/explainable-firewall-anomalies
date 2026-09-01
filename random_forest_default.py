import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

firewall_data = pd.read_csv("firewall_logs.csv")

target_column = "Action"

x_features = firewall_data.drop(columns=[target_column])
y_target = firewall_data[target_column]

x_features_encoded = pd.get_dummies(x_features)

label_encoder = LabelEncoder()
y_target_encoded = label_encoder.fit_transform(y_target)

x_train, x_test, y_train, y_test = train_test_split(
    x_features_encoded, 
    y_target_encoded, 
    test_size=0.3, 
    random_state=42
)

random_forest_model = RandomForestClassifier()

random_forest_model.fit(x_train, y_train)

predictions = random_forest_model.predict(x_test)

model_accuracy = accuracy_score(y_test, predictions)

print(model_accuracy)