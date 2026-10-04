from flask import Blueprint, request, jsonify, session
from backend.models import db
from backend.models.scan import Scan
from backend.models.ai_result import AIResult, Feedback
from backend.services.ai_service import run_ai_feature_fusion_pipeline
from backend.utils.decorators import login_required, roles_required
from backend.services.audit_service import log_audit_event

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/api/ai/analyze/<int:scan_id>', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def analyze_scan(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    
    try:
        ai_res = run_ai_feature_fusion_pipeline(scan.id)
        return jsonify({
            'message': 'AI Feature-Level Fusion Analysis completed successfully',
            'ai_result': ai_res.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'AI Processing Error', 'message': str(e)}), 500


@ai_bp.route('/api/ai/feedback', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def submit_ai_feedback():
    data = request.get_json()
    ai_result_id = data.get('ai_result_id')
    is_correct = data.get('is_correct')
    doctor_correct_diagnosis = data.get('doctor_correct_diagnosis')
    comments = data.get('comments')

    if not ai_result_id or is_correct is None:
        return jsonify({'error': 'ai_result_id and is_correct are required'}), 400

    feedback = Feedback(
        ai_result_id=ai_result_id,
        doctor_id=session['user_id'],
        is_correct=bool(is_correct),
        doctor_correct_diagnosis=doctor_correct_diagnosis,
        comments=comments
    )
    db.session.add(feedback)
    db.session.commit()

    log_audit_event(action='AI_FEEDBACK_SUBMITTED', resource_type='AIResult', resource_id=ai_result_id)
    return jsonify({'message': 'Feedback recorded for model quality assurance'}), 201
