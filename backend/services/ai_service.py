import json
from backend.models import db
from backend.models.scan import Scan, ClinicalData
from backend.models.ai_result import AIResult, ExplainabilityResult, RiskAssessment
from backend.ai.preprocessing import preprocess_medical_image
from backend.ai.resnet_fusion import fusion_model
from backend.ai.explainability import generate_gradcam_heatmap, compute_lime_explanation, compute_shap_values
from backend.services.risk_service import calculate_risk_stratification
from backend.services.audit_service import log_audit_event

def run_ai_feature_fusion_pipeline(scan_id):
    """
    Executes the complete 10-step AI pipeline:
    1. Scan retrieval
    2. Preprocessing via OpenCV
    3. ResNet-50 Image feature extraction
    4. Clinical Context Vector encoding
    5. Feature-Level Fusion
    6. Classification & Softmax top-3 probabilities
    7. Confidence Score calculation
    8. Grad-CAM visual heatmap generation
    9. LIME & SHAP explainability analysis
    10. Risk Stratification framework evaluation
    """
    scan = Scan.query.get(scan_id)
    if not scan:
        raise ValueError(f"Scan ID {scan_id} not found.")

    # 1. Retrieve Clinical Data if recorded
    clin_data = ClinicalData.query.filter_by(scan_id=scan.id).first()
    clin_dict = clin_data.to_dict() if clin_data else {}

    # 2. Image Preprocessing
    norm_image_array, preprocessed_path = preprocess_medical_image(scan.image_path)
    scan.preprocessed_image_path = preprocessed_path
    
    # 3. Model Dual-Branch Fusion Prediction
    prediction_result = fusion_model.predict(
        preprocessed_image_array=norm_image_array,
        clinical_data=clin_dict,
        scan_type=scan.scan_type,
        body_part=scan.body_part
    )

    primary_pred = prediction_result['primary_prediction']
    confidence = prediction_result['confidence_score']
    top3_json = json.dumps(prediction_result['top3_predictions'])

    # 4. Save AI Result
    ai_res = AIResult.query.filter_by(scan_id=scan.id).first()
    if not ai_res:
        ai_res = AIResult(scan_id=scan.id, primary_prediction=primary_pred, confidence_score=confidence, top3_json=top3_json, model_version=fusion_model.model_version)
        db.session.add(ai_res)
    else:
        ai_res.primary_prediction = primary_pred
        ai_res.confidence_score = confidence
        ai_res.top3_json = top3_json
        ai_res.model_version = fusion_model.model_version
    db.session.commit()

    # 5. Explainability Pipeline (Grad-CAM, LIME, SHAP)
    gradcam_path = generate_gradcam_heatmap(scan.image_path, preprocessed_path)
    lime_dict = compute_lime_explanation(
        norm_image_array, clin_dict, primary_pred, scan.scan_type, scan.body_part
    )
    shap_dict = compute_shap_values(clin_dict, primary_pred)

    expl_summary = f"Grad-CAM overlay highlights primary lesion focus. SHAP analysis highlights top clinical risk features."

    expl_res = ExplainabilityResult.query.filter_by(ai_result_id=ai_res.id).first()
    if not expl_res:
        expl_res = ExplainabilityResult(
            ai_result_id=ai_res.id,
            gradcam_heatmap_path=gradcam_path,
            lime_explanation_json=json.dumps(lime_dict),
            shap_values_json=json.dumps(shap_dict),
            summary_text=expl_summary
        )
        db.session.add(expl_res)
    else:
        expl_res.gradcam_heatmap_path = gradcam_path
        expl_res.lime_explanation_json = json.dumps(lime_dict)
        expl_res.shap_values_json = json.dumps(shap_dict)
        expl_res.summary_text = expl_summary
    db.session.commit()

    # 6. Risk Stratification Framework Evaluation
    risk_dict = calculate_risk_stratification(primary_pred, confidence, clin_dict)
    
    risk_res = RiskAssessment.query.filter_by(ai_result_id=ai_res.id).first()
    if not risk_res:
        risk_res = RiskAssessment(
            ai_result_id=ai_res.id,
            risk_level=risk_dict['risk_level'],
            risk_score=risk_dict['risk_score'],
            contributing_factors_json=json.dumps(risk_dict['contributing_factors']),
            rule_evaluations_json=json.dumps(risk_dict['rule_evaluations'])
        )
        db.session.add(risk_res)
    else:
        risk_res.risk_level = risk_dict['risk_level']
        risk_res.risk_score = risk_dict['risk_score']
        risk_res.contributing_factors_json = json.dumps(risk_dict['contributing_factors'])
        risk_res.rule_evaluations_json = json.dumps(risk_dict['rule_evaluations'])
        
    scan.status = 'ANALYZED'
    db.session.commit()

    log_audit_event(action='AI_ANALYSIS_COMPLETED', resource_type='Scan', resource_id=scan.id)
    return ai_res
