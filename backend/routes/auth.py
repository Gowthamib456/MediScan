import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, session, redirect, url_for
from flask_bcrypt import Bcrypt
from backend.models import db
from backend.models.user import User, Role, Doctor
from backend.models.patient import Patient, PatientTimeline
from backend.services.audit_service import log_audit_event

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

def _patient_identity(data):
    email = data.get('email', '').strip().lower()
    patient_id = data.get('patient_id', '').strip().upper()
    patient_name = data.get('patient_name', '').strip()

    if not email or not patient_id or not patient_name:
        return None, ('Bad Request', 'Patient email, name, and Patient ID are required.'), 400

    patient = Patient.query.filter_by(unique_patient_id=patient_id).first()
    if not patient:
        return None, ('Not Found', 'Patient ID was not found.'), 404
    if (patient.email or '').strip().lower() != email or patient.full_name.casefold() != patient_name.casefold():
        return None, ('Unauthorized', 'Patient name, email, and Patient ID do not match.'), 401
    return patient, None, None

@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or request.form
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    role_name = data.get('role_name', 'PATIENT').strip().upper()
    phone = data.get('phone', '').strip()
    hospital_id = data.get('hospital_id') or 1

    if not full_name or not email or not password:
        return jsonify({'error': 'Bad Request', 'message': 'Full name, email, and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Conflict', 'message': 'An account with this email already exists'}), 409

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role.query.filter_by(name='PATIENT').first()

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        hospital_id=hospital_id,
        role_id=role.id,
        full_name=full_name,
        email=email,
        password_hash=pw_hash,
        phone=phone,
        status='ACTIVE'
    )
    db.session.add(new_user)
    db.session.commit()

    # Role specific sub-profile creation
    patient_rec = None
    if role.name == 'DOCTOR':
        lic = data.get('license_number') or f"LIC-{new_user.id:04d}"
        spec = data.get('specialization') or "Radiology"
        doc = Doctor(user_id=new_user.id, license_number=lic, specialization=spec, department=data.get('department', 'Radiology'))
        db.session.add(doc)
    elif role.name == 'PATIENT':
        # Create linked patient profile record
        unique_pid = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        dob_str = data.get('dob') or '1990-01-01'
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            dob = datetime(1990, 1, 1).date()

        patient_rec = Patient(
            unique_patient_id=unique_pid,
            hospital_id=hospital_id,
            full_name=full_name,
            dob=dob,
            gender=data.get('gender', 'Male'),
            blood_group=data.get('blood_group', 'O+'),
            phone=phone,
            email=email,
            address=data.get('address', ''),
            medical_history='Self registered patient account'
        )
        db.session.add(patient_rec)
        db.session.commit()

        t_event = PatientTimeline(
            patient_id=patient_rec.id,
            event_type='ACCOUNT_CREATED',
            title='Patient Account Registered',
            description=f"Self-registered online account with Patient ID: {unique_pid}"
        )
        db.session.add(t_event)

    db.session.commit()
    log_audit_event(action='USER_REGISTERED', resource_type='User', resource_id=new_user.id, user_id=new_user.id, role=role.name)

    dashboard_routes = {
        'ADMIN': '/admin/dashboard',
        'DOCTOR': '/doctor/dashboard',
        'VIEWER': '/doctor/dashboard',
        'PATIENT': '/patient/dashboard'
    }

    # Auto login on registration
    session['user_id'] = new_user.id
    session['full_name'] = new_user.full_name
    session['email'] = new_user.email
    session['role_id'] = new_user.role_id
    session['role_name'] = role.name
    session['hospital_id'] = new_user.hospital_id
    if patient_rec:
        session['patient_record_id'] = patient_rec.id

    return jsonify({
        'message': 'Registration successful',
        'user': new_user.to_dict(),
        'patient_id': patient_rec.unique_patient_id if patient_rec else None,
        'redirect_url': dashboard_routes.get(role.name, '/patient/dashboard')
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or request.form
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    patient_id = data.get('patient_id', '').strip().upper()
    patient_name = data.get('patient_name', '').strip()

    if not email or not password:
        return jsonify({'error': 'Bad Request', 'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid email or password'}), 401

    if user.status != 'ACTIVE':
        return jsonify({'error': 'Forbidden', 'message': 'Account is inactive. Please contact system admin.'}), 403

    if user.role.name == 'PATIENT':
        if not patient_id:
            return jsonify({'error': 'Bad Request', 'message': 'Patient ID is required for patient login.'}), 400
        patient_record = Patient.query.filter_by(unique_patient_id=patient_id).first()
        if not patient_record:
            return jsonify({'error': 'Not Found', 'message': 'Patient ID was not found. Enter the Patient ID exactly as provided.'}), 404
        if patient_name.casefold() != patient_record.full_name.casefold():
            return jsonify({'error': 'Unauthorized', 'message': 'Patient name does not match the entered Patient ID.'}), 401
        session['patient_record_id'] = patient_record.id

    # Set Session
    session['user_id'] = user.id
    session['full_name'] = user.full_name
    session['email'] = user.email
    session['role_id'] = user.role_id
    session['role_name'] = user.role.name
    session['hospital_id'] = user.hospital_id

    log_audit_event(action='USER_LOGIN', resource_type='User', resource_id=user.id, user_id=user.id, role=user.role.name)

    dashboard_routes = {
        'ADMIN': '/admin/dashboard',
        'DOCTOR': '/doctor/dashboard',
        'VIEWER': '/doctor/dashboard',
        'PATIENT': '/patient/dashboard'
    }

    redirect_url = dashboard_routes.get(user.role.name, '/doctor/dashboard')

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'redirect_url': redirect_url
    }), 200


@auth_bp.route('/api/auth/patient/password', methods=['POST'])
def set_patient_password():
    """Create or reset a patient password after verifying their stored identity."""
    data = request.get_json() or request.form
    patient, error, status = _patient_identity(data)
    if error:
        return jsonify({'error': error[0], 'message': error[1]}), status

    password = data.get('password', '').strip()
    if len(password) < 8:
        return jsonify({'error': 'Bad Request', 'message': 'Password must contain at least 8 characters.'}), 400

    patient_role = Role.query.filter_by(name='PATIENT').first()
    user = User.query.filter_by(email=patient.email.strip().lower()).first()
    if user and user.role.name != 'PATIENT':
        return jsonify({'error': 'Conflict', 'message': 'This email belongs to a non-patient account.'}), 409
    if not user:
        user = User(
            hospital_id=patient.hospital_id,
            role_id=patient_role.id,
            full_name=patient.full_name,
            email=patient.email.strip().lower(),
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            phone=patient.phone,
            status='ACTIVE'
        )
        db.session.add(user)
    else:
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user.full_name = patient.full_name
        user.status = 'ACTIVE'
    db.session.commit()

    session['user_id'] = user.id
    session['full_name'] = user.full_name
    session['email'] = user.email
    session['role_id'] = user.role_id
    session['role_name'] = 'PATIENT'
    session['hospital_id'] = user.hospital_id
    session['patient_record_id'] = patient.id

    return jsonify({'message': 'Password saved. Opening your patient portal.', 'redirect_url': '/patient/dashboard'}), 200


@auth_bp.route('/api/auth/logout', methods=['POST', 'GET'])
def api_logout():
    user_id = session.get('user_id')
    if user_id:
        log_audit_event(action='USER_LOGOUT', resource_type='User', resource_id=user_id)
    session.clear()
    
    if request.path.startswith('/api/'):
        return jsonify({'message': 'Logged out successfully'}), 200
    return redirect(url_for('auth_login'))


@auth_bp.route('/api/auth/me', methods=['GET'])
def api_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200
