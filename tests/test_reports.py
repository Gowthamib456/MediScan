import os
from backend.utils.qr_generator import generate_report_qr_code
from backend.utils.pdf_generator import generate_medical_report_pdf

def test_qr_generation(tmp_path):
    uuid_str = "test-report-uuid-12345"
    rel_path = generate_report_qr_code(uuid_str)
    assert os.path.exists(rel_path)

def test_pdf_report_compilation(tmp_path):
    output_pdf = str(tmp_path / "test_report.pdf")
    data = {
        'report_uuid': 'test-uuid-999',
        'patient_name': 'Test Patient',
        'patient_unique_id': 'PAT-TEST-001',
        'age': 45,
        'gender': 'Male',
        'blood_group': 'A+',
        'scan_type': 'Chest X-ray',
        'doctor_name': 'Dr. Test',
        'symptoms': 'Fever and shortness of breath',
        'ai_prediction': 'Pneumonia',
        'confidence_percentage': '94.2%',
        'risk_level': 'HIGH',
        'doctor_final_diagnosis': 'Right Lower Lobe Pneumonia',
        'clinical_finding': ' Patchy opacity',
        'treatment_recommendations': 'Antibiotic course'
    }
    path = generate_medical_report_pdf(data, output_pdf)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

def test_report_export_contains_complete_patient_columns(client):
    login = client.post('/api/auth/login', json={
        'email': 'doctor@mediscan.org',
        'password': 'Doctor123!'
    })
    assert login.status_code == 200

    response = client.get('/api/reports/export?format=csv')
    assert response.status_code == 200
    header = response.get_data(as_text=True).splitlines()[0]
    assert 'Patient Email' in header
    assert 'Body Part' in header
    assert 'Symptoms' in header
    assert 'AI Confidence' in header
