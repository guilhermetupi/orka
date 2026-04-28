import litellm
from orka.core.config import settings


def setup_litellm():
    litellm.set_verbose = settings.verbose


def chat(model: str, messages: list[dict], **kwargs) -> str:
    response = litellm.completion(model=model, messages=messages, **kwargs)
    return response["choices"][0]["message"]["content"]
