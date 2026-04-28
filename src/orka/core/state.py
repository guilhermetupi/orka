from typing import Literal, TypedDict

TaskMode = Literal["ask", "plan", "debug", "implement", "run", "review"]
Tier = Literal["t0", "t1", "t2"]


class OrkaState(TypedDict):
    mode: TaskMode
    prompt: str

    tier: Tier
    risk_score: int
    needs_review: bool

    context: str
    result: str
    review: str
