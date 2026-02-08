from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task Model - Represents a todo item
    This creates a 'task' table in the database
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Who owns this task
    title: str  # Task title like "Buy groceries"
    description: Optional[str] = None  # Extra details (optional)
    completed: bool = Field(default=False)  # Is it done?
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(SQLModel, table=True):
    """
    Conversation Model - Represents a chat session
    Each conversation contains multiple messages
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Who owns this conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    """
    Message Model - Represents a single chat message
    Messages belong to a conversation
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Who owns this message
    conversation_id: int = Field(foreign_key="conversation.id")  # Which conversation
    role: str  # "user" or "assistant"
    content: str  # The actual message text
    created_at: datetime = Field(default_factory=datetime.utcnow)
