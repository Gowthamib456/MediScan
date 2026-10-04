import pytest
import numpy as np
from backend.ai.resnet_fusion import fusion_model
from backend.ai.preprocessing import preprocess_medical_image
from backend.ai.explainability import compute_lime_explanation

def test_encode_clinical_context():
    clin_dict = {
        'age': 68,
        'gender': 'Male',
        'diabetes': True,
        'hypertension': True,
        'smoking_status': 'Current Smoker',
        'symptoms': 'Fever and severe cough',
        'duration_days': 7
    }
    vec = fusion_model.encode_clinical_context(clin_dict)
    assert len(vec) == 16
    assert abs(vec[0] - 0.68) < 1e-4  # Normalized age
    assert vec[2] == 1.0   # Diabetes
    assert vec[3] == 1.0   # Hypertension
    assert vec[4] == 1.0   # Active Smoker

def test_fusion_prediction():
    dummy_img = np.ones((224, 224, 3), dtype=np.float32)
    clin_dict = {'age': 50, 'symptoms': 'cough'}
    res = fusion_model.predict(dummy_img, clin_dict, scan_type='Chest X-ray')
    
    assert 'primary_prediction' in res
    assert 'confidence_score' in res
    assert len(res['top3_predictions']) == 3
    assert res['confidence_score'] > 0.0

def test_fusion_prediction_uses_body_region():
    dummy_img = np.ones((224, 224, 3), dtype=np.float32)
    clin_dict = {'age': 50, 'symptoms': 'routine'}

    brain_result = fusion_model.predict(dummy_img, clin_dict, scan_type='MRI', body_part='Brain')
    abdomen_result = fusion_model.predict(dummy_img, clin_dict, scan_type='CT Scan', body_part='Abdomen')

    assert brain_result['body_region'] == 'brain'
    assert abdomen_result['body_region'] == 'abdomen'
    assert brain_result['primary_prediction'] != abdomen_result['primary_prediction']

def test_lime_explanation_uses_image_regions():
    dummy_img = np.ones((224, 224, 3), dtype=np.float32)
    clinical_data = {'age': 50, 'symptoms': 'headache'}
    prediction = fusion_model.predict(dummy_img, clinical_data, scan_type='MRI', body_part='Brain')

    explanation = compute_lime_explanation(
        dummy_img, clinical_data, prediction['primary_prediction'], 'MRI', 'Brain'
    )

    assert explanation['target_class'] == prediction['primary_prediction']
    assert explanation['important_regions']
    assert len(explanation['important_regions']) <= 5
    assert all('row ' in region['region'] and 'column ' in region['region'] for region in explanation['important_regions'])
