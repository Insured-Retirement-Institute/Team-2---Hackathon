export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

export type ChatContext = {
  page: string;
  alertId?: string;
  activeTab?: string;
  clientName?: string;
  policyId?: string;
  [key: string]: unknown;
};

export type ChatRequest = {
  context: ChatContext;
  message?: string;
  history?: ChatMessage[];
};

export type ChatResponse = {
  message?: ChatMessage;
};
