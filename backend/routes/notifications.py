from flask import Blueprint, jsonify, session, request
from backend.models import db
from backend.models.audit import Notification
from backend.utils.decorators import login_required

notifications_bp = Blueprint('notifications_bp', __name__)

@notifications_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_user_notifications():
    user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.id.desc()).all()
    return jsonify({'notifications': [n.to_dict() for n in notifications]}), 200

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    n = Notification.query.get_or_404(notification_id)
    if n.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    n.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200
