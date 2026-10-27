import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)


def load_and_preprocess_data(file_path, feature_names, target_name):
    dataframe = pd.read_csv(file_path)

    raw_features = dataframe[feature_names]
    labels = dataframe[target_name]

    # One-hot encoding is used instead of label encoding to avoid implying an arbitrary numerical order to categorical network attributes like protocols or flags.
    encoded_features = pd.get_dummies(raw_features)

    return encoded_features, labels


def split_dataset(features, labels):
    # Stratification is used to preserve the exact ratio of anomalies to normal traffic in both sets, preventing biased evaluation on imbalanced network logs.
    training_features, testing_features, training_labels, testing_labels = (
        train_test_split(
            features,
            labels,
            test_size=0.30,
            shuffle=True,
            random_state=28,
            stratify=labels,
        )
    )
    return training_features, testing_features, training_labels, testing_labels


def create_random_forest_model(hyperparameters):
    # Class weight is set to 'balanced' to penalize mistakes on the minority anomaly class more heavily, compensating for dataset imbalance without synthetic oversampling.
    model = RandomForestClassifier(
        n_estimators=hyperparameters["n_estimators"],
        max_depth=hyperparameters["max_depth"],
        min_samples_split=hyperparameters["min_samples_split"],
        min_samples_leaf=hyperparameters["min_samples_leaf"],
        max_features=hyperparameters["max_features"],
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    return model


def evaluate_hyperparameters_with_optuna(
    trial, training_features, training_labels, cross_validation_splitter
):
    candidate_hyperparameters = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth": trial.suggest_int("max_depth", 5, 50),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 20),
        "max_features": trial.suggest_categorical(
            "max_features", ["sqrt", "log2", None]
        ),
    }

    model = create_random_forest_model(candidate_hyperparameters)

    # F1-macro is chosen over accuracy because accuracy is misleading on imbalanced datasets where normal traffic vastly outnumbers anomalies.
    fold_scores = cross_val_score(
        estimator=model,
        X=training_features,
        y=training_labels,
        cv=cross_validation_splitter,
        scoring="f1_macro",
        n_jobs=-1,
    )

    mean_f1_score = np.mean(fold_scores)
    return mean_f1_score


def find_best_hyperparameters(
    training_features, training_labels, cross_validation_splitter, total_trials
):
    study = optuna.create_study(direction="maximize")

    def objective_function(trial):
        return evaluate_hyperparameters_with_optuna(
            trial,
            training_features,
            training_labels,
            cross_validation_splitter,
        )

    study.optimize(objective_function, n_trials=total_trials)

    return study.best_params


def evaluate_trained_model(model, testing_features, testing_labels):
    predictions = model.predict(testing_features)

    accuracy = accuracy_score(testing_labels, predictions)
    precision = precision_score(testing_labels, predictions, zero_division=0)
    sensitivity = recall_score(testing_labels, predictions, zero_division=0)
    detailed_report = classification_report(
        testing_labels, predictions, zero_division=0
    )

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Sensitivity (Recall): {sensitivity:.4f}\n")
    print("Classification Report:")
    print(detailed_report)


def save_model_to_disk(model, file_path):
    # Joblib is used instead of standard pickle because it serializes internal NumPy arrays in tree structures significantly faster and with less memory overhead.
    joblib.dump(model, file_path)
    print(f"Model saved to {file_path}")


def main():
    dataset_filename = "full_logs_dataset.csv"
    model_export_filename = "trained_random_forest_model.joblib"
    target_column = "is_anomaly"
    feature_columns = [
        "action",
        "direction",
        "ttl",
        "protocol",
        "length",
        "dst_port",
        "data_length",
        "tcp_flags",
    ]

    encoded_features, target_labels = load_and_preprocess_data(
        dataset_filename, feature_columns, target_column
    )

    training_features, testing_features, training_labels, testing_labels = (
        split_dataset(encoded_features, target_labels)
    )

    # Stratified K-Fold ensures no validation fold ends up without anomaly samples during cross-validation.
    cross_validation_splitter = StratifiedKFold(
        n_splits=5, shuffle=True, random_state=28
    )

    best_hyperparameters = find_best_hyperparameters(
        training_features,
        training_labels,
        cross_validation_splitter,
        total_trials=30,
    )
    print(f"Optimal Hyperparameters: {best_hyperparameters}\n")

    final_classifier = create_random_forest_model(best_hyperparameters)

    validation_scores = cross_val_score(
        estimator=final_classifier,
        X=training_features,
        y=training_labels,
        cv=cross_validation_splitter,
        scoring="f1_macro",
        n_jobs=-1,
    )
    mean_validation_score = np.mean(validation_scores)

    print(f"K-Fold CV F1-Macro Scores: {validation_scores}")
    print(f"K-Fold CV Mean F1-Macro: {mean_validation_score:.4f}\n")

    final_classifier.fit(training_features, training_labels)

    evaluate_trained_model(final_classifier, testing_features, testing_labels)

    save_model_to_disk(final_classifier, model_export_filename)


if __name__ == "__main__":
    main()