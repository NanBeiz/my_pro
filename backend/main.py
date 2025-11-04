from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
import os

from .kb import retrieve_from_knowledge_base
from .llm import generate_with_llm
from .agent_core import run_agent


class Recommendation(BaseModel):
	title: str
	artist: Optional[str] = None
	album: Optional[str] = None
	genre: Optional[str] = None
	score: float = 0.0
	source: str = ""


class RecommendRequest(BaseModel):
	query: str
	top_k: Optional[int] = 5


app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health() -> Any:
	return jsonify({"status": "ok"})


@app.post("/api/recommend")
def recommend():
	try:
		payload = request.get_json(force=True) or {}
		req = RecommendRequest(**payload)
	except (TypeError, ValidationError) as e:
		return jsonify({"detail": "Invalid request", "error": str(e)}), 400

	if not req.query or not req.query.strip():
		return jsonify({"detail": "Query is required"}), 400

    # Use LangChain Agent end-to-end
    top_k = req.top_k or 5
    items = run_agent(req.query, top_k=top_k)
    if not items:
        return jsonify({"detail": "Failed to generate recommendations"}), 500

    return jsonify({
        "query": req.query,
        "recommendations": [Recommendation(**{
            "title": it.get("title", ""),
            "artist": it.get("artist"),
            "album": it.get("album"),
            "genre": it.get("genre"),
            "score": float(it.get("score", 0.0)),
            "source": it.get("source", "agent"),
        }).model_dump() for it in items],
        "meta": {"strategy": "langchain_agent"}
    })


if __name__ == "__main__":
	port = int(os.getenv("PORT", "8000"))
	app.run(host="0.0.0.0", port=port, debug=True)


