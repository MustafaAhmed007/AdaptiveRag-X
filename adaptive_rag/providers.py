from .models import Evidence


class MockGenerator:
    def generate(self, query: str, evidence: list[Evidence]) -> str:
        if not evidence:
            return "I do not have enough evidence in the indexed knowledge to answer that reliably."
        return "Based on the retrieved evidence:\n\n" + "\n".join(
            f"- {item.text}" for item in evidence[:3]
        )


class ProviderGenerator:
    """OpenAI-compatible Responses API generator behind an injectable client."""

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
