export interface GameEvent {
  id: number;
  event_type: 'Goal' | 'Pass' | 'Foul' | 'Save';
  time_min: number;
  primary_player: string;
  secondary_player: string;
  // C2: Simulated output from a motion prediction model (e.g., FootBots)
  motion_context: string;
  team: 'Home' | 'Away';
}