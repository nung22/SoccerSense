export interface GameEvent {
  id: number;
  event_type: 'Goal' | 'Pass' | 'Foul' | 'Save';
  time_min: number;
  primary_player: string;
  secondary_player: string;
  motion_context: string;
  team: string;
  
  // New Visual Data
  attacker_x?: number; // Optional in case data is missing
  attacker_y?: number;
  defender_x?: number;
  defender_y?: number;
  teammates?: Array<{ x: number; y: number }>;
  opponents?: Array<{ x: number; y: number }>;
  has_tracking?: boolean;
}