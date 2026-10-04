from flask import Blueprint, request, jsonify, session
from backend.models import db
from backend.models.patient import Patient, PatientTimeline
from backend.models.scan import Scan
from backend.models.report import Report
from backend.models.ai_result import AIResult, ExplainabilityResult, RiskAssessment
from backend.utils.decorators import login_required

patient_bp = Blueprint('patient_bp', __name__)

def get_multilingual_explanations(diagnosis, scan_type):
    """
    Provides medical report explanations in multiple languages:
    English (en), Hindi (hi), Kannada (kn), Telugu (te), Tamil (ta).
    """
    diag_lower = str(diagnosis).lower()

    if 'pneumonia' in diag_lower:
        return {
            'en': "The scan shows areas of lung consolidation consistent with pneumonia (a chest infection). This can cause symptoms such as fever, cough, and shortness of breath. Please discuss the result with your doctor.",
            'hi': "स्कैन में निमोनिया (छाती में संक्रमण) से जुड़े लक्षण दिखाई दे रहे हैं। इसके कारण बुखार, खांसी और सांस लेने में तकलीफ हो सकती है। कृपया अपने डॉक्टर से परामर्श करें।",
            'kn': "ಸ್ಕ್ಯಾನ್ ನ್ಯುಮೋನಿಯಾ (ಎದೆ ಸೋಂಕು) ಗೆ ಸಂಬಂಧಿಸಿದ ಲಕ್ಷಣಗಳನ್ನು ತೋರಿಸುತ್ತದೆ. ಇದು ಜ್ವರ, ಕೆಮ್ಮು ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆಯನ್ನು ಉಂಟುಮಾಡಬಹುದು. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವೈದ್ಯರೊಂದಿಗೆ ಚರ್ಚಿಸಿ.",
            'te': "స్కాన్ న్యుమోనియా (ఛాతీ ఇన్ఫెక్షన్) కి సంబంధించిన సంకేతాలను చూపుతోంది. దీని వల్ల జ్వరం, దగ్గు మరియు శ్వాస తీసుకోవడంలో ఇబ్బంది కలగవచ్చు. దయచేసి మీ వైద్యుడిని సంప్రదించండి.",
            'ta': "ஸ்கேன் நிமோனியா (மார்பு தொற்று) தொடர்பான அறிகுறிகளைக் காட்டுகிறது. இது காய்ச்சல், இருமல் மற்றும் மூச்சுத்திணறலை ஏற்படுத்தக்கூடும். உங்கள் மருத்துவரிடம் கலந்தாலோசிக்கவும்."
        }
    elif 'tuberculosis' in diag_lower:
        return {
            'en': "The scan shows findings in the upper lung regions that may indicate tuberculosis infection. Please follow up with your healthcare provider for diagnostic confirmation and treatment guidance.",
            'hi': "स्कैन के ऊपरी फेफड़ों के हिस्से में क्षयरोग (टीबी) संक्रमण के संकेत दिखाई दे रहे हैं। कृपया पुष्टि और उपचार के लिए अपने डॉक्टर से संपर्क करें।",
            'kn': "ಉಸಿರಾಟದ ಮೇಲ್ಭಾಗದ ಶ್ವಾಸಕೋಶದಲ್ಲಿ ಕ್ಷಯರೋಗ (ಟಿಬಿ) ಸೋಂಕಿನ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ. ದಯವಿಟ್ಟು ಹೆಚ್ಚಿನ ವೈದ್ಯಕೀಯ ತಪಾಸಣೆಗಾಗಿ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ.",
            'te': "ఊపిరితిత్తుల ఎగువ భాగంలో క్షయవ్యాధి (టిబి) ఇన్ఫెక్షన్ సంకేతాలు కనిపించాయి. దయచేసి తదుపరి చికిత్స కోసం మీ వైద్యుడిని సంప్రదించండి.",
            'ta': "நுரையீரலின் மேல் பகுதியில் காசநோய் (காசநோய்) தொற்றின் அறிகுறிகள் காணப்படுகின்றன. தகுந்த சிகிச்சைக்காக மருத்துவரை அணுகவும்."
        }
    elif 'tumor' in diag_lower or 'lesion' in diag_lower:
        return {
            'en': "The scan highlights an area requiring further medical evaluation. Your specialist will discuss the image findings and recommended follow-up diagnostic steps with you.",
            'hi': "स्कैन में एक ऐसा क्षेत्र दिखाई दे रहा है जिसके लिए आगे की मेडिकल जांच की आवश्यकता है। आपके डॉक्टर आपके साथ रिपोर्ट और अगले चरणों पर चर्चा करेंगे।",
            'kn': "ಸ್ಕ್ಯಾನ್ ಹೆಚ್ಚಿನ ವೈದ್ಯಕೀಯ ತಪಾಸಣೆಯ ಅಗತ್ಯವಿರುವ ಪ್ರದೇಶವನ್ನು ತೋರಿಸುತ್ತದೆ. ನಿಮ್ಮ ವೈದ್ಯರು ಈ ಕುರಿತು ವಿವರಗಳನ್ನು ಚರ್ಚಿಸುತ್ತಾರೆ.",
            'te': "స్కాన్ తదుపరి వైద్య పరీక్షలు అవసరమైన ప్రాంతాన్ని చూపుతోంది. మీ వైద్యుడు తదుపరి చర్యల గురించి మీకు వివరిస్తారు.",
            'ta': "ஸ்கேன் மேலும் மருத்துவப் பரிசோதனை தேவைப்படும் பகுதியைக் காட்டுகிறது. உங்கள் மருத்துவர் இது குறித்து விளக்குவார்."
        }
    elif 'normal' in diag_lower:
        return {
            'en': f"The {scan_type} shows normal anatomical patterns with no major acute abnormalities detected by the system.",
            'hi': f"स्कैन में सामान्य शारीरिक संरचनाएं दिखाई दे रही हैं। कोई गंभीर असामान्यता नहीं पाई गई है।",
            'kn': f"ಸ್ಕ್ಯಾನ್ ಸಾಮಾನ್ಯ ಅಂಗರಚನಾ ಲಕ್ಷಣಗಳನ್ನು ತೋರಿಸುತ್ತದೆ. ಯಾವುದೇ ಪ್ರಮುಖ ತೊಂದರೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
            'te': f"స్కాన్ సాధారణ శరీర నిర్మాణాన్ని చూపుతోంది. ఎటువంటి తీవ్రమైన సమస్యలు కనిపించలేదు.",
            'ta': f"ஸ்கேன் இயல்பான உடற்கூறியல் அமைப்பைக் காட்டுகிறது. எந்தவொரு தீவிர பாதிப்பும் கண்டறியப்படவில்லை."
        }
    else:
        return {
            'en': f"The {scan_type} has been evaluated by the clinical team. Please consult your attending physician for detailed clinical interpretations of your report.",
            'hi': f"स्कैन का मूल्यांकन मेडिकल टीम द्वारा किया गया है। कृपया विस्तृत रिपोर्ट और सलाह के लिए अपने डॉक्टर से संपर्क करें।",
            'kn': f"ಸ್ಕ್ಯಾನ್ ಅನ್ನು ವೈದ್ಯಕೀಯ ತಂಡವು ಪರಿಶೀಲಿಸಿದೆ. ವಿವರವಾದ ವರದಿಗಾಗಿ ದಯವಿಟ್ಟು ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
            'te': f"స్కాన్ వైద్య బృందం ద్వారా పరిశీలించబడింది. వివరణాత్మక సలహా కోసం మీ వైద్యుడిని సంప్రదించండి.",
            'ta': f"ஸ்கேன் மருத்துவக் குழுவால் பரிசீலிக்கப்பட்டது. விரிவான தகவலுக்கு உங்கள் மருத்துவரை அணுகவும்."
        }


@patient_bp.route('/api/patient/portal', methods=['GET'])
@login_required
def get_patient_portal_data():
    patient = None
    patient_record_id = session.get('patient_record_id')
    if patient_record_id:
        patient = Patient.query.get(patient_record_id)

    if not patient and session.get('role_name') in ['ADMIN', 'DOCTOR']:
        patient = Patient.query.first()

    if not patient:
        return jsonify({
            'error': 'Patient record not linked to this user account',
            'message': 'No patient profile is linked to this login. Please ask an administrator to link the account.'
        }), 404

    if not patient:
        return jsonify({'error': 'No patient records found'}), 404

    scans = Scan.query.filter_by(patient_id=patient.id).order_by(Scan.id.desc()).all()
    reports = Report.query.filter_by(patient_id=patient.id).order_by(Report.id.desc()).all()
    timeline = PatientTimeline.query.filter_by(patient_id=patient.id).order_by(PatientTimeline.id.desc()).all()

    latest_report = reports[0] if reports else None
    latest_report_dict = None

    if latest_report:
        latest_report_dict = latest_report.to_dict()
        multilingual_explanations = get_multilingual_explanations(
            latest_report.doctor_final_diagnosis,
            latest_report.scan.scan_type if latest_report.scan else 'Scan'
        )
        latest_report_dict['multilingual_explanations'] = multilingual_explanations
        latest_report_dict['plain_english_explanation'] = multilingual_explanations['en']

    return jsonify({
        'patient': patient.to_dict(),
        'stats': {
            'total_reports': len(reports),
            'total_scans': len(scans),
            'latest_scan_date': scans[0].uploaded_at.strftime('%Y-%m-%d') if scans else 'N/A',
            'latest_status': latest_report.status if latest_report else 'NO_REPORTS'
        },
        'latest_report': latest_report_dict,
        'reports': [r.to_dict() for r in reports],
        'scans': [s.to_dict() for s in scans],
        'timeline': [t.to_dict() for t in timeline]
    }), 200
