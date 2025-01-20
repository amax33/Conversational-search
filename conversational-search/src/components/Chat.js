import React, { useState } from 'react';
import axios from 'axios';
import '../styles/Chat.css';

function Chat({ onQuery, onFiltersUpdate }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newUserMessage = { role: 'user', content: input };
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    setInput('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/chat', {
        conversation: updatedMessages,
      });

      const newAssistantMessage = {
        role: 'assistant',
        content: response.data.response,
      };
      setMessages((prev) => [...prev, newAssistantMessage]);

      // If a search query is included, extract and apply filters
      if (response.data.query) {
        const query = response.data.query;
        const priceMatch = query.match(/under\s*(\d+)/i);
        const maxPrice = priceMatch ? parseFloat(priceMatch[1]) : null;

        onFiltersUpdate({
          priceMax: maxPrice || null, // Update the max price filter if present
        });

        onQuery(query); // Fetch products using the extracted query
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

