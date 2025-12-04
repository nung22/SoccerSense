import json
import pandas as pd
from kloppy import metrica

# Define the correct CSV URL for Sample Game 2 Events
EVENTS_CSV_URL = "https://raw.githubusercontent.com/metrica-sports/sample-data/master/data/Sample_Game_2/Sample_Game_2_RawEventsData.csv"

def generate_motion_context(row, tracking_frame):
    """
    Calculates the distance to the nearest opponent to generate a context string.
    """
    if not tracking_frame:
        return "Motion data unavailable for this timestamp."

    # In Metrica CSV, 'From' contains the player name (e.g., 'Player1')
    ball_carrier_id = row['From']
    
    # Kloppy formats player IDs as 'Player 1' or 'Player1' depending on version
    # We try to find the player object in the frame that matches the ID
    ball_carrier = next((p for p in tracking_frame.players_coordinates.keys() 
                         if p.player_id == ball_carrier_id or p.name == ball_carrier_id), None)

    if not ball_carrier:
        # Fallback: Try matching numbers if ID match fails (e.g., 'Player10' -> 10)
        try:
            p_num = ''.join(filter(str.isdigit, str(ball_carrier_id)))
            ball_carrier = next((p for p in tracking_frame.players_coordinates.keys() 
                                 if str(p.jersey_no) == p_num), None)
        except:
            pass
            
    if not ball_carrier:
        return "Player positioning unclear from tracking data."

    carrier_coords = tracking_frame.players_coordinates[ball_carrier]
    
    # Find nearest opponent
    opponents = [
        p for p in tracking_frame.players_coordinates 
        if p.team != ball_carrier.team
    ]
    
    if not opponents:
        return "No opponents tracked in frame."

    # Calculate distances
    distances = []
    for opp in opponents:
        opp_coords = tracking_frame.players_coordinates[opp]
        if opp_coords:
            # Metrica coords are 0-1. Pitch is ~105m x 68m.
            dist_x = (carrier_coords.x - opp_coords.x) * 105
            dist_y = (carrier_coords.y - opp_coords.y) * 68
            dist = (dist_x**2 + dist_y**2)**0.5
            distances.append(dist)
    
    min_dist = min(distances) if distances else 100.0
    
    # Generate Narrative (C2 Contribution)
    if min_dist < 1.5:
        return f"High pressure! Nearest defender was only {min_dist:.1f}m away, forcing a rapid decision."
    elif min_dist < 3.0:
        return f"Moderate pressure. The attacker had {min_dist:.1f}m of space to stabilize before the shot."
    else:
        return f"Wide open. The defense completely lost the player, leaving {min_dist:.1f}m of open grass."

def main():
    print("1. Loading Metrica Tracking Data (Match 2)...")
    # Kloppy handles the tracking data natively
    tracking_dataset = metrica.load_open_data(match_id=2)
    
    print("2. Loading Metrica Event Data (CSV)...")
    # Load events using Pandas directly from the CSV URL
    events_df = pd.read_csv(EVENTS_CSV_URL)
    
    print("3. Syncing Data and Processing Context...")
    
    # Filter for GOALS (Type: SHOT, Subtype: ON TARGET-GOAL)
    goals_df = events_df[
        (events_df['Type'] == 'SHOT') & 
        (events_df['Subtype'].str.contains('GOAL', na=False))
    ]
    
    output_events = []
    frame_rate = tracking_dataset.metadata.frame_rate
    
    print(f"   Found {len(goals_df)} goals.")

    for i, (_, row) in enumerate(goals_df.iterrows()):
        # Sync timestamp to frame
        timestamp = row['Start Time [s]']
        target_frame_id = int(timestamp * frame_rate)
        
        # Find the frame
        related_frame = None
        if target_frame_id < len(tracking_dataset.frames):
            related_frame = tracking_dataset.frames[target_frame_id]
            
        context_str = generate_motion_context(row, related_frame)
        
        # Structure for Vue App
        game_event = {
            "id": i + 300, 
            "event_type": "Goal",
            "time_min": int(timestamp / 60),
            "primary_player": str(row['From']), 
            "secondary_player": "Team Effort", 
            "motion_context": context_str,
            "team": str(row['Team'])
        }
        
        output_events.append(game_event)
        print(f"   Processed Goal {i+1}: {context_str}")

    # Save to JSON
    output_path = 'src/data/realEvents.json'
    with open(output_path, 'w') as f:
        json.dump(output_events, f, indent=2)
    
    print(f"\nSuccess! Real data saved to {output_path}")

if __name__ == "__main__":
    main()