from datetime import datetime
from backend.models import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_patient_id = db.Column(db.String(50), unique=True, nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id', ondelete='SET NULL'), nullable=True)
    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    existing_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    scans = db.relationship('Scan', backref='patient', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='patient', lazy=True, cascade='all, delete-orphan')
    timeline_events = db.relationship('PatientTimeline', backref='patient', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'unique_patient_id': self.unique_patient_id,
            'hospital_id': self.hospital_id,
            'full_name': self.full_name,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'gender': self.gender,
            'blood_group': self.blood_group,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'medical_history': self.medical_history,
            'allergies': self.allergies,
            'existing_conditions': self.existing_conditions,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class PatientTimeline(db.Model):
    __tablename__ = 'patient_timeline'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    reference_id = db.Column(db.Integer)
    event_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'reference_id': self.reference_id,
            'event_date': self.event_date.strftime('%Y-%m-%d %H:%M:%S') if self.event_date else None
        }
