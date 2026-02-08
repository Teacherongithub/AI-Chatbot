# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import Conversation, Message, Task
from agent import run_agent
from mcp_server import mcp_app
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Creating database tables...")
    create_db_and_tables()
    print("✅ Database tables created successfully!")
    yield
    # Shutdown (if needed, add cleanup code here)

# Create main app with lifespan
app = FastAPI(
    title="Todo Chatbot API",
    lifespan=lifespan
)

# Add CORS to main app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://192.168.0.103:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add CORS to MCP app as well
mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://192.168.0.103:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server
app.mount("/mcp", mcp_app)

# Request model
class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: int | None = None

# Main chat endpoint
@app.post("/chat")
def chat(request: ChatRequest, session: Session = Depends(get_session)):
    """Main chatbot endpoint"""
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = session.get(Conversation, request.conversation_id)
            if not conversation:
                conversation = Conversation(user_id=request.user_id)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
        else:
            conversation = Conversation(user_id=request.user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
        
        # Get conversation history
        statement = select(Message).where(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at)
        history = session.exec(statement).all()
        
        # Convert to OpenAI format
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]
        
        # Run agent
        response = run_agent(
            user_message=request.message,
            user_id=request.user_id,
            conversation_history=conversation_history
        )
        
        # Save messages
        user_msg = Message(
            user_id=request.user_id,
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        assistant_msg = Message(
            user_id=request.user_id,
            conversation_id=conversation.id,
            role="assistant",
            content=response
        )
        
        session.add(user_msg)
        session.add(assistant_msg)
        session.commit()
        
        return {
            "response": response,
            "conversation_id": conversation.id
        }
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return {
            "response": f"Sorry, I encountered an error: {str(e)}",
            "conversation_id": request.conversation_id,
            "error": True
        }

# Health check
@app.get("/")
def root():
    return {"status": "Todo Chatbot API is running! 🚀"}

# Get conversations endpoint
@app.get("/conversations/{user_id}")
def get_conversations(user_id: str, session: Session = Depends(get_session)):
    """Get all conversations for a user"""
    statement = select(Conversation).where(Conversation.user_id == user_id)
    conversations = session.exec(statement).all()
    return {"conversations": conversations}

# Get conversation messages endpoint
@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int, session: Session = Depends(get_session)):
    """Get all messages in a conversation"""
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)
    messages = session.exec(statement).all()
    return {"messages": messages}

# TEST ENDPOINT: Create sample tasks - CHANGED TO GET
@app.get("/test/create-task")
def create_test_task(session: Session = Depends(get_session)):
    """Create test tasks - FOR TESTING ONLY"""
    
    # Check if tasks already exist
    existing = session.exec(select(Task).where(Task.user_id == "demo-user")).first()
    if existing:
        return {
            "message": "⚠️ Test tasks already exist. Delete them first or use a different endpoint.",
            "existing_count": len(session.exec(select(Task).where(Task.user_id == "demo-user")).all())
        }
    
    test_tasks = [
        Task(
            user_id="demo-user",
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False
        ),
        Task(
            user_id="demo-user",
            title="Finish homework",
            description="Math assignment chapter 5",
            completed=False
        ),
        Task(
            user_id="demo-user",
            title="Call dentist",
            description="Schedule appointment",
            completed=True
        )
    ]
    
    for task in test_tasks:
        session.add(task)
    
    session.commit()
    
    # Refresh to get IDs
    for task in test_tasks:
        session.refresh(task)
    
    return {
        "message": f"✅ Created {len(test_tasks)} test tasks!",
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed
            }
            for t in test_tasks
        ]
    }

# TEST ENDPOINT: Check database
@app.get("/test/check-db")
def check_database(session: Session = Depends(get_session)):
    """Check what's in the database"""
    
    statement = select(Task).where(Task.user_id == "demo-user")
    tasks = session.exec(statement).all()
    
    return {
        "total_tasks": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed
            }
            for t in tasks
        ]
    }

# TEST ENDPOINT: Clear all tasks
@app.delete("/test/clear-tasks")
def clear_tasks(session: Session = Depends(get_session)):
    """Delete all tasks for demo-user - FOR TESTING ONLY"""
    
    statement = select(Task).where(Task.user_id == "demo-user")
    tasks = session.exec(statement).all()
    
    count = len(tasks)
    for task in tasks:
        session.delete(task)
    
    session.commit()
    
    return {
        "message": f"🗑️ Deleted {count} tasks",
        "deleted_count": count
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)