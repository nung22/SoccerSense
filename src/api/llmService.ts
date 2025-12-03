// src/api/llmService.ts
import { GoogleGenAI } from '@google/genai';
import { buildAnalysisPrompt, buildNarrativePrompt } from './promptBuilder';
import type { GameEvent } from '@/interfaces/GameEvent';
import type { AnalysisResult } from '@/interfaces/AnalysisResult'; // Assuming you define this interface

// --- Initialization ---
// Get API key from Vite environment variable (loaded from .env.local)
const apiKey = import.meta.env.VITE_GEMINI_API_KEY as string;

if (!apiKey) {
  throw new Error("VITE_GEMINI_API_KEY is not set. Please check your .env.local file.");
}

const ai = new GoogleGenAI({ apiKey });
const model = "gemini-2.5-flash"; // Fast and capable model for this task

// --- Core Two-Stage Logic ---

export async function generateNarrativeTwoStage(
  event: GameEvent,
  tone: string,
  focusPlayer: string
): Promise<string> {

  // Stage 1: Data Analysis (Reasoning)
  const analysisPrompt = buildAnalysisPrompt(event);
  
  console.log("Stage 1: Requesting Analysis...");

  const analysisResponse = await ai.models.generateContent({
      model: model,
      contents: [{ role: "user", parts: [{ text: analysisPrompt }] }],
      config: {
          responseMimeType: "application/json", // Crucial: Ask for JSON output
          responseSchema: {
            type: "OBJECT",
            properties: {
              sentiment: { type: "STRING", enum: ["positive", "negative", "neutral"] },
              key_action: { type: "STRING" },
              justification: { type: "STRING" },
            },
          },
      },
  });

  const analysisText = analysisResponse.text;

  if (!analysisText) {
    throw new Error("AI did not return any text. The response might have been blocked.");
  }
  
  // Parse the JSON output from Stage 1
  let analysisObject: AnalysisResult;
  try {
    analysisObject = JSON.parse(analysisText) as AnalysisResult;
    console.log("Stage 1 Result:", analysisObject);
  } catch (e) {
    console.error("Failed to parse analysis JSON:", analysisText);
    throw new Error("AI returned unparsable analysis. Please check prompt.");
  }


  // Stage 2: Narrative Generation (Styling)
  const narrativePrompt = buildNarrativePrompt(JSON.stringify(analysisObject), tone, focusPlayer);
  
  console.log("Stage 2: Requesting Narrative Generation...");

  const narrativeResponse = await ai.models.generateContent({
    model: model,
    contents: [{ role: "user", parts: [{ text: narrativePrompt }] }],
    // No specific JSON format needed here, we want plain text output.
  });

  // Final Output
  return `(AI Generated Two-Stage Commentary):\n\n${narrativeResponse.text}`;
}