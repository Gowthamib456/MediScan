-- MediScan Seed Data (PostgreSQL / Neon Compliant)

-- 1. Roles
INSERT INTO roles (id, name, description) VALUES
(1, 'ADMIN', 'System Administrator with full access'),
(2, 'DOCTOR', 'Medical Doctor able to register patients, upload & analyze scans, enter notes, and finalize reports'),
(3, 'VIEWER', 'Read-only access to authorized reports'),
(4, 'PATIENT', 'Patient viewing their own profile, timeline, and finalized medical reports')
ON CONFLICT (id) DO NOTHING;

-- 2. Hospitals
INSERT INTO hospitals (id, name, code, address, contact_email, phone) VALUES
(1, 'Metro Health General Hospital', 'MHGH-001', '100 Medical Center Blvd, Suite 400', 'contact@metrohealth.org', '+1-800-555-0199')
ON CONFLICT (id) DO NOTHING;

-- 3. Initial Model Versions
INSERT INTO model_versions (id, version_name, framework, trained_on, is_active) VALUES
(1, 'v1.2.0-resnet50-fusion', 'TensorFlow/Keras + ResNet50', 'NIH Chest X-Ray 14 + Clinical Context Synthetic Corpus', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 4. Model Metrics
INSERT INTO model_metrics (model_version_id, disease_class, accuracy, precision, recall, f1_score, sensitivity, specificity, roc_auc) VALUES
(1, 'Pneumonia', 0.942, 0.931, 0.950, 0.940, 0.950, 0.935, 0.978),
(1, 'Tuberculosis', 0.928, 0.915, 0.932, 0.923, 0.932, 0.924, 0.965),
(1, 'Normal', 0.965, 0.970, 0.960, 0.965, 0.960, 0.972, 0.989),
(1, 'Atelectasis / Infiltration', 0.895, 0.880, 0.902, 0.891, 0.902, 0.888, 0.941)
ON CONFLICT DO NOTHING;
