import os
import csv
import json
from io import StringIO
from flask import Blueprint, request, jsonify, session, send_file, Response
from backend.models import db
from backend.models.report import Report
from backend.models.patient import Patient
from backend.services.report_service import generate_and_finalize_report
from backend.utils.decorators import login_required, roles_required
from backend.services.audit_service import log_audit_event

reports_bp = Blueprint('reports_bp', __name__)

@reports_bp.route('/api/reports/generate', methods=['POST'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def generate_report_api():
    data = request.get_json()
    scan_id = data.get('scan_id')
    final_diagnosis = data.get('doctor_final_diagnosis', '').strip()
    clinical_finding = data.get('clinical_finding', '').strip()
    impression = data.get('impression', '').strip()
    treatment = data.get('treatment_recommendations', '').strip()
    template_type = data.get('template_type', 'Detailed Report')

    if not scan_id or not final_diagnosis:
        return jsonify({'error': 'scan_id and doctor_final_diagnosis are required'}), 400

    try:
        report = generate_and_finalize_report(
            scan_id=scan_id,
            doctor_id=session['user_id'],
            doctor_final_diagnosis=final_diagnosis,
            clinical_finding=clinical_finding,
            impression=impression,
            treatment_recommendations=treatment,
            template_type=template_type
        )
        return jsonify({'message': 'Report finalized and PDF generated successfully', 'report': report.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': 'Report Generation Error', 'message': str(e)}), 500


@reports_bp.route('/api/reports', methods=['GET'])
@login_required
def list_reports():
    user_role = session.get('role_name')
    query = Report.query

    search_query = request.args.get('q', '').strip()
    if search_query:
        query = query.join(Report.patient).filter(
            (Patient.full_name.ilike(f"%{search_query}%")) |
            (Patient.unique_patient_id.ilike(f"%{search_query}%"))
        )

    if user_role == 'PATIENT':
        # Patient can only view reports for the explicitly selected patient profile.
        patient = Patient.query.get(session.get('patient_record_id'))
        if not patient:
            return jsonify({'reports': []}), 200
        query = query.filter_by(patient_id=patient.id)

    reports = query.order_by(Report.id.desc()).all()
    return jsonify({'reports': [r.to_dict() for r in reports]}), 200


@reports_bp.route('/api/reports/<int:report_id>/pdf', methods=['GET'])
@login_required
def download_report_pdf(report_id):
    report = Report.query.get_or_404(report_id)

    # Authorization Check for Patient
    if session.get('role_name') == 'PATIENT':
        patient = Patient.query.get(session.get('patient_record_id'))
        if not patient or report.patient_id != patient.id:
            return jsonify({'error': 'Forbidden', 'message': 'Access denied to this patient report'}), 403

    if not report.pdf_path or not os.path.exists(report.pdf_path):
        return jsonify({'error': 'PDF report file not found'}), 404

    log_audit_event(action='REPORT_DOWNLOADED', resource_type='Report', resource_id=report.id)
    return send_file(os.path.abspath(report.pdf_path), as_attachment=True, download_name=f"MediScan_Report_{report.report_uuid[:8]}.pdf")


@reports_bp.route('/api/reports/export', methods=['GET'])
@login_required
@roles_required('ADMIN', 'DOCTOR')
def export_reports():
    search_query = request.args.get('q', '').strip()
    patients_query = Patient.query.order_by(Patient.full_name.asc())
    if search_query:
        patients_query = patients_query.filter(
            (Patient.full_name.ilike(f"%{search_query}%")) |
            (Patient.unique_patient_id.ilike(f"%{search_query}%"))
        )
    patients = patients_query.all()

    log_audit_event(action='REPORTS_EXPORTED', resource_type='Report', resource_id='ALL')

    export_path = os.path.join(os.getcwd(), 'generated_reports', 'mediscan_patient_export.csv')
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, 'w', newline='', encoding='utf-8-sig') as export_file:
        cw = csv.writer(export_file)
        cw.writerow([
        'Report ID', 'Report UUID', 'Report Status', 'Report Created At', 'Report Finalized At',
        'Patient ID', 'Patient Name', 'Patient Email', 'Patient Phone', 'Date of Birth', 'Gender',
        'Blood Group', 'Address', 'Emergency Contact', 'Medical History', 'Allergies', 'Existing Conditions',
        'Scan ID', 'Scan Type', 'Body Part', 'Original Filename', 'Scan Status', 'Scan Uploaded At',
        'Symptoms', 'Symptom Duration Days', 'Blood Pressure', 'Diabetes', 'Hypertension',
        'Smoking Status', 'AI Prediction', 'AI Confidence', 'Model Version', 'Doctor Diagnosis', 'Risk Level'
        ])

        for patient in patients:
            patient_reports = patient.reports or []
            if not patient_reports:
                patient_reports = [None]

            for r in patient_reports:
                scan = r.scan if r else None
                clinical = scan.clinical_data if scan else None
                ai_result = scan.ai_result if scan else None
                cw.writerow([
                r.id if r else '',
                r.report_uuid if r else '',
                r.status if r else '',
                r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r and r.created_at else '',
                r.finalized_at.strftime('%Y-%m-%d %H:%M:%S') if r and r.finalized_at else '',
                patient.unique_patient_id,
                patient.full_name,
                patient.email or '',
                patient.phone or '',
                patient.dob.strftime('%Y-%m-%d') if patient.dob else '',
                patient.gender,
                patient.blood_group or '',
                patient.address or '',
                patient.emergency_contact or '',
                patient.medical_history or '',
                patient.allergies or '',
                patient.existing_conditions or '',
                scan.id if scan else '',
                scan.scan_type if scan else '',
                scan.body_part if scan else '',
                scan.original_filename if scan else '',
                scan.status if scan else '',
                scan.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if scan and scan.uploaded_at else '',
                clinical.symptoms if clinical else '',
                clinical.duration_days if clinical else '',
                clinical.blood_pressure if clinical else '',
                clinical.diabetes if clinical else '',
                clinical.hypertension if clinical else '',
                clinical.smoking_status if clinical else '',
                r.ai_prediction if r else '',
                ai_result.confidence_score if ai_result else '',
                ai_result.model_version if ai_result else '',
                r.doctor_final_diagnosis if r else '',
                r.risk_level if r else '',
                ])

    return send_file(
        export_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name='mediscan_patient_export.csv',
        max_age=0
    )
