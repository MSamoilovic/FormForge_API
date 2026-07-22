import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from app.api.ai_schema import PromptRequest
from app.api.deps import get_ai_service
from app.api.form_schema import FormSchemaCreate
from app.application.services.ai_service import AIService


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/test-prompt")
async def test_ai_prompt(
        request: PromptRequest,
        ai_service: AIService = Depends(get_ai_service)
):
    try:
        response_text = await ai_service.generate_response(request.prompt)
    except Exception:
        logger.exception("AI request failed")
        raise HTTPException(status_code=502, detail="Could not get a response from the AI model.")

    return {"response": response_text}


@router.post("/generate-form-from-text", response_model=FormSchemaCreate)
async def generate_form_from_text(
        request: PromptRequest,
        ai_service: AIService = Depends(get_ai_service)
):
    form_schema_definition = json.dumps(FormSchemaCreate.model_json_schema(), indent=2)

    system_prompt = f"""
    You are an expert assistant for creating web forms. Your task is to convert a user's text description into a valid JSON object that strictly follows the provided JSON schema.
    The JSON output MUST conform to this schema:
    {form_schema_definition}

    Key instructions:
    - The 'fields' array must contain objects, each with a unique 'id', a 'type', and a 'label'.
    - 'id' should be a short, descriptive, snake_case string (e.g., 'full_name', 'user_email').
    - 'type' must be one of the allowed values from the schema (e.g., 'text', 'select', 'checkbox').
    - For 'select' or 'radio' types, you MUST generate an 'options' array. Each option must have a 'label' (for the user) and a 'value' (for the system).
    - If the user implies a field is required (e.g., "I need their email"), add a 'required' validation rule.
    - Generate relevant validation rules where appropriate (e.g., a 'pattern' validation for email fields).
    - DO NOT include an 'id' at the root level of the JSON output. The output should be a single JSON object that can be directly parsed into a FormSchemaCreate model.
    """

    try:
        ai_response_str = await ai_service.generate_json_from_prompt(
            system_prompt=system_prompt,
            user_prompt=request.prompt
        )
    except Exception:
        logger.exception("AI request failed")
        raise HTTPException(status_code=502, detail="Could not get a response from the AI model.")

    try:
        return FormSchemaCreate(**json.loads(ai_response_str))
    except json.JSONDecodeError:
        logger.error("AI returned invalid JSON: %s", ai_response_str)
        raise HTTPException(status_code=502, detail="AI failed to generate valid JSON.")
    except ValidationError:
        logger.exception("AI JSON did not match schema")
        raise HTTPException(status_code=502, detail="AI response did not match the required form schema.")
