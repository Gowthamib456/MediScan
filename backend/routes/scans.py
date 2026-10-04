from flask import Blueprint, request, jsonify, session
from backend.models import db
from backend.models.patient import Patient, PatientTimeline
from backend.models.scan import Scan
from backend.services.storage_service import storage_service
from backend.utils.decorators import login_required, roles_required
from backend.services.audit_service import log_audit_event

scans_bp = Blueprint('scans_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@scans_bp.route('/api/scans/upload', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def upload_scans():
    patient_id = request.form.get('patient_id')
    scan_type = request.form.get('scan_type', 'X-ray')
    body_part = request.form.get('body_part', 'Chest')

    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400

    patient = Patient.query.get_or_404(patient_id)

    files = request.files.getlist('scans') or request.files.getlist('file')
    if not files or len(files) == 0:
        return jsonify({'error': 'No file uploaded'}), 400

    uploaded_scans = []

    for file_obj in files:
        if file_obj and allowed_file(file_obj.filename):
            save_res = storage_service.save_file(file_obj, subfolder=f"scans/pat_{patient.id}")
            
            scan = Scan(
                patient_id=patient.id,
                uploaded_by_id=session['user_id'],
                doctor_id=session['user_id'] if session.get('role_name') == 'DOCTOR' else None,
                scan_type=scan_type,
                body_part=body_part,
                image_path=save_res['relative_path'],
                original_filename=save_res['filename'],
                file_size=save_res['file_size'],
                status='UPLOADED'
            )
            db.session.add(scan)
            db.session.commit()

            # Timeline event
            t_event = PatientTimeline(
                patient_id=patient.id,
                event_type='SCAN_UPLOADED',
                title=f"Medical Scan Uploaded ({scan_type})",
                description=f"File: {save_res['filename']} ({round(save_res['file_size']/1024, 1)} KB)",
                reference_id=scan.id
            )
            db.session.add(t_event)
            db.session.commit()

            log_audit_event(action='SCAN_UPLOADED', resource_type='Scan', resource_id=scan.id)
            uploaded_scans.append(scan.to_dict())

    return jsonify({'message': f'Successfully uploaded {len(uploaded_scans)} scan(s)', 'scans': uploaded_scans}), 201


@scans_bp.route('/api/scans', methods=['GET'])
@login_required
@roles_required('ADMIN', 'DOCTOR', 'VIEWER')
def get_scans():
    patient_id = request.args.get('patient_id', type=int)
    scan_type = request.args.get('scan_type')
    status = request.args.get('status')

    query = Scan.query

    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    if scan_type:
        query = query.filter_by(scan_type=scan_type)
    if status:
        query = query.filter_by(status=status)

    scans = query.order_by(Scan.id.desc()).all()
    return jsonify({'scans': [s.to_dict() for s in scans]}), 200


@scans_bp.route('/api/scans/<int:scan_id>', methods=['GET'])
@login_required
@roles_required('ADMIN', 'DOCTOR', 'VIEWER')
def get_scan_detail(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    s_dict = scan.to_dict()

    if scan.clinical_data:
        s_dict['clinical_data'] = scan.clinical_data.to_dict()
    if scan.ai_result:
        s_dict['ai_result'] = scan.ai_result.to_dict()
    if scan.report:
        s_dict['report'] = scan.report.to_dict()

    s_dict['doctor_notes'] = [n.to_dict() for n in scan.doctor_notes]
    s_dict['collaboration_notes'] = [c.to_dict() for c in scan.collaboration_notes]

    return jsonify({'scan': s_dict}), 200
