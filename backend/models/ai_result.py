import json
from datetime import datetime
from backend.models import db

class AIResult(db.Model):
    __tablename__ = 'ai_results'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id', ondelete='CASCADE'), unique=True, nullable=False)
    primary_prediction = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    top3_json = db.Column(db.Text, nullable=False)
    model_version = db.Column(db.String(50), nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    explainability = db.relationship('ExplainabilityResult', backref='ai_result', uselist=False, cascade='all, delete-orphan')
    risk_assessment = db.relationship('RiskAssessment', backref='ai_result', uselist=False, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='ai_result', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'primary_prediction': self.primary_prediction,
            'confidence_score': round(self.confidence_score, 4),
            'confidence_percentage': f"{round(self.confidence_score * 100, 1)}%",
            'top3': json.loads(self.top3_json) if self.top3_json else [],
            'model_version': self.model_version,
            'processed_at': self.processed_at.strftime('%Y-%m-%d %H:%M:%S') if self.processed_at else None,
            'explainability': self.explainability.to_dict() if self.explainability else None,
            'risk_assessment': self.risk_assessment.to_dict() if self.risk_assessment else None
        }


class ExplainabilityResult(db.Model):
    __tablename__ = 'explainability_results'
    
    id = db.Column(db.Integer, primary_key=True)
    ai_result_id = db.Column(db.Integer, db.ForeignKey('ai_results.id', ondelete='CASCADE'), unique=True, nullable=False)
    gradcam_heatmap_path = db.Column(db.String(255))
    lime_explanation_json = db.Column(db.Text)
    shap_values_json = db.Column(db.Text)
    summary_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ai_result_id': self.ai_result_id,
            'gradcam_heatmap_path': self.gradcam_heatmap_path,
            'lime_explanation': json.loads(self.lime_explanation_json) if self.lime_explanation_json else {},
            'shap_values': json.loads(self.shap_values_json) if self.shap_values_json else {},
            'summary_text': self.summary_text
        }


class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    ai_result_id = db.Column(db.Integer, db.ForeignKey('ai_results.id', ondelete='CASCADE'), unique=True, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH
    risk_score = db.Column(db.Float, nullable=False)
    contributing_factors_json = db.Column(db.Text)
    rule_evaluations_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ai_result_id': self.ai_result_id,
            'risk_level': self.risk_level,
            'risk_score': round(self.risk_score, 2),
            'contributing_factors': json.loads(self.contributing_factors_json) if self.contributing_factors_json else [],
            'rule_evaluations': json.loads(self.rule_evaluations_json) if self.rule_evaluations_json else []
        }


class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    ai_result_id = db.Column(db.Integer, db.ForeignKey('ai_results.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    doctor_correct_diagnosis = db.Column(db.String(150))
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ai_result_id': self.ai_result_id,
            'doctor_id': self.doctor_id,
            'is_correct': self.is_correct,
            'doctor_correct_diagnosis': self.doctor_correct_diagnosis,
            'comments': self.comments,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
