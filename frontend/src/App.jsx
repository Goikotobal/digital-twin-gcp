import { useState } from 'react';
import { API_URL } from './config';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');

  const sendMessage = async () => {
    const res = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input, sessionId: 'demo123' }),
    });

    const data = await res.json();
    setResponse(data.response || 'No response received');
  };

  return (
    <div style={{ padding: 20, fontFamily: 'Arial' }}>
      <h2>🧠 Digital Twin Chat</h2>
      <input
        style={{ padding: 8, width: 300 }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask me anything..."
      />
      <button onClick={sendMessage} style={{ marginLeft: 10, padding: 8 }}>
        Send
      </button>
      <p><strong>Bot:</strong> {response}</p>
    </div>
  );
}

export default App;
