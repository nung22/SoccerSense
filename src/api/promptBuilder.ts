import type { GameEvent } from '@/interfaces/GameEvent';

// C1: Few-Shot Examples for style guidance (kept static)
const FEW_SHOT_NARRATIVE_EXAMPLES = `
  ---
  EXAMPLE ANALYSIS: {"sentiment": "positive", "key_action": "pass execution"}
  EXAMPLE NARRATIVE (Neutral): The effective pass opened up space in the midfield.
  ---
`;

export function buildAnalysisPrompt(event: GameEvent): string {
  // Stage 1: Ask the model to analyze the event and context. Output MUST be JSON.
  return `
    TASK: Analyze the following soccer event data and output a single JSON object.
    
    DATA:
    Event Type: ${event.event_type}
    Primary Player: ${event.primary_player}
    Contextual Motion Insight: ${event.motion_context}

    OUTPUT SCHEMA: { "sentiment": "positive" | "negative" | "neutral", "key_action": string, "justification": string }
  `;
}

export function buildNarrativePrompt(
  analysisJson: string, // Input from Stage 1
  tone: string,         // Input from UI (C3)
  focusPlayer: string   // Input from UI (C3)
): string {
  // Stage 2: Ask the model to apply the requested style to the analysis.
  
  const systemInstruction = `You are a world-class sports commentator. Your analysis MUST be written with a ${tone} tone and focused ONLY on the actions of ${focusPlayer}.`;

  return `
    ${systemInstruction}
    
    CONTEXTUAL ANALYSIS (JSON): ${analysisJson}
    
    ${FEW_SHOT_NARRATIVE_EXAMPLES}
    
    TASK: Using the JSON analysis provided above, generate a two-sentence narrative summary with the requested tone.
  `;
}