"""Bounded local agent limited to approved, deterministic tools."""
from app.governance import RequestGuard
from app.tools import execute

class AgentError(ValueError): pass

class LocalAgent:
    def __init__(self, guard: RequestGuard, max_steps: int = 2) -> None: self.guard, self.max_steps = guard, max_steps
    def run(self, goal: str) -> dict[str, object]:
        self.guard.check()
        if not goal.lower().startswith("calculate:"): raise AgentError("Local agent supports only 'calculate: <expression>'.")
        result = execute("calculator", {"expression": goal.split(":", 1)[1].strip()})
        return {"status": "completed", "steps": [{"status": "Running calculator…", "tool": "calculator"}], "result": result["result"]}
