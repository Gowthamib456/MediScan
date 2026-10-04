from datetime import datetime
from backend.models import db

class DoctorNote(db.Model):
    __tablename__ = 'doctor_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    clinical_finding = db.Column(db.Text, nullable=False)
    impression = db.Column(db.Text)
    final_diagnosis = db.Column(db.String(150), nullable=False)
    treatment_recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if hasattr(self, 'doctor') and self.doctor else '',
            'clinical_finding': self.clinical_finding,
            'impression': self.impression,
            'final_diagnosis': self.final_diagnosis,
            'treatment_recommendations': self.treatment_recommendations,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class CollaborationNote(db.Model):
    __tablename__ = 'collaboration_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if hasattr(self, 'doctor') and self.doctor else '',
            'note_text': self.note_text,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_uuid = db.Column(db.String(100), unique=True, nullable=False)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id', ondelete='CASCADE'), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    template_type = db.Column(db.String(50), default='Detailed Report')  # Detailed Report, Summary Report, Radiology-style
    ai_prediction = db.Column(db.String(100))
    doctor_final_diagnosis = db.Column(db.String(150), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    pdf_path = db.Column(db.String(255))
    qr_code_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default='DRAFT')  # DRAFT, FINALIZED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finalized_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'report_uuid': self.report_uuid,
            'scan_id': self.scan_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else '',
            'patient_unique_id': self.patient.unique_patient_id if self.patient else '',
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if hasattr(self, 'doctor') and self.doctor else '',
            'template_type': self.template_type,
            'scan_type': self.scan.scan_type if self.scan else '',
            'ai_prediction': self.ai_prediction,
            'doctor_final_diagnosis': self.doctor_final_diagnosis,
            'risk_level': self.risk_level,
            'pdf_path': self.pdf_path,
            'qr_code_path': self.qr_code_path,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'finalized_at': self.finalized_at.strftime('%Y-%m-%d %H:%M:%S') if self.finalized_at else None
        }
