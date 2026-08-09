"""Local request budget and rate-limit guard for every model invocation."""
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

class BudgetError(Exception): pass

class RequestGuard:
    def __init__(self, per_minute: int, per_day: int) -> None:
        self.per_minute, self.per_day = per_minute, per_day
        self._calls: dict[str, deque[datetime]] = defaultdict(deque)
    def check(self, identity: str = "local") -> None:
        now = datetime.now(UTC); calls = self._calls[identity]
        while calls and calls[0] < now - timedelta(days=1): calls.popleft()
        if len(calls) >= self.per_day: raise BudgetError("Daily model request budget reached. Try again tomorrow.")
        if sum(item >= now - timedelta(minutes=1) for item in calls) >= self.per_minute: raise BudgetError("Too many requests. Please wait a minute and try again.")
        calls.append(now)
