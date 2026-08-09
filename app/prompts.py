"""Versioned prompts kept outside HTTP handlers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Prompt:
    name: str
    version: str
    text: str


BASE_PROMPT = Prompt("local-chat", "v1", "You are a helpful, concise assistant.")


def assemble(base: Prompt = BASE_PROMPT, domain_instructions: str | None = None) -> Prompt:
    text = base.text if not domain_instructions else f"{base.text}\n\nAdditional instructions:\n{domain_instructions}"
    return Prompt(base.name, base.version, text)
