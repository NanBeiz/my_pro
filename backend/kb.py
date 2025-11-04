import json
import math
import os
import re
from functools import lru_cache
from typing import Any, Dict, List


@lru_cache(maxsize=1)
def _load_kb() -> Dict[str, Any]:
	path_candidates = [
		os.path.join(os.path.dirname(__file__), "knowledge_base.json"),
		os.path.join(os.getcwd(), "backend", "knowledge_base.json"),
		os.path.join(os.getcwd(), "knowledge_base.json"),
	]
	for p in path_candidates:
		if os.path.exists(p):
			with open(p, "r", encoding="utf-8") as f:
				return json.load(f)
	return {"tracks": []}


def _tokenize(text: str) -> List[str]:
	text = (text or "").lower()
	return re.findall(r"[\w\u4e00-\u9fa5]+", text)


def _score_item(query_tokens: List[str], item: Dict[str, Any]) -> float:
	fields = [
		item.get("title", ""),
		item.get("artist", ""),
		item.get("album", ""),
		item.get("genre", ""),
		" ".join(item.get("tags", []) or []),
	]
	text_tokens = []
	for f in fields:
		text_tokens.extend(_tokenize(f))
	if not text_tokens:
		return 0.0
	match = sum(1 for t in query_tokens if t in text_tokens)
	coverage = match / max(1, len(set(query_tokens)))
	len_penalty = 1.0 - 0.1 * math.log10(1 + abs(len(text_tokens) - len(query_tokens)))
	len_penalty = max(0.7, min(1.0, len_penalty))
	return round(coverage * len_penalty, 4)


def retrieve_from_knowledge_base(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
	query_tokens = _tokenize(query)
	if not query_tokens:
		return []
	tracks: List[Dict[str, Any]] = list(_load_kb().get("tracks", []) or [])
	for item in tracks:
		item["score"] = _score_item(query_tokens, item)
	tracks.sort(key=lambda x: x.get("score", 0.0), reverse=True)
	return tracks[: max(1, top_k)]


def kb_tool_search(query: str, top_k: int = 5) -> Dict[str, Any]:
	results = retrieve_from_knowledge_base(query, top_k=top_k)
	return {"items": results}



