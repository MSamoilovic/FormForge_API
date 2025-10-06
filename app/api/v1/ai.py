from fastapi import APIRouter, Depends

from app.api.ai_schema import PromptRequest
from app.application.services.ai_service import AIService


router = APIRouter()

@router.post("test-prompt")
async def test_ai_prompt(request: PromptRequest, ai_service: AIService = Depends(AIService)):
    response_text = await ai_service.generate_response(request.prompt)
    return {"response": response_text}