// src/interfaces/AnalysisResult.ts
export interface AnalysisResult {
  sentiment: 'positive' | 'negative' | 'neutral';
  key_action: string;
  justification: string;
}