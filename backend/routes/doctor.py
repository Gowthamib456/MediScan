from datetime import datetime
import uuid
from flask import Blueprint, request, jsonify, session
from backend.models import db
from backend.models.user import Hospital, User
from backend.models.patient import Patient, PatientTimeline
from backend.models.scan import Scan, ClinicalData
from backend.models.ai_result import AIResult, ExplainabilityResult, RiskAssessment
from backend.models.report import Report, DoctorNote, CollaborationNote
from backend.services.storage_service import storage_service
from backend.utils.decorators import login_required, roles_required
from backend.services.audit_service import log_audit_event

doctor_bp = Blueprint('doctor_bp', __name__)

@doctor_bp.route('/api/patients', methods=['GET', 'POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def api_patients():
    if request.method == 'GET':
        search_query = request.args.get('q', '').strip()
        query = Patient.query
        
        if search_query:
            query = query.filter(
                (Patient.full_name.ilike(f"%{search_query}%")) |
                (Patient.unique_patient_id.ilike(f"%{search_query}%")) |
                (Patient.phone.ilike(f"%{search_query}%"))
            )
            
        patients = query.order_by(Patient.id.desc()).all()
        return jsonify({'patients': [p.to_dict() for p in patients]}), 200

    data = request.get_json()
    full_name = data.get('full_name', '').strip()
    dob_str = data.get('dob', '').strip()
    gender = data.get('gender', '').strip()

    if not full_name or not dob_str or not gender:
        return jsonify({'error': 'Bad Request', 'message': 'Full name, DOB, and gender are required'}), 400

    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Bad Request', 'message': 'DOB must be YYYY-MM-DD'}), 400

    unique_pid = f"PAT-{uuid.uuid4().hex[:8].upper()}"

    new_patient = Patient(
        unique_patient_id=unique_pid,
        hospital_id=session.get('hospital_id'),
        full_name=full_name,
        dob=dob,
        gender=gender,
        blood_group=data.get('blood_group'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        medical_history=data.get('medical_history'),
        allergies=data.get('allergies'),
        existing_conditions=data.get('existing_conditions')
    )
    db.session.add(new_patient)
    db.session.commit()

    # Timeline event
    timeline = PatientTimeline(
        patient_id=new_patient.id,
        event_type='PATIENT_REGISTERED',
        title='Patient Registered',
        description=f"Patient registered with ID: {unique_pid}"
    )
    db.session.add(timeline)
    db.session.commit()

    log_audit_event(action='PATIENT_REGISTERED', resource_type='Patient', resource_id=new_patient.id)
    return jsonify({'message': 'Patient registered successfully', 'patient': new_patient.to_dict()}), 201


@doctor_bp.route('/api/patients/<int:patient_id>', methods=['GET', 'PUT'])
@login_required
@roles_required('ADMIN', 'DOCTOR', 'VIEWER')
def api_patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        scans = [s.to_dict() for s in patient.scans]
        reports = [r.to_dict() for r in patient.reports]
        timeline = [t.to_dict() for t in patient.timeline_events]
        
        p_dict = patient.to_dict()
        p_dict['scans'] = scans
        p_dict['reports'] = reports
        p_dict['timeline'] = timeline
        return jsonify({'patient': p_dict}), 200

    if session.get('role_name') not in ['ADMIN', 'DOCTOR']:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json() or {}
    if data.get('dob'):
        try:
            patient.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Bad Request', 'message': 'DOB must be YYYY-MM-DD'}), 400
    patient.gender = data.get('gender', patient.gender)
    patient.full_name = data.get('full_name', patient.full_name)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.phone = data.get('phone', patient.phone)
    patient.email = data.get('email', patient.email)
    patient.address = data.get('address', patient.address)
    patient.medical_history = data.get('medical_history', patient.medical_history)
    patient.allergies = data.get('allergies', patient.allergies)
    patient.existing_conditions = data.get('existing_conditions', patient.existing_conditions)

    db.session.commit()
    log_audit_event(action='PATIENT_UPDATED', resource_type='Patient', resource_id=patient.id)
    return jsonify({'message': 'Patient profile updated', 'patient': patient.to_dict()}), 200


@doctor_bp.route('/api/hospitals/all', methods=['GET'])
@login_required
def get_all_hospitals():
    hospitals = Hospital.query.all()
    return jsonify({'hospitals': [h.to_dict() for h in hospitals]}), 200


@doctor_bp.route('/api/patients/transfer', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def transfer_patient_api():
    data = request.get_json()
    patient_id = data.get('patient_id')
    target_hospital_id = data.get('target_hospital_id')
    reason = data.get('reason', 'Patient Relocation / Inter-Hospital Referral')

    if not patient_id or not target_hospital_id:
        return jsonify({'error': 'patient_id and target_hospital_id are required'}), 400

    try:
        transfer_result = storage_service.transfer_patient_to_hospital(
            patient_id=patient_id,
            target_hospital_id=target_hospital_id,
            transferring_user_id=session.get('user_id'),
            transfer_reason=reason
        )
        return jsonify({
            'message': 'Inter-Hospital Secure Transfer completed successfully',
            'transfer': transfer_result
        }), 200
    except Exception as e:
        return jsonify({'error': 'Transfer Error', 'message': str(e)}), 500


@doctor_bp.route('/api/clinical-data', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def api_clinical_data():
    data = request.get_json()
    scan_id = data.get('scan_id')
    
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
        
    scan = Scan.query.get_or_404(scan_id)
    
    clin_data = ClinicalData.query.filter_by(scan_id=scan.id).first()
    if not clin_data:
        clin_data = ClinicalData(
            scan_id=scan.id,
            patient_id=scan.patient_id,
            symptoms=data.get('symptoms', 'None'),
            duration_days=int(data.get('duration_days', 0)),
            age=int(data.get('age', 40)),
            gender=data.get('gender', 'Male'),
            blood_pressure=data.get('blood_pressure', '120/80'),
            diabetes=bool(data.get('diabetes', False)),
            hypertension=bool(data.get('hypertension', False)),
            smoking_status=data.get('smoking_status', 'Non-Smoker'),
            previous_diseases=data.get('previous_diseases'),
            current_medications=data.get('current_medications'),
            allergies=data.get('allergies'),
            clinical_notes=data.get('clinical_notes')
        )
        db.session.add(clin_data)
    else:
        clin_data.symptoms = data.get('symptoms', clin_data.symptoms)
        clin_data.duration_days = int(data.get('duration_days', clin_data.duration_days))
        clin_data.age = int(data.get('age', clin_data.age))
        clin_data.gender = data.get('gender', clin_data.gender)
        clin_data.blood_pressure = data.get('blood_pressure', clin_data.blood_pressure)
        clin_data.diabetes = bool(data.get('diabetes', clin_data.diabetes))
        clin_data.hypertension = bool(data.get('hypertension', clin_data.hypertension))
        clin_data.smoking_status = data.get('smoking_status', clin_data.smoking_status)
        clin_data.previous_diseases = data.get('previous_diseases', clin_data.previous_diseases)
        clin_data.current_medications = data.get('current_medications', clin_data.current_medications)

    db.session.commit()
    log_audit_event(action='CLINICAL_DATA_RECORDED', resource_type='Scan', resource_id=scan.id)
    return jsonify({'message': 'Clinical data saved successfully', 'clinical_data': clin_data.to_dict()}), 200


@doctor_bp.route('/api/scans/compare', methods=['GET'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def compare_scans():
    scan_id1 = request.args.get('scan1_id', type=int)
    scan_id2 = request.args.get('scan2_id', type=int)

    if not scan_id1 or not scan_id2:
        return jsonify({'error': 'Two scan IDs are required'}), 400

    scan1 = Scan.query.get_or_404(scan_id1)
    scan2 = Scan.query.get_or_404(scan_id2)

    return jsonify({
        'scan1': scan1.to_dict(),
        'scan2': scan2.to_dict(),
        'scan1_ai': scan1.ai_result.to_dict() if scan1.ai_result else None,
        'scan2_ai': scan2.ai_result.to_dict() if scan2.ai_result else None
    }), 200


@doctor_bp.route('/api/collaboration-notes', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def add_collaboration_note():
    data = request.get_json()
    scan_id = data.get('scan_id')
    note_text = data.get('note_text', '').strip()

    if not scan_id or not note_text:
        return jsonify({'error': 'Scan ID and note text are required'}), 400

    note = CollaborationNote(
        scan_id=scan_id,
        doctor_id=session['user_id'],
        note_text=note_text
    )
    db.session.add(note)
    db.session.commit()

    log_audit_event(action='COLLABORATION_NOTE_ADDED', resource_type='Scan', resource_id=scan_id)
    return jsonify({'message': 'Note added successfully', 'note': note.to_dict()}), 201
