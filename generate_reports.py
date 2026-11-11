import os
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
     ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


def create_output_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def load_and_preprocess_data(file_path, feature_names, target_name):
    dataframe = pd.read_csv(file_path)

    raw_features = dataframe[feature_names]
    labels = dataframe[target_name]

    # One-hot encoding matches the exact feature transformation applied during training.
    encoded_features = pd.get_dummies(raw_features)

    return dataframe, encoded_features, labels


def split_dataset(features, labels):
    # Identical random_state and stratification ensure evaluation is strictly on unseen test data.
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


def align_features_with_model(model, features):
    # Reindexing prevents dimension mismatch if the test split lacks rare categorical values.
    if hasattr(model, "feature_names_in_"):
        return features.reindex(columns=model.feature_names_in_, fill_value=0)
    return features


def export_text_metrics_report(
    model, testing_features, testing_labels, output_dir
):
    predictions = model.predict(testing_features)
    probabilities = model.predict_proba(testing_features)[:, 1]

    accuracy = accuracy_score(testing_labels, predictions)
    precision = precision_score(testing_labels, predictions, zero_division=0)
    recall = recall_score(testing_labels, predictions, zero_division=0)
    f1_binary = f1_score(testing_labels, predictions, zero_division=0)
    f1_macro = f1_score(
        testing_labels, predictions, average="macro", zero_division=0
    )
    roc_auc = roc_auc_score(testing_labels, probabilities)
    pr_auc = average_precision_score(testing_labels, probabilities)
    # MCC provides a balanced metric even when class sizes differ radically.
    mcc = matthews_corrcoef(testing_labels, predictions)

    class_report = classification_report(
        testing_labels,
        predictions,
        target_names=["Legitimate (0)", "Anomaly (1)"],
        digits=6,
        zero_division=0,
    )

    report_content = (
        "==================================================\n"
        "       RANDOM FOREST PERFORMANCE REPORT           \n"
        "==================================================\n\n"
        f"Accuracy:                  {accuracy:.6f}\n"
        f"Precision (Anomaly):       {precision:.6f}\n"
        f"Recall / Sensitivity:      {recall:.6f}\n"
        f"F1-Score (Anomaly):        {f1_binary:.6f}\n"
        f"F1-Score (Macro):          {f1_macro:.6f}\n"
        f"ROC-AUC Score:             {roc_auc:.6f}\n"
        f"PR-AUC (Avg Precision):    {pr_auc:.6f}\n"
        f"Matthews Corr. Coef (MCC): {mcc:.6f}\n\n"
        "--------------------------------------------------\n"
        "           DETAILED CLASSIFICATION REPORT         \n"
        "--------------------------------------------------\n"
        f"{class_report}\n"
    )

    print(report_content)

    report_path = os.path.join(output_dir, "performance_metrics.txt")
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report_content)


def plot_confusion_matrices(model, testing_features, testing_labels, output_dir):
    predictions = model.predict(testing_features)
    class_names = ["Legitimate", "Anomaly"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Absolute counts show the exact volume of False Positives and False Negatives.
    cm_absolute = confusion_matrix(testing_labels, predictions)
    disp_abs = ConfusionMatrixDisplay(
        confusion_matrix=cm_absolute, display_labels=class_names
    )
    disp_abs.plot(ax=axes[0], cmap="Blues", values_format="d", colorbar=False)
    axes[0].set_title("Confusion Matrix (Absolute Counts)")

    # Normalized matrix reveals the proportional error rate per class regardless of imbalance.
    cm_normalized = confusion_matrix(
        testing_labels, predictions, normalize="true"
    )
    disp_norm = ConfusionMatrixDisplay(
        confusion_matrix=cm_normalized, display_labels=class_names
    )
    disp_norm.plot(
        ax=axes[1], cmap="Blues", values_format=".4f", colorbar=False
    )
    axes[1].set_title("Confusion Matrix (Normalized by True Class)")

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "confusion_matrices.png"), dpi=300
    )
    plt.close()


def plot_roc_and_pr_curves(model, testing_features, testing_labels, output_dir):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ROC curve evaluates the trade-off between True Positive Rate and False Positive Rate.
    RocCurveDisplay.from_estimator(
        model,
        testing_features,
        testing_labels,
        ax=axes[0],
        name="Random Forest",
        color="darkorange",
    )
    axes[0].plot([0, 1], [0, 1], color="navy", linestyle="--", label="Random")
    axes[0].set_title("ROC Curve (Receiver Operating Characteristic)")
    axes[0].legend(loc="lower right")
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Precision-Recall curve is more informative than ROC on highly skewed anomaly datasets.
    PrecisionRecallDisplay.from_estimator(
        model,
        testing_features,
        testing_labels,
        ax=axes[1],
        name="Random Forest",
        color="purple",
    )
    axes[1].set_title("Precision-Recall Curve")
    axes[1].legend(loc="lower left")
    axes[1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "roc_and_pr_curves.png"), dpi=300
    )
    plt.close()


def plot_feature_importance(model, feature_names, output_dir, top_n=15):
    # Feature importance ranking supports explainability for the downstream LLM layer.
    importances = model.feature_importances_
    std_devs = np.std(
        [tree.feature_importances_ for tree in model.estimators_], axis=0
    )

    indices = np.argsort(importances)[::-1][:top_n]
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]
    top_std = std_devs[indices]

    plt.figure(figsize=(10, 6))
    plt.barh(
        range(len(top_features)),
        top_importances[::-1],
        xerr=top_std[::-1],
        align="center",
        color="teal",
        alpha=0.8,
        ecolor="black",
        capsize=3,
    )
    plt.yticks(range(len(top_features)), top_features[::-1])
    plt.xlabel("Mean Decrease in Impurity (Gini Importance)")
    plt.title(f"Top {len(top_features)} Feature Importances (Random Forest)")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "feature_importance.png"), dpi=300
    )
    plt.close()


def plot_correlation_matrix(encoded_features, labels, output_dir, top_n=15):
    # Filtering top correlated features keeps the heatmap readable when one-hot encoding creates many columns.
    full_df = encoded_features.copy()
    full_df["is_anomaly"] = labels

    correlations_with_target = (
        full_df.corr()["is_anomaly"].abs().sort_values(ascending=False)
    )
    top_columns = correlations_with_target.head(top_n + 1).index

    corr_matrix = full_df[top_columns].corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    cax = ax.matshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
    fig.colorbar(cax)

    ticks = np.arange(len(top_columns))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(top_columns, rotation=45, ha="left", fontsize=9)
    ax.set_yticklabels(top_columns, fontsize=9)

    for i in range(len(top_columns)):
        for j in range(len(top_columns)):
            value = corr_matrix.iloc[i, j]
            text_color = "white" if abs(value) > 0.5 else "black"
            ax.text(
                j,
                i,
                f"{value:.2f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=8,
            )

    plt.title(
        "Pearson Correlation Matrix (Top Features vs Target)", pad=20
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "correlation_matrix.png"), dpi=300
    )
    plt.close()


def main():
    dataset_filename = "full_logs_dataset.csv"
    model_filename = "trained_random_forest_model.joblib"
    output_directory = "model_reports"
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

    create_output_directory(output_directory)

    print("Loading dataset and trained model...")
    raw_df, encoded_features, target_labels = load_and_preprocess_data(
        dataset_filename, feature_columns, target_column
    )
    model = joblib.load(model_filename)

    _, testing_features, _, testing_labels = split_dataset(
        encoded_features, target_labels
    )
    testing_features = align_features_with_model(model, testing_features)

    print("Generating text performance metrics...")
    export_text_metrics_report(
        model, testing_features, testing_labels, output_directory
    )

    print("Generating Confusion Matrices...")
    plot_confusion_matrices(
        model, testing_features, testing_labels, output_directory
    )

    print("Generating ROC and Precision-Recall curves...")
    plot_roc_and_pr_curves(
        model, testing_features, testing_labels, output_directory
    )

    print("Generating Feature Importance plot...")
    plot_feature_importance(
        model,
        testing_features.columns.tolist(),
        output_directory,
        top_n=15,
    )

    print("Generating Correlation Matrix...")
    plot_correlation_matrix(
        encoded_features, target_labels, output_directory, top_n=15
    )

    print(f"\nAll reports successfully saved in '{output_directory}/'!")


if __name__ == "__main__":
    main()