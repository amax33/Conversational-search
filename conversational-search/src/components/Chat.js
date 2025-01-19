import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Chat.css';

function Chat({ onQuery }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 1. Add the user message to local state
    const newUserMessage = { role: 'user', content: input };
    const updatedMessages = [...messages, newUserMessage];

    setMessages(updatedMessages);
    setInput('');

    try {
      // 2. Send the ENTIRE conversation so far to the backend
      const response = await axios.post('http://127.0.0.1:8000/api/chat', {
        conversation: updatedMessages,
      });

      // 3. Add the LLM/assistant message to local state
      const newAssistantMessage = {
        role: 'assistant',
        content: response.data.response,
      };
      setMessages((prev) => [...prev, newAssistantMessage]);

      // 4. If there is a 'query' from the backend, we do a search in the product list
      if (response.data.query) {
        onQuery(response.data.query);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;

