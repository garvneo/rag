"""OpenAI-backed embedding provider."""

from collections.abc import Sequence

from openai import OpenAI


class OpenAIEmbedder:
    def __init__(self, client: OpenAI, model: str = "text-embedding-3-small") -> None:
        self.client = client
        self.model = model

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in response.data]
