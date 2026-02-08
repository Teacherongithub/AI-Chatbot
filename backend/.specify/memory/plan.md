# Implementation Plan

1. **DB Setup:** Configure `database.py` to connect to Neon PostgreSQL via environment variables.
2. **Models:** Implement SQLModel classes in `models.py`.
3. **MCP Server:** Initialize the Official MCP SDK server and define the 5 tool functions.
4. **Agent Logic:** Setup OpenAI Agents SDK to call the MCP tools based on natural language intent.
5. **API Route:** Create the FastAPI POST endpoint to orchestrate the stateless flow.