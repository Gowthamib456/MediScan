from datetime import datetime
from backend.models import db

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    scan_type = db.Column(db.String(50), nullable=False)  # Chest X-ray, CT Scan, MRI
    body_part = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    preprocessed_image_path = db.Column(db.String(255))
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    status = db.Column(db.String(50), default='UPLOADED')  # UPLOADED, ANALYZED, REVIEWED, FINALIZED
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    clinical_data = db.relationship('ClinicalData', backref='scan', uselist=False, cascade='all, delete-orphan')
    ai_result = db.relationship('AIResult', backref='scan', uselist=False, cascade='all, delete-orphan')
    doctor_notes = db.relationship('DoctorNote', backref='scan', lazy=True, cascade='all, delete-orphan')
    collaboration_notes = db.relationship('CollaborationNote', backref='scan', lazy=True, cascade='all, delete-orphan')
    report = db.relationship('Report', backref='scan', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        result = {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else '',
            'patient_unique_id': self.patient.unique_patient_id if self.patient else '',
            'uploaded_by_id': self.uploaded_by_id,
            'doctor_id': self.doctor_id,
            'scan_type': self.scan_type,
            'body_part': self.body_part,
            'image_path': self.image_path,
            'preprocessed_image_path': self.preprocessed_image_path,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'status': self.status,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None,
            'has_clinical_data': self.clinical_data is not None,
            'has_ai_result': self.ai_result is not None,
            'has_report': self.report is not None
        }
        result['ai_result'] = self.ai_result.to_dict() if self.ai_result else None
        return result


class ClinicalData(db.Model):
    __tablename__ = 'clinical_data'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id', ondelete='CASCADE'), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    duration_days = db.Column(db.Integer)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_pressure = db.Column(db.String(20))
    diabetes = db.Column(db.Boolean, default=False)
    hypertension = db.Column(db.Boolean, default=False)
    smoking_status = db.Column(db.String(50))
    previous_diseases = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    allergies = db.Column(db.Text)
    clinical_notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'patient_id': self.patient_id,
            'symptoms': self.symptoms,
            'duration_days': self.duration_days,
            'age': self.age,
            'gender': self.gender,
            'blood_pressure': self.blood_pressure,
            'diabetes': self.diabetes,
            'hypertension': self.hypertension,
            'smoking_status': self.smoking_status,
            'previous_diseases': self.previous_diseases,
            'current_medications': self.current_medications,
            'allergies': self.allergies,
            'clinical_notes': self.clinical_notes,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d %H:%M:%S') if self.recorded_at else None
        }
