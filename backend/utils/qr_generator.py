import os
import qrcode

def generate_report_qr_code(report_uuid, base_url="http://localhost:5000"):
    """
    Generates a secure QR code image containing a report verification URL.
    Does NOT store sensitive medical data directly inside the QR code.
    """
    verification_url = f"{base_url}/verify-report/{report_uuid}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    
    qr_dir = os.path.join(os.getcwd(), 'generated_reports', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    qr_filename = f"qr_{report_uuid}.png"
    filepath = os.path.join(qr_dir, qr_filename)
    img.save(filepath)
    
    return f"generated_reports/qr_codes/{qr_filename}"
