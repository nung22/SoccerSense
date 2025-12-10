import type { GameEvent } from '@/interfaces/GameEvent';

export function buildMatchReportPrompt(events: GameEvent[], tone: string): string {
  // We keep the ID_ prefix in the input so the AI can clearly reference them
  const eventsSummary = events.map(e => 
    `ID_${e.id}: Min ${e.time_min}, ${e.event_type} by ${e.primary_player} (${e.team}). Context: ${e.motion_context}`
  ).join('\n');

  return `
    You are a world-class sports analyst and journalist.
    TONE: ${tone}
    EVENTS:
    ${eventsSummary}
    
    TASK: Output a valid JSON object with EXACTLY these two fields:
    1. "summary": A 3-paragraph match report narrative highlighting the overall tactical story revealed by the context. Ensure the article does not sound robotic, is well-written, and uses varied vocabulary.
    2. "key_moments": An array of integers (e.g., [300, 303]) representing the IDs of the 3 most important events.

    IMPORTANT CONSTRAINTS:
    - Use the key "summary". Do NOT use "justification".
    - Use the key "key_moments". Do NOT use "key_action".
    - The "key_moments" array must contain NUMBERS only, not strings (e.g., [300, 303], NOT ["ID_300", "ID_303"]).
    - Output RAW JSON only. Do not wrap it in markdown code blocks (no \`\`\`json).
  `;
}