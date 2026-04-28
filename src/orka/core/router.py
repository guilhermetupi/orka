def get_model_for_tier(tier: str) -> str:
    if tier == "t0":
        return "ollama/qwen3.5:4b"

    if tier == "t1":
        return "gpt-5.4-nano"

    if tier == "t2":
        return "claude-sonnet-4-6"

    raise ValueError(f"Unknown tier: {tier}")