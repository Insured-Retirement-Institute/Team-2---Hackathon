import { createContext, useContext } from "react";
import type { ChatContext } from "@/types/chat";

type ChatContextAPI = {
  sendContext: (ctx: ChatContext) => void;
};

export const ChatAPIContext = createContext<ChatContextAPI>({ sendContext: () => {} });
export const useChatContext = () => useContext(ChatAPIContext);
