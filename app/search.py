"""Server-configured search adapter; no arbitrary HTTP target is accepted."""
import httpx

class SearchError(Exception): pass
class ConfiguredSearch:
    def __init__(self, url: str | None, timeout: float = 8, transport=None) -> None: self.url, self.timeout, self.transport = url, timeout, transport
    async def search(self, query: str) -> list[dict[str, str]]:
        if not self.url: raise SearchError("Web search is not configured.")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client: response = await client.get(self.url, params={"q": query})
            response.raise_for_status(); items = response.json().get("results", [])
            return [{"title": str(x["title"]), "url": str(x["url"]), "snippet": str(x.get("snippet", ""))} for x in items[:5]]
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error: raise SearchError("Web search failed.") from error
