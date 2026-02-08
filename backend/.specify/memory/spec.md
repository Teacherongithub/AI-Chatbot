# Technical Specification

## 1. Database Schema (SQLModel)
- **Task:** user_id, id, title, description, completed, created_at, updated_at.
- **Conversation:** user_id, id, created_at, updated_at.
- **Message:** user_id, id, conversation_id, role, content, created_at.

## 2. MCP Tools
The server must expose these 5 tools:
1. `add_task`: Create new task (user_id, title, description).
2. `list_tasks`: Filter by status (all, pending, completed).
3. `complete_task`: Mark task_id as complete.
4. `delete_task`: Remove task_id.
5. `update_task`: Modify title or description.

## 3. Chat Endpoint
- **Method:** POST `/api/{user_id}/chat`.
- **Input:** `conversation_id` (optional), `message` (required).