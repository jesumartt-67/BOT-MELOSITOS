import React, { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';

const ChatWindow = () => {
  const [messages, setMessages] = useState([
    { role: 'bot', content: '¡Hola! Soy el asistente del Jardín Infantil. ¿En qué puedo ayudarte hoy?' }
  ]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');

    try {
      // Llamada al endpoint /ask de tu backend inteligente en el i5-9400
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });

      const data = await response.json();

      // Se utiliza data.answer para recibir la respuesta filtrada de Groq
      setMessages([...newMessages, { role: 'bot', content: data.answer }]);

    } catch (error) {
      setMessages([...newMessages, { role: 'bot', content: 'Error de conexión con el servidor.' }]);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4 bg-gray-50">
      <header className="p-4 bg-blue-600 text-white rounded-t-lg shadow-md">
        <h1 className="text-xl font-bold">Asistente Virtual Jardín</h1>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 border-x bg-white">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
              <div className="flex items-center gap-2 mb-1 text-xs font-semibold uppercase">
                {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                {msg.role}
              </div>
              <div className="whitespace-pre-wrap">{msg.content}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 bg-white border-t rounded-b-lg flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          className="flex-1 p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          placeholder="Pregunta sobre uniformes, costos..."
        />
        <button onClick={sendMessage} className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 transition">
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;