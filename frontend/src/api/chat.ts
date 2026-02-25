import type { ChatRequest, ChatResponse } from "@/types/chat";
import { logRequest, logResponse } from "./logger";

const MOCK_RESPONSES: Record<string, string> = {
  product:
    "The Pacific Life 7-Year MYGA is a Multi-Year Guaranteed Annuity offering:\n\n• Guaranteed Rate: 4.2% for 7 years\n• Minimum Premium: $25,000\n• Surrender Charge Period: 7 years (declining)\n• Free Withdrawal: Up to 10% annually\n• Rate Lock: Guaranteed for entire term\n\nIdeal for clients seeking predictable growth and principal protection.",
  compare:
    "Here's a quick comparison:\n\n**Current Policy (Renewing)**\n• Rate dropping to 1.5% (minimum guarantee)\n• No surrender charges remaining\n• Full liquidity available\n\n**Recommended MYGA**\n• 4.2% guaranteed for 7 years\n• +2.7% rate advantage\n• 10% annual free withdrawal\n\nThe recommendation favors the new MYGA if the client has adequate emergency reserves.",
  suitability:
    "Key suitability factors to document:\n\n• Age and time horizon vs. annuity term\n• Liquidity needs and emergency reserves\n• Risk tolerance assessment\n• Investment objectives alignment\n• Tax situation considerations\n\nAlways ensure the recommendation serves the client's best interest.",
  client:
    "Here's how to explain the rate change:\n\n\"Your current policy rate drops from 2.5% to 1.5% at renewal — the minimum guarantee. We can move to a new policy at 4.2%, locked for 7 years. That's almost 3x higher.\n\nThe trade-off: a 7-year commitment, though you can withdraw 10% per year penalty-free.\"\n\nUse concrete dollar amounts and explain trade-offs honestly.",
  rate: "Rate Information:\n\n• Current renewal: 1.5% (minimum guaranteed)\n• Recommended MYGA: 4.2% guaranteed 7 years\n• Market range: 3.8% - 4.5% for 7-year MYGAs\n\nOn $125k:\n• Renewal: ~$1,875/year\n• New MYGA: ~$5,250/year\n• Difference: +$3,375 annually",
  compliance:
    "Compliance Requirements:\n\n• Best interest standard documentation\n• Suitability questionnaire signed\n• Comparison of alternatives documented\n• Client acknowledgment of key terms\n• Replacement forms if applicable (1035 exchange)\n• Supervisory review before submission\n\nConsult your compliance department when in doubt.",
};

function getMockResponse(message: string): string {
  const lower = message.toLowerCase();
  if (lower.includes("product") || lower.includes("myga"))
    return MOCK_RESPONSES.product;
  if (
    lower.includes("compare") ||
    lower.includes("renewal") ||
    lower.includes("option")
  )
    return MOCK_RESPONSES.compare;
  if (lower.includes("suitability") || lower.includes("suitable"))
    return MOCK_RESPONSES.suitability;
  if (lower.includes("client") || lower.includes("explain"))
    return MOCK_RESPONSES.client;
  if (lower.includes("rate") || lower.includes("interest"))
    return MOCK_RESPONSES.rate;
  if (lower.includes("compliance") || lower.includes("regulation"))
    return MOCK_RESPONSES.compliance;
  return "I can help with:\n\n• Product information and features\n• Renewal analysis and comparisons\n• Suitability guidance\n• Client communication tips\n• Compliance requirements\n• Rate comparisons\n\nWhat would you like to explore?";
}

/**
 * POST /api/chat/message
 *
 * Two use cases:
 * 1. Context-only (no message) — navigation/tab change beacon
 * 2. With message — user chat, includes history (last 15 Q&A pairs)
 */
export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  logRequest("POST /api/chat/message", request);

  // Context-only: no response needed
  if (!request.message) {
    const r = {};
    logResponse("POST /api/chat/message (context)", r);
    return new Promise((resolve) => setTimeout(() => resolve(r), 50));
  }

  return new Promise((resolve) => {
    setTimeout(
      () => {
        const r: ChatResponse = {
          message: {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: getMockResponse(request.message!),
            timestamp: new Date().toISOString(),
          },
        };
        logResponse("POST /api/chat/message", r);
        resolve(r);
      },
      600 + Math.random() * 400,
    );
  });
}
