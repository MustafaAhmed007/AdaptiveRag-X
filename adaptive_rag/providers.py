from .config import settings
from .models import Evidence


class MockGenerator:
    def generate(self, query: str, evidence: list[Evidence]) -> str:
        if not evidence:
            return "I do not have enough evidence in the indexed knowledge to answer that reliably."
        return "Based on the retrieved evidence:\n\n" + "\n".join(
            f"- {item.text}" for item in evidence[:3]
        )


class ProviderGenerator:
    """OpenAI Responses API generator behind an injected client."""

    def __init__(self, client, model: str = "gpt-4.1-mini"):
        self.client = client
        self.model = model

    def generate(self, query: str, evidence: list[Evidence]) -> str:
        context = "\n\n".join(item.text for item in evidence)
        response = self.client.responses.create(
            model=self.model,
            input=(
                "You are a grounded RAG assistant. Answer only from the supplied evidence. "
                "If evidence is insufficient, say so. Do not invent facts.\n\n"
                f"Question: {query}\n\nEvidence:\n{context}"
            ),
        )
        return response.output_text


def build_generator():
    if settings.llm_provider.lower() == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        from openai import OpenAI

        return ProviderGenerator(OpenAI(api_key=settings.openai_api_key), settings.llm_model)
    return MockGenerator()
