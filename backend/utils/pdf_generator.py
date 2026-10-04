import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_medical_report_pdf(report_data, output_path):
    """
    Generates a production-quality medical PDF report based on selected template style:
    1. 'Radiology-Style Report (Standard Format)'
    2. 'Detailed Report (Full AI & Explainability)'
    3. 'Summary Report (Executive Brief)'
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    template_type = report_data.get('template_type', 'Detailed Report')
    
    # Common Base Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=8,
        spaceAfter=4
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )

    elements = []

    # Risk level color calculation
    risk_level = str(report_data.get('risk_level', 'LOW')).upper()
    risk_color = '#10B981' if risk_level == 'LOW' else ('#F59E0B' if risk_level == 'MEDIUM' else '#EF4444')

    # Branching based on Template Style
    if 'Radiology' in template_type or 'Standard' in template_type:
        # ==========================================
        # TEMPLATE 1: RADIOLOGY-STYLE REPORT (STANDARD)
        # ==========================================
        elements.append(Paragraph("DEPARTMENT OF RADIOLOGY & IMAGING", title_style))
        elements.append(Paragraph(f"Standard Clinical Diagnostic Report | UUID: {report_data['report_uuid']}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=10))

        # Patient Info Table
        info_data = [
            [
                Paragraph("<b>Patient Name:</b> " + str(report_data.get('patient_name', '')), normal_style),
                Paragraph("<b>Patient ID:</b> " + str(report_data.get('patient_unique_id', '')), normal_style)
            ],
            [
                Paragraph("<b>Age / Gender:</b> " + f"{report_data.get('age', 'N/A')} yrs / {report_data.get('gender', 'N/A')}", normal_style),
                Paragraph("<b>Blood Group:</b> " + str(report_data.get('blood_group', 'N/A')), normal_style)
            ],
            [
                Paragraph("<b>Procedure / Scan:</b> " + str(report_data.get('scan_type', '')), normal_style),
                Paragraph("<b>Date of Report:</b> " + datetime.utcnow().strftime('%Y-%m-%d'), normal_style)
            ],
            [
                Paragraph("<b>Attending Radiologist:</b> " + str(report_data.get('doctor_name', 'Dr. System')), normal_style),
                Paragraph("<b>Format:</b> Standard Radiology Report", normal_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[3.5 * inch, 3.5 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 10))

        # Clinical Context
        elements.append(Paragraph("CLINICAL HISTORY & INDICATIONS", heading_style))
        history_text = f"Patient presents with: {report_data.get('symptoms', 'Standard radiological check')}. Vitals: BP {report_data.get('blood_pressure', 'N/A')}, Diabetes: {'Yes' if report_data.get('diabetes') else 'No'}, Smoking: {report_data.get('smoking_status', 'N/A')}."
        elements.append(Paragraph(history_text, normal_style))
        elements.append(Spacer(1, 10))

        # Image Thumbnail
        elements.append(Paragraph("RADIOLOGICAL IMAGING", heading_style))
        scan_img_path = report_data.get('image_path')
        if scan_img_path and os.path.exists(scan_img_path):
            try:
                img_table = Table([[Image(scan_img_path, width=2.8*inch, height=2.8*inch)]], colWidths=[7*inch])
                img_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
                elements.append(img_table)
            except Exception:
                elements.append(Paragraph("Scan image attached in medical file.", normal_style))
        else:
            elements.append(Paragraph("Medical scan attached on DICOM PACS server.", normal_style))
        elements.append(Spacer(1, 10))

        # Radiological Findings & Impression
        elements.append(Paragraph("FINDINGS & IMPRESSION", heading_style))
        findings_data = [
            [Paragraph("<b>Radiological Findings:</b><br/>" + str(report_data.get('clinical_finding', 'No acute abnormality noted.')), normal_style)],
            [Paragraph("<b>Final Diagnosis / Impression:</b><br/>" + str(report_data.get('doctor_final_diagnosis', 'Confirmed normal study.')), normal_style)],
            [Paragraph("<b>Recommendations:</b><br/>" + str(report_data.get('treatment_recommendations', 'Clinical correlation recommended.')), normal_style)]
        ]
        f_table = Table(findings_data, colWidths=[7 * inch])
        f_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(f_table)
        elements.append(Spacer(1, 15))

        # Signature & Verification
        qr_img_path = report_data.get('qr_code_path')
        qr_elem = Paragraph("<b>Scan QR</b>", normal_style)
        if qr_img_path and os.path.exists(qr_img_path):
            try: qr_elem = Image(qr_img_path, width=0.9*inch, height=0.9*inch)
            except Exception: pass

        sig_table = Table([
            [qr_elem, Paragraph(f"<b>Digitally Verified By:</b> {report_data.get('doctor_name', 'Radiologist')}<br/><b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d')}<br/><b>Verification ID:</b> {report_data['report_uuid'][:16]}", normal_style)]
        ], colWidths=[1.2*inch, 5.8*inch])
        sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(sig_table)

    elif 'Executive' in template_type or 'Summary' in template_type:
        # ==========================================
        # TEMPLATE 2: SUMMARY REPORT (EXECUTIVE BRIEF)
        # ==========================================
        elements.append(Paragraph("EXECUTIVE MEDICAL SUMMARY BRIEF", title_style))
        elements.append(Paragraph(f"High-Level Clinical Brief & Action Plan | ID: {report_data['report_uuid'][:12]}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=12))

        # Executive Card (Diagnosis & Risk Level)
        exec_card = [
            [
                Paragraph(f"<b>PATIENT:</b> {report_data.get('patient_name')} ({report_data.get('patient_unique_id')})", normal_style),
                Paragraph(f"<b>ASSESSED RISK:</b> <font color='{risk_color}'><b>{risk_level}</b></font>", normal_style)
            ],
            [
                Paragraph(f"<b>CONFIRMED DIAGNOSIS:</b> <b>{report_data.get('doctor_final_diagnosis')}</b>", normal_style),
                Paragraph(f"<b>AI PREDICTION:</b> {report_data.get('ai_prediction')} ({report_data.get('confidence_percentage')})", normal_style)
            ]
        ]
        exec_table = Table(exec_card, colWidths=[3.5 * inch, 3.5 * inch])
        exec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#3B82F6')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(exec_table)
        elements.append(Spacer(1, 12))

        # Key Findings & Treatment Summary
        elements.append(Paragraph("1. Clinical Context & Vitals", heading_style))
        elements.append(Paragraph(f"Age: {report_data.get('age')} | Gender: {report_data.get('gender')} | Symptoms: {report_data.get('symptoms')} | Blood Pressure: {report_data.get('blood_pressure')}", normal_style))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("2. Executive Impression & Doctor Action Plan", heading_style))
        plan_data = [
            [Paragraph("<b>Clinical Impression:</b> " + str(report_data.get('clinical_finding', 'N/A')), normal_style)],
            [Paragraph("<b>Recommended Action Plan:</b> " + str(report_data.get('treatment_recommendations', 'N/A')), normal_style)]
        ]
        plan_table = Table(plan_data, colWidths=[7 * inch])
        plan_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(plan_table)
        elements.append(Spacer(1, 12))

        # Compact Scan & QR Verification
        img_cells = []
        scan_img_path = report_data.get('image_path')
        if scan_img_path and os.path.exists(scan_img_path):
            try: img_cells.append(Image(scan_img_path, width=2.0*inch, height=2.0*inch))
            except Exception: img_cells.append(Paragraph("Scan attached", normal_style))
        else:
            img_cells.append(Paragraph("Scan image attached", normal_style))

        qr_img_path = report_data.get('qr_code_path')
        if qr_img_path and os.path.exists(qr_img_path):
            try: img_cells.append(Image(qr_img_path, width=1.2*inch, height=1.2*inch))
            except Exception: img_cells.append(Paragraph("QR Verification", normal_style))
        else:
            img_cells.append(Paragraph("QR Verification", normal_style))

        summary_footer_table = Table([
            [img_cells[0], img_cells[1] if len(img_cells)>1 else Paragraph("", normal_style),
             Paragraph(f"<b>Finalized By:</b> {report_data.get('doctor_name')}<br/><b>Status:</b> FINALIZED<br/><b>Token:</b> {report_data['report_uuid'][:12]}", normal_style)]
        ], colWidths=[2.2*inch, 1.5*inch, 3.3*inch])
        summary_footer_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(summary_footer_table)

    else:
        # ==========================================
        # TEMPLATE 3: DETAILED REPORT (FULL AI & EXPLAINABILITY)
        # ==========================================
        elements.append(Paragraph("MediScan Clinical Decision Support System", title_style))
        elements.append(Paragraph(f"Official AI-Integrated Radiology & Clinical Context Report | UUID: {report_data['report_uuid']}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=12))

        # Patient Info Table
        info_data = [
            [
                Paragraph("<b>Patient Name:</b> " + str(report_data.get('patient_name', '')), normal_style),
                Paragraph("<b>Patient ID:</b> " + str(report_data.get('patient_unique_id', '')), normal_style)
            ],
            [
                Paragraph("<b>Age / Gender:</b> " + f"{report_data.get('age', 'N/A')} yrs / {report_data.get('gender', 'N/A')}", normal_style),
                Paragraph("<b>Blood Group:</b> " + str(report_data.get('blood_group', 'N/A')), normal_style)
            ],
            [
                Paragraph("<b>Scan Type:</b> " + str(report_data.get('scan_type', '')), normal_style),
                Paragraph("<b>Date of Report:</b> " + datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'), normal_style)
            ],
            [
                Paragraph("<b>Attending Doctor:</b> " + str(report_data.get('doctor_name', 'Dr. System')), normal_style),
                Paragraph("<b>Template:</b> Detailed Report (Full AI & Explainability)", normal_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[3.5 * inch, 3.5 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 10))

        # Clinical Context Section
        elements.append(Paragraph("1. Clinical Context & Vitals Integration", heading_style))
        clin_data = [
            [Paragraph("<b>Symptoms:</b> " + str(report_data.get('symptoms', 'None reported')), normal_style)],
            [Paragraph("<b>Vitals & Risk Factors:</b> Blood Pressure: " + str(report_data.get('blood_pressure', 'N/A')) + 
                       " | Diabetes: " + ("Yes" if report_data.get('diabetes') else "No") +
                       " | Hypertension: " + ("Yes" if report_data.get('hypertension') else "No") +
                       " | Smoking: " + str(report_data.get('smoking_status', 'Non-Smoker')), normal_style)]
        ]
        clin_table = Table(clin_data, colWidths=[7 * inch])
        clin_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(clin_table)
        elements.append(Spacer(1, 10))

        # AI Feature Fusion & Analysis Results
        elements.append(Paragraph("2. AI Feature Fusion & Neural Network Predictions", heading_style))
        
        ai_summary_data = [
            [
                Paragraph("<b>Primary AI Prediction:</b> " + str(report_data.get('ai_prediction', 'N/A')), normal_style),
                Paragraph("<b>Model Confidence:</b> " + str(report_data.get('confidence_percentage', 'N/A')), normal_style)
            ],
            [
                Paragraph(f"<b>Assessed Risk Level:</b> <font color='{risk_color}'><b>{risk_level}</b></font>", normal_style),
                Paragraph("<b>Model Architecture:</b> ResNet-50 + Clinical MLP Fusion", normal_style)
            ]
        ]
        ai_table = Table(ai_summary_data, colWidths=[3.5 * inch, 3.5 * inch])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(ai_table)
        elements.append(Spacer(1, 10))

        # Medical Scan Image & Explainability Heatmap
        elements.append(Paragraph("3. Radiological Scan & Grad-CAM Explainability Attention Map", heading_style))
        img_cells = []
        
        scan_img_path = report_data.get('image_path')
        if scan_img_path and os.path.exists(scan_img_path):
            try: img_cells.append(Image(scan_img_path, width=2.3*inch, height=2.3*inch))
            except Exception: img_cells.append(Paragraph("Scan Image Attached", normal_style))
        else:
            img_cells.append(Paragraph("Medical Scan Image", normal_style))
            
        heatmap_path = report_data.get('gradcam_heatmap_path')
        if heatmap_path and os.path.exists(heatmap_path):
            try: img_cells.append(Image(heatmap_path, width=2.3*inch, height=2.3*inch))
            except Exception: img_cells.append(Paragraph("Grad-CAM Heatmap Attached", normal_style))
        else:
            img_cells.append(Paragraph("Grad-CAM AI Attention Overlay", normal_style))
            
        img_table = Table([img_cells], colWidths=[3.5 * inch, 3.5 * inch])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(img_table)
        elements.append(Spacer(1, 10))

        # Doctor Assessment Section
        elements.append(Paragraph("4. Doctor's Final Clinical Assessment & Diagnosis", heading_style))
        doc_data = [
            [Paragraph("<b>Final Diagnosis:</b> " + str(report_data.get('doctor_final_diagnosis', 'Pending Doctor Confirmation')), normal_style)],
            [Paragraph("<b>Clinical Findings & Impression:</b> " + str(report_data.get('clinical_finding', 'Standard radiological assessment completed.')), normal_style)],
            [Paragraph("<b>Treatment & Recommendations:</b> " + str(report_data.get('treatment_recommendations', 'Follow-up as clinically indicated.')), normal_style)]
        ]
        doc_table = Table(doc_data, colWidths=[7 * inch])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(doc_table)
        elements.append(Spacer(1, 10))

        # Verification QR Code & Signature Section
        qr_img_path = report_data.get('qr_code_path')
        qr_element = Paragraph("<b>Scan to Verify Report</b>", normal_style)
        if qr_img_path and os.path.exists(qr_img_path):
            try: qr_element = Image(qr_img_path, width=0.9*inch, height=0.9*inch)
            except Exception: pass

        footer_table = Table([
            [
                qr_element,
                Paragraph(f"<b>Finalized By:</b> {report_data.get('doctor_name', 'Authorized Doctor')}<br/>"
                          f"<b>Status:</b> {report_data.get('status', 'FINALIZED')}<br/>"
                          f"<b>Digital Verification Token:</b> {report_data.get('report_uuid')[:16]}...", normal_style)
            ]
        ], colWidths=[1.3 * inch, 5.7 * inch])
        footer_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(footer_table)

    # Global Medical Safety Disclaimer
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceAfter=4))
    elements.append(Paragraph(
        "<b>MEDICAL SAFETY DISCLAIMER:</b> MediScan provides AI-assisted clinical decision support and does NOT replace professional medical judgment. "
        "All predictions and risk classifications are meant for qualified healthcare provider review only.",
        disclaimer_style
    ))

    doc.build(elements)
    return output_path
