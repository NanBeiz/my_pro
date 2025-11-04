import json
import os
import math
from typing import List, Dict

_KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")


def _load_kb() -> Dict:
	with open(_KB_PATH, "r", encoding="utf-8") as f:
		return json.load(f)


def _tokenize(text: str) -> List[str]:
	# Simple whitespace + lowercase tokenization; replace with better NLP if needed
	return [t for t in text.lower().replace("\n", " ").split(" ") if t]


def _compute_score(query_tokens: List[str], item: Dict) -> float:
	# Combine title, artist, genre, tags
	fields = [
		item.get("title", ""),
		item.get("artist", ""),
		item.get("album", ""),
		item.get("genre", ""),
		" ".join(item.get("tags", [])),
	]
	candidate_text = " ".join(fields).lower()
	if not candidate_text:
		return 0.0

	# Simple term frequency score with small boosts
	score = 0.0
	for token in query_tokens:
		if not token:
			continue
		count = candidate_text.count(token)
		if count:
			boost = 1.0
			if token in (item.get("genre", "").lower()):
				boost += 0.5
			score += math.log(1 + count) * boost
	return score


def retrieve_from_knowledge_base(query: str, top_k: int = 5) -> List[Dict]:
	kb = _load_kb()
	tracks: List[Dict] = kb.get("tracks", [])
	q_tokens = _tokenize(query)
	if not tracks:
		return []

	scored = []
	for t in tracks:
		s = _compute_score(q_tokens, t)
		if s > 0.0:
			scored.append({**t, "score": round(float(s), 4)})

	scored.sort(key=lambda x: x["score"], reverse=True)
	return scored[:top_k]


