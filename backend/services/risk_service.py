import json

def calculate_risk_stratification(primary_prediction, confidence_score, clinical_data):
    """
    Transparent Configurable Risk Scoring Framework:
    Combines:
    1. Predicted Condition Baseline Risk (0.0 - 1.0)
    2. AI Model Confidence Score
    3. Clinical Risk Factors (Age, Smoking, Hypertension, Diabetes, Symptom duration)
    4. Clinical Priority Rules
    Returns: LOW, MEDIUM, or HIGH risk classification with breakdown factors.
    """
    # 1. Condition Severity Weight
    condition_weights = {
        'Pneumonia': 0.70,
        'Tuberculosis': 0.85,
        'Pulmonary Embolism': 0.90,
        'Brain Tumor / Lesion': 0.95,
        'Ischemic Stroke': 0.90,
        'Lung Nodule': 0.65,
        'Normal': 0.10,
        'Normal CT': 0.10,
        'Normal MRI': 0.10,
    }
    
    base_weight = condition_weights.get(primary_prediction, 0.50)
    
    # 2. Clinical Risk Score Calculation
    clin_score = 0.0
    contributing_factors = []
    rule_evaluations = []

    if clinical_data:
        age = clinical_data.get('age', 0)
        if age > 65:
            clin_score += 0.15
            contributing_factors.append({'factor': 'Elderly Age Group (>65 yrs)', 'weight': '+0.15'})
            
        if clinical_data.get('diabetes'):
            clin_score += 0.10
            contributing_factors.append({'factor': 'Diabetes Mellitus', 'weight': '+0.10'})
            
        if clinical_data.get('hypertension'):
            clin_score += 0.10
            contributing_factors.append({'factor': 'Hypertension', 'weight': '+0.10'})
            
        smoking = str(clinical_data.get('smoking_status', '')).lower()
        if 'smoker' in smoking:
            clin_score += 0.15
            contributing_factors.append({'factor': f'Smoking History ({smoking})', 'weight': '+0.15'})
            
        duration = clinical_data.get('duration_days', 0) or 0
        if duration > 14:
            clin_score += 0.10
            contributing_factors.append({'factor': f'Prolonged Symptom Duration ({duration} days)', 'weight': '+0.10'})

    # 3. Rule Evaluation Matrix
    rule_evaluations.append({
        'rule': 'AI Primary Prediction Weight',
        'condition': primary_prediction,
        'assigned_weight': base_weight
    })
    
    rule_evaluations.append({
        'rule': 'AI Model Confidence Score',
        'score': round(confidence_score, 4),
        'weighted_impact': round(confidence_score * 0.3, 4)
    })

    # Combined Weighted Risk Score Formula
    total_risk_score = (base_weight * 0.5) + (confidence_score * 0.2) + (clin_score * 0.3)
    total_risk_score = min(max(total_risk_score, 0.0), 1.0)

    if total_risk_score >= 0.65 or primary_prediction in ['Pulmonary Embolism', 'Brain Tumor / Lesion', 'Ischemic Stroke']:
        risk_level = 'HIGH'
    elif total_risk_score >= 0.40:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    return {
        'risk_level': risk_level,
        'risk_score': round(total_risk_score, 2),
        'contributing_factors': contributing_factors,
        'rule_evaluations': rule_evaluations
    }
