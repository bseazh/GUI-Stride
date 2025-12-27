
import { GoogleGenAI } from "@google/genai";
import { SearchParams } from "../types";

export const performAutomatedSearch = async (params: SearchParams): Promise<string> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
  
  const focusItem = params.items.find(i => i.id === params.focusItemId);
  const itemsDescription = params.items.map(item => 
    `${item.id === params.focusItemId ? '[PRIORITY] ' : ''}- Merchant: ${item.merchantName || 'Unknown'}, Product: ${item.productFullName || 'Unnamed'}, Price: ${item.price || 'N/A'}`
  ).join('\n');

  const prompt = `
    You are a market research assistant. 
    Platform Target: ${params.platform}
    Number of Search Results per Item: ${params.searchCount}
    
    The user wants a deep-dive analysis focusing specifically on: 
    ${focusItem ? `"${focusItem.productFullName}" from "${focusItem.merchantName}"` : "all items"}.

    Items to Analyze:
    ${itemsDescription}

    Please simulate an automated search and return a detailed market intelligence report in Markdown format. 
    1. Provide a comprehensive price comparison for the priority item.
    2. Check for authenticity flags on ${params.platform} relative to the official merchant.
    3. Briefly summarize the other items in the context of market trends.
    4. Provide actionable recommendations.
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        temperature: 0.7,
        topK: 40,
        topP: 0.95,
      }
    });

    return response.text || "No results generated.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    throw new Error("Failed to process search. Please check your network or API key.");
  }
};
