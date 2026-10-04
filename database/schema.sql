-- MediScan Complete Database Schema
-- Standard PostgreSQL DDL for Neon Cloud Database & SQLite

CREATE TABLE IF NOT EXISTS hospitals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER,
    role_id INTEGER NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    unique_patient_id VARCHAR(50) UNIQUE NOT NULL,
    hospital_id INTEGER,
    full_name VARCHAR(150) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    blood_group VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(150),
    address TEXT,
    emergency_contact VARCHAR(100),
    medical_history TEXT,
    allergies TEXT,
    existing_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    uploaded_by_id INTEGER,
    doctor_id INTEGER,
    scan_type VARCHAR(50) NOT NULL,
    body_part VARCHAR(100) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    preprocessed_image_path VARCHAR(255),
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    status VARCHAR(50) DEFAULT 'UPLOADED',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS clinical_data (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL,
    symptoms TEXT NOT NULL,
    duration_days INTEGER,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    blood_pressure VARCHAR(20),
    diabetes BOOLEAN DEFAULT FALSE,
    hypertension BOOLEAN DEFAULT FALSE,
    smoking_status VARCHAR(50),
    previous_diseases TEXT,
    current_medications TEXT,
    allergies TEXT,
    clinical_notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_results (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER UNIQUE NOT NULL,
    primary_prediction VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    top3_json TEXT NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS explainability_results (
    id SERIAL PRIMARY KEY,
    ai_result_id INTEGER UNIQUE NOT NULL,
    gradcam_heatmap_path VARCHAR(255),
    lime_explanation_json TEXT,
    shap_values_json TEXT,
    summary_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_result_id) REFERENCES ai_results(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id SERIAL PRIMARY KEY,
    ai_result_id INTEGER UNIQUE NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_score FLOAT NOT NULL,
    contributing_factors_json TEXT,
    rule_evaluations_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_result_id) REFERENCES ai_results(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS doctor_notes (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    clinical_finding TEXT NOT NULL,
    impression TEXT,
    final_diagnosis VARCHAR(150) NOT NULL,
    treatment_recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS collaboration_notes (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_uuid VARCHAR(100) UNIQUE NOT NULL,
    scan_id INTEGER UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    template_type VARCHAR(50) DEFAULT 'Detailed Report',
    ai_prediction VARCHAR(100),
    doctor_final_diagnosis VARCHAR(150) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    pdf_path VARCHAR(255),
    qr_code_path VARCHAR(255),
    status VARCHAR(50) DEFAULT 'DRAFT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalized_at TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS patient_timeline (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    reference_id INTEGER,
    event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    role VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    ai_result_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    doctor_correct_diagnosis VARCHAR(150),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_result_id) REFERENCES ai_results(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS model_versions (
    id SERIAL PRIMARY KEY,
    version_name VARCHAR(50) UNIQUE NOT NULL,
    framework VARCHAR(50) DEFAULT 'TensorFlow/Keras',
    trained_on VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_version_id INTEGER NOT NULL,
    disease_class VARCHAR(100) NOT NULL,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    sensitivity FLOAT NOT NULL,
    specificity FLOAT NOT NULL,
    roc_auc FLOAT NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_version_id) REFERENCES model_versions(id) ON DELETE CASCADE
);
