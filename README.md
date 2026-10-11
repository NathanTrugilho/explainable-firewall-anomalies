# Explainable-firewall-anomalies

A Computer Engineering cybersecurity final project for detecting firewall traffic anomalies using **Random Forest**, with a locally executed **Large Language Model (LLM)** providing explainable AI explanations for the model’s classification decisions.

## Overview

The project creates a controlled virtual network environment with **pfSense**, legitimate client traffic, and simulated attacks from **Kali Linux**. Firewall logs are collected, processed, labeled, and used to train a Random Forest classifier.

A local fine-tuned LLM provides human-readable explanations for detected anomalies.

## Features

- Virtualized firewall lab using pfSense
- Synthetic benign and malicious traffic generation
- Attack simulation with Nmap, Hping3, and security tools
- Firewall log collection and preprocessing
- Anomaly classification with Random Forest
- Hyperparameter optimization and cross-validation
- Validation with external datasets
- Local LLM fine-tuning for log interpretation
- Simple application for log upload and anomaly reports

## Pipeline

```text
Network Traffic
      ↓
pfSense Firewall Logs
      ↓
Preprocessing and Feature Engineering
      ↓
Random Forest Classification
      ↓
Anomaly Result + Feature Analysis
      ↓
Local LLM Explanation
      ↓
User Interface Report
```

## Technologies

- Python
- pandas
- scikit-learn
- pfSense
- Kali Linux
- Random Forest
- Local LLMs (Llama, Mistral, or similar)
- Virtualization platform
- Web or desktop interface

## Evaluation Metrics

The model is evaluated using:

- Accuracy
- Precision
- Recall
- F1-score

## Project Goal

Build a privacy-focused and locally deployable solution that helps users identify suspicious firewall activity and understand why a traffic pattern was classified as anomalous.
