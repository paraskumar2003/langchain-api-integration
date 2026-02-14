"""
Test script to verify the question evaluation endpoint with new HR analysis fields.
This script tests the get_question_evaluation function directly without running the server.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.index import QuestionModel
from app.service.index import get_question_evaluation
import json

# Test payload from user
test_question_data = {
    "dimension": "visual",
    "level": "basic",
    "type": "text",
    "prompt_html": "What are you seeing in this image? Explain strategically",
    "image_url": "https://almondvirtex.s3.ap-south-1.amazonaws.com/mtn%2Bdevelopment/questions/advance_2.png",
    "audio_url": None,
    "options": [],
    "response_type": "text",
    "response_file_url": "",
    "response_text": "This is a musical note."
}

print("=" * 80)
print("Testing Question Evaluation with HR Analysis Fields")
print("=" * 80)
print("\nTest Question Data:")
print(json.dumps(test_question_data, indent=2))
print("\n" + "=" * 80)

try:
    # Create QuestionModel instance
    question = QuestionModel(**test_question_data)
    
    print("\n✓ Question model validated successfully")
    print("\nCalling get_question_evaluation()...")
    print("-" * 80)
    
    # Call the evaluation function
    result = get_question_evaluation(question)
    
    print("\n✓ Evaluation completed successfully!")
    print("\n" + "=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 80)
    
    # Verify all expected fields are present
    expected_fields = [
        "confidence",
        "is_correct",
        "reason",
        "visual",
        "auditory",
        "rhythmic",
        "subconscious",
        "candidates_approach",
        "demonstrated_strengths",
        "omissions_or_delays",
        "hr_interpretation"
    ]
    
    print("\n" + "=" * 80)
    print("FIELD VERIFICATION:")
    print("=" * 80)
    
    all_present = True
    for field in expected_fields:
        if field in result:
            print(f"✓ {field}: Present")
        else:
            print(f"✗ {field}: MISSING")
            all_present = False
    
    print("=" * 80)
    
    if all_present:
        print("\n✅ SUCCESS: All expected fields are present in the response!")
    else:
        print("\n❌ FAILURE: Some fields are missing!")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
