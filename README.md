<<<<<<< HEAD
# MediScan – Clinical Context Integration in Medical Imaging

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-FF6F00?style=flat&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?style=flat&logo=opencv&logoColor=white)](https://opencv.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An intelligent clinical decision-support web application that analyzes medical images (**Chest X-Ray**, **CT Scan**, **MRI**) together with structured patient clinical information (**symptoms**, **vitals**, **medical history**, **risk factors**) using **ResNet-50 Feature-Level Fusion** and **Explainable AI (Grad-CAM, LIME, SHAP)**.

---

## 🌟 Key Features

1. **Multi-Role RBAC**: 4 distinct roles (`ADMIN`, `DOCTOR`, `VIEWER`, `PATIENT`).
2. **Dual-Branch Feature-Level Fusion**:
   - **Image Branch**: 2048-dimensional feature embedding extracted via **ResNet-50** deep convolutional backbone.
   - **Clinical Branch**: 16-dimensional standardized vector encoding patient symptoms, vitals, age, smoking status, hypertension, and diabetes.
   - **Fusion Layer**: Concatenates image & clinical vectors into an MLP classifier with Softmax output.
3. **Explainable AI (XAI)**:
   - **Grad-CAM**: Generates visual activation heatmaps overlaid on medical scans with an interactive opacity slider.
   - **SHAP**: Visualizes clinical feature contributions (Symptoms, Age, Smoking history, Vitals).
   - **LIME**: Identifies local image segment contributions.
4. **Transparent Risk Stratification**: Rule-based framework classifying cases into `LOW`, `MEDIUM`, or `HIGH` risk based on prediction severity, confidence, and clinical risk factors.
5. **PDF Report Engine**: ReportLab PDF generator creating tamper-evident reports with embedded verification **QR Codes**.
6. **Patient Portal & Accessibility**:
   - Simplified **"In Plain English"** medical explanations.
   - **Web Speech API** audio reading (`🔊 Listen to Explanation`).
   - Visual medical timeline.
7. **PWA & Design System**: Progressive Web App with offline static caching, dark/light theme toggle, and keyboard shortcuts (`S`, `D`, `R`, `?`).
8. **Security & Audit Logging**: Password hashing via **Bcrypt**, session protection, row-level patient data isolation, and MySQL tamper-resistant audit logs.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- `pip` / virtual environment

### 2. Setup Virtual Environment & Install Dependencies
```bash
cd MediScan
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```
Open your browser and navigate to **`http://localhost:5000`**.

---

## 🔑 Demo Login Credentials

The application automatically seeds the database with out-of-the-box demo accounts:

| Role | Email | Password | Dashboard Features |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin@mediscan.org` | `Admin123!` | User & Hospital management, System Audit Logs, Model Metrics |
| **DOCTOR** | `doctor@mediscan.org` | `Doctor123!` | Patient directory, Scan upload, AI Fusion Studio, Report PDF generation |
| **PATIENT** | Patient-created account | Patient-chosen password | View own reports, Plain-English summary, Voice Speech, Timeline |

---

## 🧪 Running Automated Tests

Run the PyTest test suite:
```bash
pytest tests/
```

---

## 📁 Project Directory Layout

```
MediScan/
├── app.py                     # Main Flask Application Entry Point & DB Seeder
├── config.py                  # App & Database Configuration
├── requirements.txt           # Python Dependencies
│
├── backend/
│   ├── routes/                # REST API Controllers (auth, admin, doctor, patient, scans, ai, reports, analytics)
│   ├── models/                # SQLAlchemy Models (user, patient, scan, ai_result, report, audit, metrics)
│   ├── services/              # Business Logic (ai_service, fusion_service, report_service, risk_service, storage)
│   ├── ai/                    # Deep Learning Engine (resnet_fusion.py, preprocessing.py, explainability.py)
│   └── utils/                 # PDF ReportLab Generator, QR Code Generator, RBAC Decorators
│
├── frontend/
│   ├── templates/             # HTML5 Jinja2 Templates (base, auth, admin, doctor, patient, shared)
│   └── static/                # CSS Design System, JS App Scripts, Speech API, PWA Service Worker
│
├── database/
│   ├── schema.sql             # SQL Database DDL Schema (20 Relational Tables)
│   └── seed.sql               # Seed Script
│
├── tests/                     # Automated PyTest Test Suite
└── docs/                      # Technical System Architecture Documentation
```

---

## 📜 Medical Safety Disclaimer

> **MediScan** provides AI-assisted clinical decision support and does **NOT** replace professional medical judgment. All predictions, confidence scores, and risk classifications are designed for qualified healthcare provider review only.
=======
# MediScan
AI-powered medical imaging system integrating medical images and clinical context for disease prediction and analysis.
>>>>>>> 2378a17a8b10fde06af24b8b557a2ebfa699833c
