import type { ChatRequest, ChatResponse } from "@/types/chat";
import { logRequest, logResponse } from "./logger";
import { KNOWLEDGE_BASE } from "./knowledge-base";
import {
  BedrockRuntimeClient,
  InvokeModelWithResponseStreamCommand,
} from "@aws-sdk/client-bedrock-runtime";

const AWS_REGION = import.meta.env.VITE_AWS_REGION || "us-east-1";
const BEDROCK_MODEL_ID = import.meta.env.VITE_BEDROCK_MODEL_ID || "global.anthropic.claude-opus-4-5-20251101-v1:0";

function getBedrockClient() {
  const accessKeyId = import.meta.env.VITE_AWS_ACCESS_KEY_ID;
  const secretAccessKey = import.meta.env.VITE_AWS_SECRET_ACCESS_KEY;
  const sessionToken = import.meta.env.VITE_AWS_SESSION_TOKEN;

  if (!accessKeyId || !secretAccessKey) {
    throw new Error("AWS credentials not configured. Please set VITE_AWS_ACCESS_KEY_ID and VITE_AWS_SECRET_ACCESS_KEY in .env.local");
  }

  return new BedrockRuntimeClient({
    region: AWS_REGION,
    credentials: {
      accessKeyId,
      secretAccessKey,
      sessionToken,
    },
  });
}

function extractTextFromChunk(chunk: any): string {
  if (chunk.chunk?.bytes) {
    const decoder = new TextDecoder();
    const body = JSON.parse(decoder.decode(chunk.chunk.bytes));
    if (body.type === "content_block_delta") {
      const delta = body.delta;
      if (delta?.type === "text_delta") {
        return delta.text || "";
      }
    }
  }
  return "";
}

/**
 * Chat with Bedrock streaming
 */
export async function sendChat(
  request: ChatRequest,
  onChunk?: (text: string) => void
): Promise<ChatResponse> {
  logRequest("Bedrock chat", request);

  // Context-only: no response needed
  if (!request.message) {
    return {};
  }

  // Build messages for Claude
  const messages = [];
  if (request.history) {
    for (const msg of request.history.slice(-15)) {
      messages.push({ role: msg.role, content: msg.content });
    }
  }
  if (request.message) {
    messages.push({ role: "user", content: request.message });
  }

  // System prompt with context
  let systemPrompt = KNOWLEDGE_BASE;
  
  if (request.context) {
    systemPrompt += `\n\n## Current Page Context\n${JSON.stringify(request.context, null, 2)}`;
  }

  console.log("🚀 Calling Bedrock:", {
    model: BEDROCK_MODEL_ID,
    region: AWS_REGION,
    messageCount: messages.length,
  });

  const command = new InvokeModelWithResponseStreamCommand({
    modelId: BEDROCK_MODEL_ID,
    contentType: "application/json",
    body: JSON.stringify({
      anthropic_version: "bedrock-2023-05-31",
      max_tokens: 2000,
      system: systemPrompt,
      messages,
      temperature: 0.7,
    }),
  });

  try {
    const bedrockClient = getBedrockClient();
    const response = await bedrockClient.send(command);
    console.log("✅ Bedrock response received, streaming...");
    let fullContent = "";

    if (response.body) {
      for await (const chunk of response.body) {
        const text = extractTextFromChunk(chunk);
        if (text) {
          fullContent += text;
          if (onChunk) {
            onChunk(text);
          }
        }
      }
    }

    console.log("✅ Streaming complete, total length:", fullContent.length);

    const result: ChatResponse = {
      message: {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: fullContent,
        timestamp: new Date().toISOString(),
      },
    };
    logResponse("Bedrock chat", result);
    return result;
  } catch (error) {
    console.error("❌ Bedrock error:", error);
    throw error;
  }
}
