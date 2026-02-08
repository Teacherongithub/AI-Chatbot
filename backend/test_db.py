from database import create_db_and_tables, get_session
from models import Task

def test_database():
    """
    Test if database connection works and create tables
    """
    print("🔄 Creating database tables...")
    create_db_and_tables()
    
    print("\n🔄 Testing database connection...")
    
    # Try to add a test task
    session = next(get_session())
    
    test_task = Task(
        user_id="test_user",
        title="Test Task - Delete Me",
        description="This is a test task"
    )
    
    session.add(test_task)
    session.commit()
    session.refresh(test_task)
    
    print(f"✅ Test task created with ID: {test_task.id}")
    print(f"   Title: {test_task.title}")
    print(f"   Completed: {test_task.completed}")
    
    # Read the task back
    all_tasks = session.query(Task).filter(Task.user_id == "test_user").all()
    print(f"\n✅ Found {len(all_tasks)} task(s) in database")
    
    print("\n🎉 Database is working perfectly!")

if __name__ == "__main__":
    test_database()
