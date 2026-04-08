import { useEffect, useRef, useState } from "react";
import { ClerkProvider, useAuth } from "@clerk/react";

function ChatContent() {
  const { getToken } = useAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("idle");

  const fileInputRef = useRef(null); // Ref for the hidden file input
  const messagesEndRef = useRef(null); // Ref for auto-scrolling
  const wsRef = useRef(null);

  // 🔌 Connect WebSocket
  useEffect(() => {
    async function connect() {
      const token = await getToken();

      const ws = new WebSocket(
        "wss://talenthackathon-economity-backend-production.up.railway.app/ws/asesor"
      );

      ws.onopen = () => {
        console.log("Connected");

        // 🔐 Send token FIRST (your backend expects this)
        ws.send(JSON.stringify({ token }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "message") {
          setMessages((prev) => [
            ...prev,
            { sender: "bot", text: data.content },
          ]);
        }

        if (data.type === "status") {
          setStatus(data.content);
        }
      };

      ws.onclose = () => console.log("Disconnected");

      wsRef.current = ws;
    }

    connect();

    return () => wsRef.current?.close();
  }, []);

  // 📤 Send message
  const sendMessage = () => {
    if (!input.trim()) return;

    const newMessage = { sender: "user", text: input };

    setMessages((prev) => [...prev, newMessage]);

    wsRef.current?.send(
      JSON.stringify({
        content: input,
        history: messages,
      })
    );

    setInput("");
  };

  // Handle Enter key press
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Added !e.shiftKey to allow multiline input if needed
      e.preventDefault();
      sendMessage();
    }
  };

  // Handle file attachment
  const handleAttachFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      console.log("Attached file:", files[0].name);
      // TODO: Implement actual file upload logic here
      // For now, just logging the file name.
      // You might want to add a message to the chat indicating a file was attached.
    }
  };

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 min-h-0 overflow-y-auto p-4 flex flex-col gap-4 pb-2">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                msg.sender === "user"
                  ? "bg-primary text-white"
                  : "bg-surface-container-lowest text-on-surface border border-outline-variant"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}

        {/* Status indicator */}
        {status !== "idle" && (
          <div className="flex items-center gap-2">
            <div className="ai-chip animate-pulse">{status}...</div>
          </div>
        )}
        <div ref={messagesEndRef} /> {/* For auto-scrolling */}
      </div>

      <div className="p-4 flex items-center gap-2 border-t border-outline-variant">
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
        {/* Attach files icon */}
        <button
          onClick={handleAttachFileClick}
          className="p-2 rounded-full hover:bg-surface-container-low transition-colors"
          aria-label="Attach file"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-gray-500 cursor-pointer hover:text-gray-700 transition-colors">
            <path strokeLinecap="round" strokeLinejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94a3 3 0 114.243 4.243l-10.53 10.53a1.5 1.5 0 01-2.121-2.121l9.645-9.645" />
          </svg>
        </button>

        <input
          className="flex-1 input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown} // Add onKeyDown handler
          placeholder="Ask your advisor!"
        />

        {/* Microphone icon */}
        <button
          className="p-2 rounded-full hover:bg-surface-container-low transition-colors"
          aria-label="Voice input"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-gray-500 cursor-pointer hover:text-red-500 transition-colors">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 6a6 6 0 01-6-6v-1.5m6 6v3.75m-3.75 0h7.5M12 10.5a3 3 0 11-6 0v-1.5a3 3 0 016 0v1.5z" />
          </svg>
        </button>

        <button
          onClick={sendMessage}
          className="btn-primary"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default function Chat() {
  return (
    <ClerkProvider publishableKey={import.meta.env.PUBLIC_CLERK_PUBLISHABLE_KEY}>
      <ChatContent />
    </ClerkProvider>
  );
}