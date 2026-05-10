## Server Usage

Run the server with `uv run server.py`.

```
https://federal-chocolate-dove.fastmcp.app/mcp
```

## OPENAI Usage
```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "federal-chocolate-dove",
            "server_url": "https://federal-chocolate-dove.fastmcp.app/mcp",
            "require_approval": "never",
        },
    ],
    input="Hello from Horizon!",
)
```

## CLAUDE AND GEMINI CODE Usage
```python

# CLAUDE
claude mcp add --scope local --transport http federal-chocolate-dove https://federal-chocolate-dove.fastmcp.app/mcp

# GEMINI
gemini mcp add federal-chocolate-dove https://federal-chocolate-dove.fastmcp.app/mcp --transport http

```