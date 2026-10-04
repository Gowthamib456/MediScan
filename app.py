import os
import datetime
import uuid
from flask import Flask, render_template, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageDraw
from config import Config
from backend.models import db
from backend.models.user import User, Role, Hospital, Doctor
from backend.models.patient import Patient, PatientTimeline
from backend.models.scan import Scan, ClinicalData
from backend.models.ai_result import AIResult, ExplainabilityResult, RiskAssessment
from backend.models.report import Report, DoctorNote
from backend.models.metrics import ModelVersion, ModelMetric
from backend.routes.auth import auth_bp, bcrypt
from backend.routes.admin import admin_bp
from backend.routes.doctor import doctor_bp
from backend.routes.patient import patient_bp
from backend.routes.scans import scans_bp
from backend.routes.ai import ai_bp
from backend.routes.reports import reports_bp
from backend.routes.analytics import analytics_bp
from backend.routes.notifications import notifications_bp
from backend.services.ai_service import run_ai_feature_fusion_pipeline
from backend.services.report_service import generate_and_finalize_report

app = Flask(
    __name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)

app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
bcrypt.init_app(app)
CORS(app)

# Register API Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(scans_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(notifications_bp)

# Static file serving for uploads and generated reports
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/generated_reports/<path:filename>')
def serve_generated_reports(filename):
    return send_from_directory(app.config['REPORTS_FOLDER'], filename)

# HTML View Routes
@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role_name')
        if role == 'ADMIN':
            return redirect(url_for('view_admin_dashboard'))
        elif role == 'PATIENT':
            return redirect(url_for('view_patient_dashboard'))
        else:
            return redirect(url_for('view_doctor_dashboard'))
    return redirect(url_for('auth_login'))

@app.route('/login')
def auth_login():
    return render_template('auth/login.html')

@app.route('/register')
def auth_register():
    return render_template('auth/register.html')

@app.route('/admin/dashboard')
def view_admin_dashboard():
    if 'user_id' not in session or session.get('role_name') != 'ADMIN':
        return redirect(url_for('auth_login'))
    return render_template('admin/dashboard.html')

@app.route('/doctor/dashboard')
def view_doctor_dashboard():
    if 'user_id' not in session or session.get('role_name') not in ['ADMIN', 'DOCTOR', 'VIEWER']:
        return redirect(url_for('auth_login'))
    return render_template('doctor/dashboard.html')

@app.route('/doctor/patients')
def view_doctor_patients():
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    return render_template('doctor/patients.html')

@app.route('/doctor/patient-detail/<int:patient_id>')
def view_patient_detail(patient_id):
    if 'user_id' not in session or session.get('role_name') not in ['ADMIN', 'DOCTOR', 'VIEWER']:
        return redirect(url_for('auth_login'))
    return render_template('doctor/patient_detail.html', patient_id=patient_id)

@app.route('/doctor/upload-scan')
def view_upload_scan():
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    return render_template('doctor/upload_scan.html')

@app.route('/doctor/scan-analysis/<int:scan_id>')
def view_scan_analysis(scan_id):
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    scan = Scan.query.get_or_404(scan_id)
    return render_template('doctor/scan_analysis.html', scan=scan.to_dict())

@app.route('/doctor/compare-scans')
def view_compare_scans():
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    return render_template('doctor/scan_compare.html')

@app.route('/doctor/reports')
def view_doctor_reports():
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    return render_template('doctor/reports.html')

@app.route('/doctor/analytics')
def view_doctor_analytics():
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    return render_template('doctor/analytics.html')

@app.route('/patient/dashboard')
def view_patient_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth_login'))
    return render_template('patient/dashboard.html')

# Database Initialization & Seeding Routine
def seed_database_defaults():
    """Populates database with initial roles, hospitals, demo users, sample patient & sample scan."""
    with app.app_context():
        try:
            db.create_all()

            # Seed Roles
            roles_map = {
                'ADMIN': 'System Administrator with full access',
                'DOCTOR': 'Medical Doctor with diagnosis & reporting permissions',
                'VIEWER': 'Read-only access to authorized reports',
                'PATIENT': 'Patient viewing own profile and reports'
            }
            
            db_roles = {}
            for r_name, r_desc in roles_map.items():
                r = Role.query.filter_by(name=r_name).first()
                if not r:
                    r = Role(name=r_name, description=r_desc)
                    db.session.add(r)
                    db.session.commit()
                db_roles[r_name] = r.id

            # Seed Hospital
            hosp = Hospital.query.filter_by(code='MHGH-001').first()
            if not hosp:
                hosp = Hospital(
                    name='Metro Health General Hospital',
                    code='MHGH-001',
                    address='100 Medical Center Blvd, Suite 400',
                    contact_email='contact@metrohealth.org',
                    phone='+1-800-555-0199'
                )
                db.session.add(hosp)
                db.session.commit()

            # Seed Demo Users
            demo_users = [
                ('Admin User', 'admin@mediscan.org', 'Admin123!', db_roles['ADMIN']),
                ('Dr. Sarah Jenkins', 'doctor@mediscan.org', 'Doctor123!', db_roles['DOCTOR'])
            ]

            created_users = {}
            for name, email, raw_pw, r_id in demo_users:
                pw_hash = bcrypt.generate_password_hash(raw_pw).decode('utf-8')
                u = User.query.filter_by(email=email).first()
                if not u:
                    u = User(hospital_id=hosp.id, role_id=r_id, full_name=name, email=email, password_hash=pw_hash)
                    db.session.add(u)
                    db.session.commit()

                    if r_id == db_roles['DOCTOR']:
                        doc = Doctor(user_id=u.id, license_number='LIC-8849', specialization='Radiology', department='Radiology')
                        db.session.add(doc)
                    db.session.commit()
                else:
                    u.role_id = r_id
                    db.session.commit()
                created_users[email] = u

            # Seed Sample Model Version & Metrics
            mv = ModelVersion.query.filter_by(version_name='v1.2.0-resnet50-fusion').first()
            if not mv:
                mv = ModelVersion(version_name='v1.2.0-resnet50-fusion', framework='TensorFlow/Keras + ResNet50', trained_on='NIH Chest X-Ray 14 + Clinical Corpus')
                db.session.add(mv)
                db.session.commit()

                metrics = [
                    ModelMetric(model_version_id=mv.id, disease_class='Pneumonia', accuracy=0.942, precision=0.931, recall=0.950, f1_score=0.940, sensitivity=0.950, specificity=0.935, roc_auc=0.978),
                    ModelMetric(model_version_id=mv.id, disease_class='Tuberculosis', accuracy=0.928, precision=0.915, recall=0.932, f1_score=0.923, sensitivity=0.932, specificity=0.924, roc_auc=0.965),
                    ModelMetric(model_version_id=mv.id, disease_class='Normal', accuracy=0.965, precision=0.970, recall=0.960, f1_score=0.965, sensitivity=0.960, specificity=0.972, roc_auc=0.989)
                ]
                db.session.add_all(metrics)
                db.session.commit()
        except Exception as e:
            print("Database initialization notice:", e)

# Auto seed database on startup
seed_database_defaults()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
