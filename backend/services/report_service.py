import os
import uuid
from datetime import datetime
from backend.models import db
from backend.models.scan import Scan, ClinicalData
from backend.models.patient import Patient, PatientTimeline
from backend.models.ai_result import AIResult, ExplainabilityResult, RiskAssessment
from backend.models.report import Report, DoctorNote
from backend.models.audit import Notification
from backend.utils.qr_generator import generate_report_qr_code
from backend.utils.pdf_generator import generate_medical_report_pdf
from backend.services.audit_service import log_audit_event

def generate_and_finalize_report(scan_id, doctor_id, doctor_final_diagnosis, clinical_finding="", impression="", treatment_recommendations="", template_type="Detailed Report"):
    """
    Finalizes Doctor Diagnosis and compiles production PDF report with QR code.
    """
    scan = Scan.query.get(scan_id)
    if not scan:
        raise ValueError(f"Scan ID {scan_id} not found.")

    patient = Patient.query.get(scan.patient_id)
    ai_result = AIResult.query.filter_by(scan_id=scan.id).first()
    explainability = ExplainabilityResult.query.filter_by(ai_result_id=ai_result.id).first() if ai_result else None
    risk_assessment = RiskAssessment.query.filter_by(ai_result_id=ai_result.id).first() if ai_result else None
    clinical_data = ClinicalData.query.filter_by(scan_id=scan.id).first()

    # 1. Record Doctor Note
    doc_note = DoctorNote.query.filter_by(scan_id=scan.id, doctor_id=doctor_id).first()
    if not doc_note:
        doc_note = DoctorNote(
            scan_id=scan.id,
            doctor_id=doctor_id,
            clinical_finding=clinical_finding,
            impression=impression,
            final_diagnosis=doctor_final_diagnosis,
            treatment_recommendations=treatment_recommendations
        )
        db.session.add(doc_note)
    else:
        doc_note.clinical_finding = clinical_finding
        doc_note.impression = impression
        doc_note.final_diagnosis = doctor_final_diagnosis
        doc_note.treatment_recommendations = treatment_recommendations
    db.session.commit()

    # 2. Check/Create Report
    report = Report.query.filter_by(scan_id=scan.id).first()
    report_uuid = report.report_uuid if report else str(uuid.uuid4())
    
    # 3. Generate Verification QR Code
    qr_rel_path = generate_report_qr_code(report_uuid)
    
    # 4. Prepare Report Context Data Dictionary
    pdf_filename = f"report_{patient.unique_patient_id}_{report_uuid[:8]}.pdf"
    pdf_rel_path = f"generated_reports/{pdf_filename}"
    pdf_abs_path = os.path.join(os.getcwd(), 'generated_reports', pdf_filename)

    report_context = {
        'report_uuid': report_uuid,
        'patient_name': patient.full_name,
        'patient_unique_id': patient.unique_patient_id,
        'age': clinical_data.age if clinical_data else 'N/A',
        'gender': clinical_data.gender if clinical_data else 'N/A',
        'blood_group': patient.blood_group or 'N/A',
        'scan_type': scan.scan_type,
        'doctor_name': doc_note.doctor.full_name if hasattr(doc_note, 'doctor') and doc_note.doctor else 'Attending Physician',
        'template_type': template_type,
        'symptoms': clinical_data.symptoms if clinical_data else 'N/A',
        'blood_pressure': clinical_data.blood_pressure if clinical_data else 'N/A',
        'diabetes': clinical_data.diabetes if clinical_data else False,
        'hypertension': clinical_data.hypertension if clinical_data else False,
        'smoking_status': clinical_data.smoking_status if clinical_data else 'N/A',
        'ai_prediction': ai_result.primary_prediction if ai_result else 'N/A',
        'confidence_percentage': f"{round(ai_result.confidence_score*100,1)}%" if ai_result else 'N/A',
        'risk_level': risk_assessment.risk_level if risk_assessment else 'LOW',
        'image_path': scan.preprocessed_image_path or scan.image_path,
        'gradcam_heatmap_path': explainability.gradcam_heatmap_path if explainability else None,
        'doctor_final_diagnosis': doctor_final_diagnosis,
        'clinical_finding': clinical_finding,
        'treatment_recommendations': treatment_recommendations,
        'qr_code_path': os.path.join(os.getcwd(), qr_rel_path),
        'status': 'FINALIZED'
    }

    # 5. Build PDF File
    generate_medical_report_pdf(report_context, pdf_abs_path)

    # 6. Save Report Record in DB
    if not report:
        report = Report(
            report_uuid=report_uuid,
            scan_id=scan.id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            template_type=template_type,
            ai_prediction=ai_result.primary_prediction if ai_result else 'N/A',
            doctor_final_diagnosis=doctor_final_diagnosis,
            risk_level=risk_assessment.risk_level if risk_assessment else 'LOW',
            pdf_path=pdf_rel_path,
            qr_code_path=qr_rel_path,
            status='FINALIZED',
            finalized_at=datetime.utcnow()
        )
        db.session.add(report)
    else:
        report.template_type = template_type
        report.doctor_final_diagnosis = doctor_final_diagnosis
        report.risk_level = risk_assessment.risk_level if risk_assessment else 'LOW'
        report.pdf_path = pdf_rel_path
        report.qr_code_path = qr_rel_path
        report.status = 'FINALIZED'
        report.finalized_at = datetime.utcnow()
        
    scan.status = 'FINALIZED'
    db.session.commit()

    # 7. Add Patient Timeline Event
    timeline_event = PatientTimeline(
        patient_id=patient.id,
        event_type='REPORT_FINALIZED',
        title=f"{scan.scan_type} Medical Report Finalized",
        description=f"Dr. {doc_note.doctor.full_name if hasattr(doc_note, 'doctor') and doc_note.doctor else ''} finalized diagnosis: {doctor_final_diagnosis}",
        reference_id=report.id
    )
    db.session.add(timeline_event)

    log_audit_event(action='REPORT_FINALIZED', resource_type='Report', resource_id=report.id, user_id=doctor_id)
    return report
