"""CrewAI adapter; transport and truth fields are shared with the base tool."""
import json
from hunterkiller_langchain import get_levels, DESCRIPTION


def create_levels_tool(*, key=None):
    from crewai.tools import tool

    @tool("hunterkiller_levels")
    def hunterkiller_levels(symbol: str) -> str:
        """Read liquidation walls, snapshot age and public record. Free data is 2 hours behind."""
        return json.dumps(get_levels(symbol, key=key))

    return hunterkiller_levels
