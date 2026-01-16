# Todo AI Agent Specification

## 1. Objective
Build a stateless, AI-powered agent using the OpenAI Agents SDK and Model Context Protocol (MCP) to manage a user's todo list via natural language.

## 2. Agent Configuration
- **Name:** `TodoManagerAgent`
- **Model:** `gpt-4o-mini` (Cost-effective for class projects)
- **Instructions:** - You are a helpful Todo List Assistant.
    - Your goal is to manage the user's tasks by calling the provided MCP tools.
    - Always confirm the result of a tool call to the user (e.g., "I've added 'Buy milk' to your list!").
    - If a user command is ambiguous, ask for clarification.
    - Support natural language for adding, listing, completing, updating, and deleting tasks.

## 3. MCP Tool Mapping
The agent must use the following tools exposed by the MCP Server:

| Tool Name | Purpose | Required Parameters |
| :--- | :--- | :--- |
| `add_task` | Create a new todo | `user_id`, `title` |
| `list_tasks` | Fetch tasks | `user_id`, `status` (all/pending/completed) |
| `complete_task` | Mark task as done | `user_id`, `task_id` |
| `update_task` | Edit title/desc | `user_id`, `task_id` |
| `delete_task` | Remove a task | `user_id`, `task_id` |

## 4. Conversation Flow (Stateless)
1. **Input:** User sends a message via ChatKit UI.
2. **Context:** FastAPI fetches conversation history from Neon DB.
3. **Execution:** `Runner.run()` processes the prompt + history + tools.
4. **Tool Execution:** Agent calls MCP tool -> MCP tool updates Neon DB.
5. **Output:** Agent generates a response; FastAPI saves the message and returns it to ChatKit.

## 5. Success Criteria
- [ ] Agent successfully adds a task from a sentence like "Remind me to call Mom."
- [ ] Agent retrieves only "pending" tasks when asked "What do I have left to do?"
- [ ] Conversation history persists after a page refresh.