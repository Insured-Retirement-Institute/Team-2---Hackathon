import {
  useState,
  useRef,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  X,
  Send,
  Sparkles,
  User,
  Maximize2,
  Minimize2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessage, ChatContext } from "@/types/chat";
import { sendChat } from "@/api/chat";
import { ChatAPIContext } from "@/hooks/useChatContext";

function FluxCapacitorIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    >
      <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.8" />
      <line x1="12" y1="9" x2="12" y2="2" />
      <line x1="12" y1="15" x2="7" y2="22" />
      <line x1="12" y1="15" x2="17" y2="22" />
      <circle cx="12" cy="12" r="10" strokeWidth="1.5" opacity="0.4" />
    </svg>
  );
}

const WELCOME: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hello! I'm your AI Assistant for Replacement Reviews. I can help you understand products, analyze suitability, compare options, and answer compliance questions. How can I assist you today?",
  timestamp: new Date().toISOString(),
};

const MAX_PAIRS = 15;

function trimHistory(msgs: ChatMessage[]): ChatMessage[] {
  const convo = msgs.slice(1); // exclude welcome
  if (convo.length <= MAX_PAIRS * 2) return msgs;
  return [msgs[0], ...convo.slice(convo.length - MAX_PAIRS * 2)];
}

export function ChatBot({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const location = useLocation();
  const ctxRef = useRef<ChatContext>({ page: "/" });

  // Any component can call this to send a context beacon
  const sendContext = useCallback((ctx: ChatContext) => {
    ctxRef.current = ctx;
    sendChat({ context: ctx });
  }, []);

  // Auto-send context on route changes
  useEffect(() => {
    const path = location.pathname;
    const match = path.match(/\/alerts\/(.+)/);
    sendContext({ ...ctxRef.current, page: path, alertId: match?.[1] });
  }, [location.pathname, sendContext]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);
  
  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  const send = async (content?: string) => {
    const text = (content || input).trim();
    if (!text || typing) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => trimHistory([...prev, userMsg]));
    setInput("");
    setTyping(true);

    const assistantId = `assistant-${Date.now()}`;

    try {
      const history = messages.slice(1); // exclude welcome
      let firstChunk = true;
      await sendChat(
        {
          context: ctxRef.current,
          message: text,
          history,
        },
        (chunk: string) => {
          // On first chunk, create the message and hide typing indicator
          if (firstChunk) {
            firstChunk = false;
            setTyping(false);
            const assistantMsg: ChatMessage = {
              id: assistantId,
              role: "assistant",
              content: chunk,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => trimHistory([...prev, assistantMsg]));
          } else {
            // Update streaming content
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: msg.content + chunk }
                  : msg
              )
            );
          }
        }
      );
    } catch {
      setMessages((prev) => {
        const hasMessage = prev.some(msg => msg.id === assistantId);
        if (hasMessage) {
          return prev.map((msg) =>
            msg.id === assistantId
              ? {
                  ...msg,
                  content: "Sorry, something went wrong. Please try again.",
                }
              : msg
          );
        } else {
          return trimHistory([...prev, {
            id: assistantId,
            role: "assistant",
            content: "Sorry, something went wrong. Please try again.",
            timestamp: new Date().toISOString(),
          }]);
        }
      });
    } finally {
      setTyping(false);
    }
  };

  return (
    <ChatAPIContext.Provider value={{ sendContext }}>
      {children}

      {/* FAB */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center z-50"
          aria-label="Open AI Assistant"
        >
          <FluxCapacitorIcon className="h-7 w-7" />
          <span className="absolute -top-1 -right-1 h-3 w-3 bg-green-500 rounded-full border-2 border-white animate-pulse" />
        </button>
      )}

      {/* Chat Panel */}
      {open && (
        <>
          {/* Backdrop for expanded mode */}
          {expanded && (
            <div
              className="fixed inset-0 bg-black/50 z-40 transition-opacity"
              onClick={() => setExpanded(false)}
            />
          )}
          
          <div
            className={`fixed bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-slate-200 transition-all duration-300 overflow-hidden ${
              expanded
                ? "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-[1200px] h-[90vh]"
                : "bottom-6 right-6 w-[420px] h-[600px] text-sm"
            }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-2xl">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-full bg-white/20 flex items-center justify-center">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm">AI Assistant</h3>
                <p className="text-xs text-blue-100">
                  Powered by Intelligent Insights
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setExpanded(!expanded)}
                className="h-8 w-8 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                aria-label={expanded ? "Collapse" : "Expand"}
              >
                {expanded ? (
                  <Minimize2 className="h-4 w-4" />
                ) : (
                  <Maximize2 className="h-4 w-4" />
                )}
              </button>
              <button
                onClick={() => setOpen(false)}
                className="h-8 w-8 rounded-full hover:bg-white/20 flex items-center justify-center transition-colors"
                aria-label="Close chat"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 bg-slate-50">
            {messages.map((m) => (
              <div
                key={m.id}
                className={cn(
                  "flex gap-3",
                  m.role === "user" ? "justify-end" : "justify-start",
                )}
              >
                {m.role === "assistant" && (
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center shrink-0 mt-1">
                    <Sparkles className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={cn(
                    "rounded-2xl px-4 py-3",
                    m.role === "user"
                      ? "bg-blue-600 text-white rounded-br-md max-w-fit"
                      : "bg-white text-slate-900 border border-slate-200 rounded-bl-md w-full",
                  )}
                >
                  <div className="prose prose-sm max-w-none prose-slate prose-headings:font-semibold prose-p:leading-relaxed prose-ul:my-2 prose-li:my-1 prose-code:bg-slate-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-table:border-collapse prose-table:w-full prose-th:border prose-th:border-slate-300 prose-th:bg-slate-100 prose-th:px-3 prose-th:py-2 prose-th:text-left prose-th:font-semibold prose-td:border prose-td:border-slate-300 prose-td:px-3 prose-td:py-2">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {m.content}
                    </ReactMarkdown>
                  </div>
                  <div
                    className={cn(
                      "text-xs mt-2 opacity-70",
                      m.role === "user" ? "text-blue-100" : "text-slate-500",
                    )}
                  >
                    {new Date(m.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>
                {m.role === "user" && (
                  <div className="h-8 w-8 rounded-full bg-slate-300 flex items-center justify-center shrink-0 mt-1">
                    <User className="h-4 w-4 text-slate-600" />
                  </div>
                )}
              </div>
            ))}

            {typing && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center shrink-0 mt-1">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex gap-1">
                    <span
                      className="h-2 w-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    />
                    <span
                      className="h-2 w-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <span
                      className="h-2 w-2 bg-slate-400 rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              </div>
            )}

            <div ref={endRef} />
          </div>

          {/* Input */}
          <div className="px-4 py-4 border-t border-slate-200 bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
                placeholder="Ask me anything..."
                className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
              <button
                onClick={() => send()}
                disabled={!input.trim() || typing}
                className="h-10 w-10 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white flex items-center justify-center transition-colors"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2 px-1">
              AI responses are for guidance only. Verify all information before
              use.
            </p>
          </div>
        </div>
        </>
      )}
    </ChatAPIContext.Provider>
  );
}
