"""Standalone Composio tool. Not an official hosted Composio toolkit listing."""
from hunterkiller_langchain import get_levels


def create_levels_tool(composio, *, key=None):
    from pydantic import BaseModel, Field

    class LevelsInput(BaseModel):
        symbol: str = Field(description="Pair such as BTCUSDT. Free data is 2 hours behind.")

    @composio.experimental.tool()
    def hunterkiller_levels(input: LevelsInput, ctx):
        """Read liquidation walls with snapshot age, evidence labels and public record."""
        return get_levels(input.symbol, key=key)

    return hunterkiller_levels
