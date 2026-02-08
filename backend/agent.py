import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests

# Load environment variables
load_dotenv()

# Initialize OpenAI client (works with both OpenAI and Gemini)
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL", None)  # Optional: for Gemini

if base_url:
    # Using Gemini endpoint
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
else:
    # Using standard OpenAI
    client = OpenAI(api_key=api_key)

# Define tools for the AI to interact with your Task Database
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new todo task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title (e.g., 'Buy milk')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional details about the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Get all todo tasks for the user",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task (mark as complete, change title, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Whether the task is completed"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a todo task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]

def call_mcp_tool(tool_name: str, arguments: dict, user_id: str):
    """Bridge between the AI and your FastAPI database routes"""
    base_url = "http://localhost:8000/mcp/tools"  # Fixed port to 8000
    
    try:
        if tool_name == "create_task":
            response = requests.post(
                f"{base_url}/create_task",
                json={
                    "user_id": user_id,
                    "title": arguments["title"],
                    "description": arguments.get("description")
                }
            )
        
        elif tool_name == "list_tasks":
            response = requests.get(
                f"{base_url}/list_tasks",
                params={"user_id": user_id}
            )
        
        elif tool_name == "update_task":
            task_id = arguments["task_id"]
            response = requests.patch(
                f"{base_url}/update_task/{task_id}",
                params={"user_id": user_id},
                json={
                    "completed": arguments.get("completed"),
                    "title": arguments.get("title"),
                    "description": arguments.get("description")
                }
            )
        
        elif tool_name == "delete_task":
            task_id = arguments["task_id"]
            response = requests.delete(
                f"{base_url}/delete_task/{task_id}",
                params={"user_id": user_id}
            )
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
        
        response.raise_for_status()
        return response.json()
    
    except Exception as e:
        return {"error": str(e)}

def run_agent(user_message: str, user_id: str, conversation_history: list):
    """Main agent loop using OpenAI or Gemini"""
    
    messages = conversation_history + [
        {"role": "user", "content": user_message}
    ]
    
    # Determine model based on base_url
    if base_url and "generativelanguage.googleapis.com" in base_url:
        model_name = "gemini-1.5-flash"  # Gemini
    else:
        model_name = "gpt-4o-mini"  # OpenAI
    
    try:
        # Initial call to AI
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Check if AI wants to use tools (Database interactions)
        if assistant_message.tool_calls:
            messages.append(assistant_message)
            
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Calling tool: {tool_name} with {arguments}")
                
                # Execute the database change
                tool_result = call_mcp_tool(tool_name, arguments, user_id)
                
                # Feed the result back to the AI
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result)
                })
            
            # Final response after database action
            final_response = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return final_response.choices[0].message.content
        else:
            return assistant_message.content

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}. Please check your .env file."

print("🚀 AI Agent Loaded!")