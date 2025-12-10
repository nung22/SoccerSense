import { GoogleGenAI } from '@google/genai';
import { buildMatchReportPrompt } from './promptBuilder';
import type { GameEvent } from '@/interfaces/GameEvent';

// --- Configuration ---
const apiKey = import.meta.env.VITE_GEMINI_API_KEY as string;

if (!apiKey) {
  throw new Error("VITE_GEMINI_API_KEY is not set. Please check your .env.local file.");
}

const ai = new GoogleGenAI({ apiKey });

// If 2.5-flash-lite continues to give 503s, try switching back to "gemini-1.5-flash"
const model = "gemini-2.5-flash"; 

// --- Helper: Auto-Retry for Rate Limits (429) & Server Errors (503) ---
async function callGeminiWithRetry(prompt: string, isJson: boolean = false, retries = 3): Promise<string> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await ai.models.generateContent({
        model: model,
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        config: isJson ? { 
          responseMimeType: "application/json" 
        } : undefined,
      });

      // Safely access text
      const text = response.text ? response.text : "";
      if (!text) throw new Error("Empty response from AI");
      
      return text;

    } catch (error: any) {
      // Check for Rate Limit (429) OR Server Overload (503)
      const status = error.status || error.code;
      const isTransient = status === 429 || status === 503 || (error.message && (error.message.includes('429') || error.message.includes('503')));
      
      if (isTransient) {
        console.warn(`⚠️ API Issue (${status}). Retrying in ${(i + 1) * 2} seconds...`);
        // Wait: 2s, 4s, 6s...
        await new Promise(resolve => setTimeout(resolve, (i + 1) * 2000));
        continue; // Try again
      }
      throw error; // Crash if it's a permanent error (like 400 Bad Request or 401 Auth)
    }
  }
  throw new Error("Max retries exceeded. Please wait a moment.");
}

// --- Main Function: Generate Match Report ---
export async function generateMatchReport(events: GameEvent[], tone: string): Promise<{ summary: string, key_moments: number[] }> {
  const prompt = buildMatchReportPrompt(events, tone);
  
  // 1. Get raw text (Retries automatically if needed)
  let jsonText = await callGeminiWithRetry(prompt, true);

  // 2. Clean Markdown: Remove ```json and ``` if AI adds them
  jsonText = jsonText.replace(/```json|```/g, '').trim();

  try {
    const data = JSON.parse(jsonText);
    
    // --- ROBUST PARSING LOGIC ---
    // This handles cases where AI ignores instructions and uses old keys
    
    // 1. Summary: Check 'summary' first, fallback to 'justification'
    const summaryText = data.summary || data.justification || "No summary generated.";

    // 2. Key Moments: Check 'key_moments', fallback to 'key_action'
    let rawMoments = data.key_moments || data.key_action || [];
    let momentIds: number[] = [];

    // Handle Array format: [300, 303]
    if (Array.isArray(rawMoments)) {
      momentIds = rawMoments.map((id: any) => Number(id)); 
    } 
    // Handle String format: "ID_300, ID_303" (Fallback)
    else if (typeof rawMoments === 'string') {
      const matches = rawMoments.match(/\d+/g);
      if (matches) {
        momentIds = matches.map(Number);
      }
    }

    return {
      summary: summaryText,
      key_moments: momentIds
    };

  } catch (e) {
    console.error("JSON Parse Failed. Raw text was:", jsonText);
    return { 
      summary: `Error parsing report output. Raw text: ${jsonText.substring(0, 100)}...`, 
      key_moments: [] 
    };
  }
}