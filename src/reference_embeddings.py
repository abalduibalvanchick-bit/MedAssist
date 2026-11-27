"""Смысловое ранжирование кандидатов через локальную модель Ollama."""

import json
from functools import lru_cache
from math import hypot, isfinite
from urllib.request import Request, urlopen


class OllamaRanker:
    """Сравнивает вопрос и найденные разделы в пространстве одной модели."""

    def __init__(self, model, endpoint="http://127.0.0.1:11434/api/embed"):
        self.model = model
        self.endpoint = endpoint
        self._cached = lru_cache(maxsize=128)(self._encode_batch)

    def _encode_batch(self, texts):
        request = Request(self.endpoint, data=json.dumps({"model": self.model, "input": texts}).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=60) as response:
            vectors = json.loads(response.read(4 * 1024 * 1024))["embeddings"]
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise ValueError("Модель вернула неверное число векторов.")
        normalized = []
        for vector in vectors:
            if not isinstance(vector, list) or not vector or not all(type(x) in (int, float) for x in vector):
                raise ValueError("Модель вернула некорректный вектор.")
            norm = hypot(*vector)
            if not norm or not isfinite(norm):
                raise ValueError("Невозможно нормировать вектор.")
            normalized.append(tuple(x / norm for x in vector))
        return tuple(normalized)

    def rank(self, query, candidates):
        query_vector, = self._encode_batch((query,))
        documents = tuple(f"{section.title}\n{section.heading}\n{section.text[:1600]}"
                          for _, section in candidates)
        scored = []
        for offset in range(0, len(documents), 8):
            vectors = self._cached(documents[offset:offset + 8])
            for (index, _), vector in zip(candidates[offset:], vectors):
                if len(vector) != len(query_vector):
                    raise ValueError("Размерности векторов не совпадают.")
                scored.append((sum(a * b for a, b in zip(query_vector, vector)), index))
        return [index for _, index in sorted(scored, key=lambda row: -row[0])]
