from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from backend.models import db
from backend.models.user import User, Role, Hospital, Doctor
from backend.models.audit import AuditLog
from backend.models.metrics import ModelVersion, ModelMetric
from backend.utils.decorators import login_required, roles_required
from backend.services.audit_service import log_audit_event

admin_bp = Blueprint('admin_bp', __name__)
bcrypt = Bcrypt()

@admin_bp.route('/api/admin/users', methods=['GET', 'POST'])
@login_required
@roles_required('ADMIN')
def manage_users():
    if request.method == 'GET':
        users = User.query.order_by(User.id.desc()).all()
        return jsonify({'users': [u.to_dict() for u in users]}), 200

    data = request.get_json()
    email = data.get('email', '').strip()
    full_name = data.get('full_name', '').strip()
    password = data.get('password', '').strip()
    role_id = data.get('role_id')
    hospital_id = data.get('hospital_id')

    if not email or not full_name or not password or not role_id:
        return jsonify({'error': 'Bad Request', 'message': 'Missing required fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Conflict', 'message': 'Email already registered'}), 409

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=pw_hash,
        role_id=role_id,
        hospital_id=hospital_id,
        phone=data.get('phone')
    )
    db.session.add(new_user)
    db.session.commit()

    # Create role specific sub-profile if Doctor
    role = Role.query.get(role_id)
    if role and role.name == 'DOCTOR':
        lic = data.get('license_number') or f"LIC-{new_user.id:04d}"
        spec = data.get('specialization') or "Radiology"
        doc = Doctor(user_id=new_user.id, license_number=lic, specialization=spec, department=data.get('department', 'Radiology'))
        db.session.add(doc)

    db.session.commit()
    log_audit_event(action='ADMIN_CREATE_USER', resource_type='User', resource_id=new_user.id)

    return jsonify({'message': 'User created successfully', 'user': new_user.to_dict()}), 201


@admin_bp.route('/api/admin/hospitals', methods=['GET', 'POST'])
@login_required
@roles_required('ADMIN')
def manage_hospitals():
    if request.method == 'GET':
        hospitals = Hospital.query.all()
        return jsonify({'hospitals': [h.to_dict() for h in hospitals]}), 200

    data = request.get_json()
    name = data.get('name')
    code = data.get('code')

    if not name or not code:
        return jsonify({'error': 'Name and Code are required'}), 400

    hospital = Hospital(
        name=name,
        code=code,
        address=data.get('address'),
        contact_email=data.get('contact_email'),
        phone=data.get('phone')
    )
    db.session.add(hospital)
    db.session.commit()

    log_audit_event(action='ADMIN_CREATE_HOSPITAL', resource_type='Hospital', resource_id=hospital.id)
    return jsonify({'message': 'Hospital added successfully', 'hospital': hospital.to_dict()}), 201


@admin_bp.route('/api/admin/audit-logs', methods=['GET'])
@login_required
@roles_required('ADMIN')
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(100).all()
    return jsonify({'audit_logs': [l.to_dict() for l in logs]}), 200


@admin_bp.route('/api/admin/model-performance', methods=['GET'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def get_model_performance():
    models = ModelVersion.query.order_by(ModelVersion.id.desc()).all()
    return jsonify({'models': [m.to_dict() for m in models]}), 200
