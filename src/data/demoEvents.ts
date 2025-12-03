import type { GameEvent } from '@/interfaces/GameEvent';

export const demoEvents: GameEvent[] = [
  {
    id: 1,
    event_type: 'Goal',
    time_min: 88,
    primary_player: 'A. Smith',
    secondary_player: 'J. Brown',
    motion_context: 'The defense was severely out of position due to a rapid tactical shift on the wing, leaving a massive gap in the center.',
    team: 'Home',
  },
  {
    id: 2,
    event_type: 'Pass',
    time_min: 45,
    primary_player: 'L. Messi',
    secondary_player: 'J. Alba',
    motion_context: 'Primary player utilized a low-risk, high-reward diagonal trajectory, bypassing three defenders who were over-committed.',
    team: 'Away',
  },
  {
    id: 3,
    event_type: 'Foul',
    time_min: 12,
    primary_player: 'M. Jones',
    secondary_player: 'R. Sterling',
    motion_context: 'Defensive player arrived late to the challenge with high velocity, failing to decelerate before contact.',
    team: 'Home',
  },
];