from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendRequest(BaseModel):
	query: str = Field(..., description="User natural language query for music recommendations")
	top_k: Optional[int] = Field(5, ge=1, le=20)


class Recommendation(BaseModel):
	title: str
	artist: Optional[str] = None
	album: Optional[str] = None
	genre: Optional[str] = None
	score: float = 0.0
	source: str = "knowledge_base"


class RecommendResponse(BaseModel):
	query: str
	recommendations: List[Recommendation]
	meta: dict


