"use client";

import { useState, useRef, useEffect, useMemo } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

interface Message {
  role: "user" | "assistant";
  content: string;
}

type TodoStatus = "pending" | "in_progress" | "done" | "error";

interface TodoItem {
  text: string;
  status: TodoStatus;
  message?: string | null;
}

// Convert URLs in plain text to clickable <a> elements.
function linkify(text: string) {
  // Regex matches http/https URLs stopping before trailing punctuation.
  const urlPattern = /(https?:\/\/[^\s)]+)([)\.,!?]?)/g;
  const elements: (string | JSX.Element)[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = urlPattern.exec(text)) !== null) {
    const [full, url, trailing] = match;
    // Push preceding text
    if (match.index > lastIndex) {
      elements.push(text.slice(lastIndex, match.index));
    }
    elements.push(
      <a
        key={elements.length}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="underline decoration-primary-500 hover:text-primary-600 break-words"
      >
        {url}
      </a>
    );
    if (trailing) elements.push(trailing);
    lastIndex = match.index + full.length;
  }
  if (lastIndex < text.length) {
    elements.push(text.slice(lastIndex));
  }
  return elements;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastResponseId, setLastResponseId] = useState<string | null>(null);
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionId = useMemo(() => (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`), []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Connect to SSE for progress updates
  useEffect(() => {
    const es = new EventSource(`${API_BASE_URL}/events?session_id=${encodeURIComponent(sessionId)}`);

    es.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        if (data.type === "todos" && Array.isArray(data.todos)) {
          setTodos(data.todos.map((t: string) => ({ text: t, status: "pending" as TodoStatus })));
        } else if (data.type === "todo_update" && data.todo && data.status) {
          setTodos((prev) => prev.map((item) => item.text === data.todo ? { ...item, status: data.status as TodoStatus, message: data.message ?? item.message } : item));
        }
      } catch (e) {
        console.warn("Failed to parse event:", e);
      }
    };

    es.onerror = () => {
      // Keep the UI calm; the user can still chat even if SSE drops
    };

    return () => {
      es.close();
    };
  }, [sessionId]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    // Clear previous plan and show new one only during this request
    setTodos([]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          previous_response_id: lastResponseId,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const assistantMessage: Message = {
        role: "assistant",
        content: data.output,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setLastResponseId(data.last_response_id);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: `Sorry, I encountered an error. Please make sure the backend server is running on ${API_BASE_URL}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] flex flex-col bg-white/80 dark:bg-slate-800/80 backdrop-blur-lg rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-purple-600 p-6 text-white">
          <h1 className="text-3xl font-bold mb-1">🎵 Concert Buddy</h1>
          <p className="text-primary-100 text-sm">
            Your AI-powered concert assistant
          </p>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-500 dark:text-slate-400 mt-20">
              <div className="text-6xl mb-4">🎸</div>
              <h2 className="text-2xl font-semibold mb-2">
                Welcome to Concert Buddy!
              </h2>
              <p className="text-lg">
                Ask me about upcoming concerts, get ticket info, or create
                playlists!
              </p>
              <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                <div className="p-4 bg-primary-50 dark:bg-slate-700 rounded-xl">
                  <div className="text-2xl mb-2">🔍</div>
                  <div className="text-sm font-medium">Find Concerts</div>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-slate-700 rounded-xl">
                  <div className="text-2xl mb-2">🎫</div>
                  <div className="text-sm font-medium">Get Tickets</div>
                </div>
                <div className="p-4 bg-pink-50 dark:bg-slate-700 rounded-xl">
                  <div className="text-2xl mb-2">🎵</div>
                  <div className="text-sm font-medium">Create Playlists</div>
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              } animate-slide-up`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-5 py-3 ${
                  message.role === "user"
                    ? "bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-md"
                }`}
              >
                <div className="whitespace-pre-wrap break-words">
                  {linkify(message.content)}
                </div>
              </div>
            </div>
          ))}

          {loading && todos.length > 0 && (
            <div className="flex justify-start animate-slide-up">
              <div className="max-w-[75%] rounded-2xl px-5 py-3 bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100 shadow-md">
                <ul className="space-y-2">
                  {todos.map((t, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={t.status === "done"}
                        readOnly
                        disabled
                        className="mt-0.5 h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      <div>
                        <div className="text-sm">{t.text}</div>
                        {t.message && (
                          <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                            {t.message}
                          </div>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {loading && (
            <div className="flex justify-start animate-fade-in">
              <div className="bg-slate-100 dark:bg-slate-700 rounded-2xl px-5 py-3 shadow-md">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-200 dark:border-slate-700 p-4 bg-white/50 dark:bg-slate-800/50 backdrop-blur">
          <div className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about concerts, tickets, or playlists..."
              disabled={loading}
              className="flex-1 px-5 py-3 bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-slate-900 dark:text-slate-100 placeholder-slate-500"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-8 py-3 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 text-white font-semibold rounded-2xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
