from flask import request, session
from backend.models import db
from backend.models.audit import AuditLog

def log_audit_event(action, resource_type=None, resource_id=None, user_id=None, role=None):
    """
    Logs tamper-resistant audit event to database.
    """
    try:
        u_id = user_id or session.get('user_id')
        u_role = role or session.get('role_name', 'SYSTEM')
        
        ip_addr = request.remote_addr if request else '127.0.0.1'
        u_agent = request.user_agent.string if request and request.user_agent else 'System/CLI'
        
        audit_entry = AuditLog(
            user_id=u_id,
            role=u_role,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=ip_addr,
            user_agent=u_agent
        )
        db.session.add(audit_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[Audit Log Warning] Failed to write audit event: {e}")
