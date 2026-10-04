from flask import Blueprint, jsonify, session
from sqlalchemy import func
from backend.models import db
from backend.models.patient import Patient
from backend.models.scan import Scan
from backend.models.ai_result import AIResult, RiskAssessment
from backend.models.report import Report
from backend.utils.decorators import login_required, roles_required

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/api/analytics/dashboard', methods=['GET'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def get_analytics_data():
    total_patients = Patient.query.count()
    total_scans = Scan.query.count()
    total_reports = Report.query.filter_by(status='FINALIZED').count()
    pending_reviews = Scan.query.filter_by(status='ANALYZED').count()

    # Average AI Confidence
    avg_conf = db.session.query(func.avg(AIResult.confidence_score)).scalar() or 0.0

    # Diagnosis Distribution
    diag_counts = db.session.query(
        AIResult.primary_prediction, func.count(AIResult.id)
    ).group_by(AIResult.primary_prediction).all()
    
    diag_dist = [{'label': d[0], 'count': d[1]} for d in diag_counts]

    # Risk Distribution
    risk_counts = db.session.query(
        RiskAssessment.risk_level, func.count(RiskAssessment.id)
    ).group_by(RiskAssessment.risk_level).all()
    
    risk_dist = [{'risk_level': r[0], 'count': r[1]} for r in risk_counts]

    # Scan Type Distribution
    scan_type_counts = db.session.query(
        Scan.scan_type, func.count(Scan.id)
    ).group_by(Scan.scan_type).all()
    
    scan_type_dist = [{'scan_type': st[0], 'count': st[1]} for st in scan_type_counts]

    return jsonify({
        'summary': {
            'total_patients': total_patients,
            'total_scans': total_scans,
            'reports_generated': total_reports,
            'pending_reviews': pending_reviews,
            'average_confidence': round(avg_conf * 100, 1),
            'high_risk_cases': sum(r['count'] for r in risk_dist if r['risk_level'] == 'HIGH')
        },
        'diagnosis_distribution': diag_dist,
        'risk_distribution': risk_dist,
        'scan_type_distribution': scan_type_dist
    }), 200
