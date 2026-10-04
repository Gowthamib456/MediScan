# MediScan Technical Architecture & System Specification

## 1. System Overview
MediScan is a clinical decision-support web application that combines medical imaging (Chest X-Ray, CT, MRI) with structured patient clinical context (symptoms, vitals, medical history, risk factors) using dual-branch Feature-Level Fusion, ResNet-50 deep learning, and Explainable AI (Grad-CAM, LIME, SHAP).

---

## 2. Technology Stack
- **Backend Core**: Python 3.10+, Flask 3.0, Flask-SQLAlchemy, Flask-Bcrypt, Flask-CORS, PyMySQL, python-dotenv.
- **AI & Analytics**: TensorFlow/Keras (ResNet-50 feature extractor), OpenCV (`opencv-python-headless`), Pillow, NumPy, Pandas, Scikit-Learn.
- **Explainability**: Grad-CAM visual heatmap overlay, LIME local surrogate region explainer, SHAP clinical feature value analyzer.
- **Document & Verification**: ReportLab PDF compilation, `qrcode` generation.
- **Frontend Architecture**: Modular Vanilla JS (ES6+), Bootstrap 5 UI Design System (Light/Dark glassmorphism themes), Chart.js (Analytics & Model performance graphs), Canvas API, Web Speech API (Voice synthesis).
- **Database Engine**: MySQL 8.0+ (with SQLite fallback for dynamic zero-dependency local dev).

---

## 3. Data Flow Diagram (DFD)

```
[ Doctor ]
               │
               ├─► Upload Medical Scan (X-Ray / CT / MRI) ────────┐
               └─► Input Clinical Symptoms, Vitals & History ─────┼──► [ OpenCV Preprocessing ]
                                                                  │           │
                                                                  ▼           ▼
                                                 [ ResNet-50 Image Vector (2048-d) ]
                                                                  │
                                                                  ├─► [ Feature Level Fusion ]
                                                                  │           │
                                                 [ Clinical Context Vector (16-d) ] ──┘
                                                                              │
                                                                              ▼
                                                                  [ Softmax Classification Head ]
                                                                              │
                                       ┌──────────────────────────────────────┼──────────────────────────────────────┐
                                       ▼                                      ▼                                      ▼
                           [ Top 3 Predictions & Conf ]             [ Grad-CAM / LIME / SHAP ]             [ Transparent Risk Framework ]
                                       │                                      │                                      │
                                       └──────────────────────────────────────┼──────────────────────────────────────┘
                                                                              │
                                                                              ▼
                                                             [ Doctor Review & Final Diagnosis ]
                                                                              │
                                                                              ▼
                                                             [ ReportLab PDF & QR Generation ]
                                                                              │
                                                                              ▼
                                                             [ Patient Portal & Voice Speech ]
```

---

## 4. User Role & Permission Matrix (RBAC)

| Role | User Mgmt | Hospital Mgmt | Register Patient | Upload Scan | AI Analysis | Doctor Notes | Finalize Report | View Own Report | Audit Logs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADMIN** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **DOCTOR** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **VIEWER** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Read-Only | ❌ |
| **PATIENT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Own Only) | ❌ |

---

## 5. REST API Architecture

### Authentication
- `POST /api/auth/login` - Authenticates user & sets session
- `POST /api/auth/logout` - Clears session & logs audit event
- `GET /api/auth/me` - Returns active session user

### Patients & Scans
- `GET /api/patients` - List/search patients
- `POST /api/patients` - Register new patient
- `GET /api/patients/<id>` - Patient detail with scans & timeline
- `POST /api/scans/upload` - Upload medical image file
- `GET /api/scans` - List scans with filters
- `GET /api/scans/<id>` - Fetch scan with clinical & AI data

### AI Analysis & Explainability
- `POST /api/ai/analyze/<scan_id>` - Executes 10-step AI Feature Fusion pipeline
- `POST /api/ai/feedback` - Doctor feedback submission for quality assurance

### Reports & Analytics
- `POST /api/reports/generate` - Finalizes report and compiles PDF
- `GET /api/reports` - List reports with RBAC filter
- `GET /api/reports/<id>/pdf` - Download PDF report file
- `GET /api/reports/export` - Export reports as CSV or JSON
- `GET /api/analytics/dashboard` - Global analytics metrics & chart distributions
