import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from app.api.ai_schema import PromptRequest
from app.api.form_schema import  FormSchemaCreate
from app.application.services.ai_service import AIService


router = APIRouter()

@router.post("/test-prompt")
async def test_ai_prompt(request: PromptRequest, ai_service: AIService = Depends(AIService)):
    response_text = await ai_service.generate_response(request.prompt)
    return {"response": response_text}

@router.post("/generate-form-from-text", response_model=FormSchemaCreate)
def generate_form_from_text(
        request: PromptRequest,
        ai_service: AIService = Depends(AIService)
):
    """
    Prima tekstualni upit, generiše FormSchema JSON pomoću AI
    i validira ga pre slanja.
    """
    # 1. Dobijamo JSON šemu našeg Pydantic modela
    global ai_response_str
    form_schema_definition = json.dumps(FormSchemaCreate.model_json_schema(), indent=2)

    # 2. Kreiramo detaljan "System Prompt"
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
        ai_response_str = ai_service.generate_json_from_prompt(
            system_prompt=system_prompt,
            user_prompt=request.prompt
        )

        ai_json = json.loads(ai_response_str)
        validated_schema = FormSchemaCreate(**ai_json)

        return validated_schema

    except json.JSONDecodeError:
        print("AI returned invalid JSON:", ai_response_str)
        raise HTTPException(status_code=500, detail="AI failed to generate valid JSON.")
    except ValidationError as e:
        print("AI JSON did not match schema:", e)
        raise HTTPException(status_code=500, detail="AI response did not match the required form schema.")
    except Exception as e:
        print("An unexpected error occurred:", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the AI request.")