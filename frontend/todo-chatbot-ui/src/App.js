// src/App.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Bot, User, Trash2 } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:8000';
const USER_ID = 'demo-user';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [todos, setTodos] = useState([]);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load todos on mount
  useEffect(() => {
    loadTodos();
  }, []);

  // Load todos from backend
  const loadTodos = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/mcp/tools/list_tasks?user_id=${USER_ID}`
      );

      console.log('Tasks response:', response.data);

      // Handle different response structures
      if (response.data && response.data.tasks && Array.isArray(response.data.tasks)) {
        setTodos(response.data.tasks);
      } else if (Array.isArray(response.data)) {
        setTodos(response.data);
      } else {
        console.warn('Unexpected tasks response format:', response.data);
        setTodos([]);
      }
    } catch (error) {
      console.error('Error loading todos:', error);
      if (error.response) {
        console.error('Backend error:', error.response.data);
      }
      setTodos([]);
    }
  };

  // Send message to chatbot
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');

    // Add user message to chat UI immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    console.log('Sending message:', {
      message: userMessage,
      user_id: USER_ID,
      conversation_id: conversationId
    });

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: userMessage,
        user_id: USER_ID,
        conversation_id: conversationId
      });

      console.log('Chat response:', response.data);

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);

      // Update conversation ID if it's the first message
      if (!conversationId && response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      }

      // Reload todos (in case the AI added/updated one)
      await loadTodos();

    } catch (error) {
      console.error('Error sending message:', error);
      if (error.response) {
        console.error('Backend error:', error.response.data);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please check if the backend is running.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Toggle todo completion
  const toggleTodo = async (todoId, currentStatus) => {
    try {
      console.log('Toggling todo:', todoId, 'to', !currentStatus);
      const response = await axios.patch(
        `${API_URL}/mcp/tools/update_task/${todoId}?user_id=${USER_ID}`,
        { completed: !currentStatus }
      );
      console.log('Toggle response:', response.data);
      await loadTodos();
    } catch (error) {
      console.error('Error updating todo:', error);
      if (error.response) {
        console.error('Backend error:', error.response.data);
      }
    }
  };

  // Delete todo
  const deleteTodo = async (todoId) => {
    try {
      console.log('Deleting todo:', todoId);
      const response = await axios.delete(
        `${API_URL}/mcp/tools/delete_task/${todoId}?user_id=${USER_ID}`
      );
      console.log('Delete response:', response.data);
      await loadTodos();
    } catch (error) {
      console.error('Error deleting todo:', error);
      if (error.response) {
        console.error('Backend error:', error.response.data);
      }
    }
  };

  return (
    <div className="app-container">
      {/* Left Panel - Todo List */}
      <div className="todo-panel">
        <div className="todo-header">
          <h2>📝 My Tasks</h2>
          <div className="todo-count">
            {todos.filter(t => !t.completed).length} active, {todos.filter(t => t.completed).length} completed
          </div>
        </div>

        <div className="todo-list">
          {todos.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📭</div>
              <p>No tasks yet!</p>
              <p style={{ fontSize: '14px', marginTop: '5px' }}>
                Try saying: &quot;Add buy milk&quot;
              </p>
            </div>
          ) : (
            todos.map(todo => (
              <div key={todo.id} className="todo-item">
                <input
                  type="checkbox"
                  className="todo-checkbox"
                  checked={todo.completed || false}
                  onChange={() => toggleTodo(todo.id, todo.completed)}
                />
                <div className="todo-content">
                  <div className={`todo-title ${todo.completed ? 'completed' : ''}`}>
                    {todo.title}
                  </div>
                  {todo.description && (
                    <div className="todo-description">{todo.description}</div>
                  )}
                </div>
                <button
                  className="delete-btn"
                  onClick={() => deleteTodo(todo.id)}
                  title="Delete task"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Right Panel - Chat */}
      <div className="chat-panel">
        <div className="chat-header">
          <Bot size={28} />
          <h2>AI Todo Assistant</h2>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <p>Start chatting with your AI assistant!</p>
              <p style={{ fontSize: '14px', marginTop: '10px' }}>
                Try: &quot;Add buy groceries&quot; or &quot;Show my tasks&quot;
              </p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="loading">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Type a message... (e.g., 'Add buy milk')"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              className="send-btn"
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;