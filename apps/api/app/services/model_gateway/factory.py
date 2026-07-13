from app.core.config import settings
from app.services.model_gateway.openai_compatible import OpenAICompatibleGateway
from app.services.model_gateway.types import ModelGateway


def get_model_gateway() -> ModelGateway:
    if settings.model_provider == "openai_compatible":
        return OpenAICompatibleGateway()
    raise ValueError(f"Unsupported model provider: {settings.model_provider}")
