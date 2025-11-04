import os
import re
import json
from typing import Any, Dict, List

from .kb import kb_tool_search


def _mock_llm_response(user_query: str, kb_candidates: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
	base = kb_candidates[:top_k] if kb_candidates else []
	if base:
		for b in base:
			b["source"] = b.get("source", "kb+llm")
			b["score"] = float(b.get("score", 0.65)) + 0.1
		return base
	return [{
		"title": f"基于'{(user_query or '')[:16]}'的推荐",
		"artist": None,
		"album": None,
		"genre": None,
		"score": 0.6,
		"source": "llm",
	}]


def _get_openai_client():
	"""Create OpenAI client for DeepSeek using the latest SDK pattern.

	Defensively avoid passing unsupported kwargs and gracefully handle environments
	where underlying HTTP clients inject unexpected parameters (e.g., 'proxies').
	"""
	api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
	if not api_key:
		return None
	# DeepSeek recommends base_url without trailing /v1; SDK appends /v1 automatically.
	base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
	try:
		from openai import OpenAI  # import inside to avoid import-time side effects
		# Prefer explicit base_url; avoid passing any 'proxies' or unknown kwargs.
		client = OpenAI(api_key=api_key, base_url=base_url)
		return client
	except TypeError as te:
		# Some environments inject unexpected args into underlying clients; try minimal ctor.
		try:
			from openai import OpenAI
			client = OpenAI(api_key=api_key)
			return client
		except Exception:
			return None
	except Exception:
		return None


def _tools_schema() -> List[Dict[str, Any]]:
	return [{
		"type": "function",
		"function": {
			"name": "search_knowledge",
			"description": "搜索本地音乐知识库，返回与用户需求最匹配的曲目",
			"parameters": {
				"type": "object",
				"properties": {
					"query": {"type": "string"},
					"top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
				},
				"required": ["query"],
			},
		},
	}]


def _system_prompt(kb_candidates: List[Dict[str, Any]]) -> str:
	grounding = "\n".join(
		f"- 标题:{c.get('title','')} 歌手:{c.get('artist','')} 专辑:{c.get('album','')} 风格:{c.get('genre','')} 评分:{c.get('score',0)}"
		for c in (kb_candidates or [])
	)
	return (
		"你是一个中文音乐推荐智能体。先尝试调用工具 search_knowledge 检索本地 JSON 知识库；"
		"若结果不足，再结合用户需求与工具结果生成更优推荐。输出每条包含：标题、歌手、专辑、风格、置信度、来源。\n"
		f"知识库候选：\n{grounding}\n"
	)


def generate_with_llm(user_query: str, kb_candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
	client = _get_openai_client()
	if client is None:
		return _mock_llm_response(user_query, kb_candidates, top_k)

	model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
	messages = [
		{"role": "system", "content": _system_prompt(kb_candidates)},
		{"role": "user", "content": user_query},
	]

	try:
		first = client.chat.completions.create(
			model=model,
			messages=messages,
			tools=_tools_schema(),
			tool_choice="auto",
			temperature=0.6,
		)

		tool_calls = first.choices[0].message.tool_calls or []
		if tool_calls:
			for call in tool_calls:
				if call.function and call.function.name == "search_knowledge":
					args = json.loads(call.function.arguments or "{}")
					query = args.get("query") or user_query
					limit = int(args.get("top_k") or top_k)
					tool_result = kb_tool_search(query=query, top_k=limit)
					messages.append(first.choices[0].message)
					messages.append({
						"role": "tool",
						"tool_call_id": call.id,
						"name": "search_knowledge",
						"content": json.dumps(tool_result, ensure_ascii=False),
					})

			second = client.chat.completions.create(
				model=model,
				messages=messages,
				temperature=0.6,
			)
			content = (second.choices[0].message.content or "").strip()
		else:
			content = (first.choices[0].message.content or "").strip()

		items: List[Dict[str, Any]] = []
		for line in content.splitlines():
			line = line.strip().lstrip("-•*")
			if not line:
				continue
			parts = [p.strip() for p in re.split(r"[，,;；]\s*", line)]
			rec: Dict[str, Any] = {
				"title": parts[0] if parts else line,
				"artist": None,
				"album": None,
				"genre": None,
				"score": 0.75,
				"source": "llm",
			}
			items.append(rec)

		if not items and content:
			items = [{
				"title": content[:64],
				"artist": None,
				"album": None,
				"genre": None,
				"score": 0.7,
				"source": "llm",
			}]

		return items[: max(1, top_k)]
	except Exception:
		return _mock_llm_response(user_query, kb_candidates, top_k)



