"""Разреженный TF–IDF по символьным триграммам и слияние рангов."""

from collections import Counter, defaultdict
from math import log, sqrt


def trigrams(term):
    padded = "^" + term + "$"
    return {padded[i:i + 3] for i in range(len(padded) - 2)}


class VectorIndex:
    """Заголовки карточек и разделов в пространстве видимых роли документов."""

    def __init__(self, sections):
        documents = [Counter(g for word in section.focus for g in trigrams(word))
                     for section in sections]
        df = Counter(g for doc in documents for g in doc)
        self.idf = {g: 1 + log((1 + len(documents)) / (1 + count)) for g, count in df.items()}
        self.postings = defaultdict(list)
        for index, doc in enumerate(documents):
            weights = {g: self.idf[g] * (1 + log(count)) for g, count in sorted(doc.items())}
            norm = sqrt(sum(w * w for w in weights.values()))
            for gram, weight in weights.items():
                self.postings[gram].append((index, weight / norm))

    def scores(self, terms):
        grams = Counter(g for term in terms for g in trigrams(term))
        # Неизвестные триграммы входят в норму: случайное частичное
        # совпадение с длинным посторонним запросом получает меньший вес.
        weights = {g: self.idf.get(g, 1) * (1 + log(count)) for g, count in grams.items()}
        norm = sqrt(sum(w * w for w in weights.values()))
        scores = defaultdict(float)
        for gram, weight in sorted(weights.items()):
            for index, value in self.postings.get(gram, ()):
                scores[index] += value * weight / norm
        return scores


def fuse(lexical, vector, *other_rankings, depth=30):
    fused = Counter()
    for ranking in (lexical, vector, *other_rankings):
        for rank, index in enumerate(ranking[:depth], 1):
            fused[index] += 1 / (60 + rank)
    # Порядок лексической выдачи разрешает равенства в RRF.
    tie = {index: rank for rank, index in enumerate(lexical)}
    return sorted(fused.items(), key=lambda pair: (-pair[1], tie.get(pair[0], len(tie)), pair[0]))
