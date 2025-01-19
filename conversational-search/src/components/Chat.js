import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Chat.css';

function Chat({ onQuery }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    setMessages((prev) => [...prev, { role: 'user', content: input }]);

    // Fetch response from the backend
    const response = await axios.post('http://127.0.0.1:8000/api/chat', { message: input });

    // Add AI response to the chat
    setMessages((prev) => [...prev, { role: 'assistant', content: response.data.response }]);

    // If the AI triggers a search, call the `onQuery` handler
    if (response.data.query) {
      onQuery(response.data.query);
    }

    setInput('');
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

