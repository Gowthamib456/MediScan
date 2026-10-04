from datetime import datetime
from backend.models import db

class ModelVersion(db.Model):
    __tablename__ = 'model_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_name = db.Column(db.String(50), unique=True, nullable=False)
    framework = db.Column(db.String(50), default='TensorFlow/Keras')
    trained_on = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    metrics = db.relationship('ModelMetric', backref='model_version', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'version_name': self.version_name,
            'framework': self.framework,
            'trained_on': self.trained_on,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'metrics': [m.to_dict() for m in self.metrics]
        }


class ModelMetric(db.Model):
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    model_version_id = db.Column(db.Integer, db.ForeignKey('model_versions.id', ondelete='CASCADE'), nullable=False)
    disease_class = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    sensitivity = db.Column(db.Float, nullable=False)
    specificity = db.Column(db.Float, nullable=False)
    roc_auc = db.Column(db.Float, nullable=False)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'disease_class': self.disease_class,
            'accuracy': round(self.accuracy, 4),
            'precision': round(self.precision, 4),
            'recall': round(self.recall, 4),
            'f1_score': round(self.f1_score, 4),
            'sensitivity': round(self.sensitivity, 4),
            'specificity': round(self.specificity, 4),
            'roc_auc': round(self.roc_auc, 4),
            'evaluated_at': self.evaluated_at.strftime('%Y-%m-%d %H:%M:%S') if self.evaluated_at else None
        }
