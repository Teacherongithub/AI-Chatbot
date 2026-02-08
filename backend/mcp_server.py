# backend/mcp_server.py
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from database import get_session
from models import Task, Conversation, Message
from typing import List, Optional
from pydantic import BaseModel

mcp_app = FastAPI()

# Request/Response Models
class CreateTaskRequest(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None

class UpdateTaskRequest(BaseModel):
    completed: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool

# Tool 1: Create Task
@mcp_app.post("/tools/create_task")
def create_task(request: CreateTaskRequest, session: Session = Depends(get_session)):
    """Create a new todo task"""
    task = Task(
        user_id=request.user_id,
        title=request.title,
        description=request.description
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }
    }

# Tool 2: List Tasks
@mcp_app.get("/tools/list_tasks")
def list_tasks(user_id: str, session: Session = Depends(get_session)):
    """Get all tasks for a user"""
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    
    return {
        "success": True,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed
            }
            for task in tasks
        ]
    }

# Tool 3: Update Task
@mcp_app.patch("/tools/update_task/{task_id}")
def update_task(
    task_id: int,
    user_id: str,
    request: UpdateTaskRequest,
    session: Session = Depends(get_session)
):
    """Update a task (mark complete, edit title, etc.)"""
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        return {"success": False, "error": "Task not found"}
    
    if request.completed is not None:
        task.completed = request.completed
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        }
    }

# Tool 4: Delete Task
@mcp_app.delete("/tools/delete_task/{task_id}")
def delete_task(task_id: int, user_id: str, session: Session = Depends(get_session)):
    """Delete a task"""
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        return {"success": False, "error": "Task not found"}
    
    session.delete(task)
    session.commit()
    
    return {"success": True, "message": "Task deleted"}

print("🛠️ MCP Server tools loaded!")