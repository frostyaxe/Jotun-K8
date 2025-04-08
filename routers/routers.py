from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from fastapi import Request
from customizer.customize import Customizer

router = APIRouter()

def get_models(request: Request) -> Dict[str, object]:
    return request.app.state.models

@router.post("/predict/{model_name}")
async def predict(model_name: str, request: Dict, models: Dict[str, object] = Depends(get_models)):
    customize = Customizer()
    isValidationSuccess = customize.validate(model_name)
    if not isValidationSuccess:
        raise HTTPException(400, f"Validation failed for the current model {model_name}")
    model = models[model_name]
    request_dict = customize.get_model_instance(model_name, request)
    input_validation_errors = customize.validate_features(model_name, model, request_dict)
    if input_validation_errors:
        return {"status": "failure", "message": "Validation failed for the inputs", "errors": input_validation_errors}
    prediction = model.predict(customize.get_prediction_features(model_name, request_dict))
    return {"status": "success", "message": "Predicted the result successfully", "result" : customize.get_processed_result(model_name, prediction)}


