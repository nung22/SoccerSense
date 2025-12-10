import json
import pandas as pd
from kloppy import metrica

# Define the correct CSV URL for Sample Game 2 Events
EVENTS_CSV_URL = "https://raw.githubusercontent.com/metrica-sports/sample-data/master/data/Sample_Game_2/Sample_Game_2_RawEventsData.csv"

# --- 1. DEFINE FAKE NAMES MAPPING ---
# Map the Metrica Player IDs (e.g., 'Player10') to Famous Names
PLAYER_MAPPING = {
    # Home Team (e.g., Barcelona style)
    "Player1": "M. Ter Stegen",
    "Player2": "N. Semedo",
    "Player3": "G. Pique",
    "Player4": "I. Rakitic",
    "Player5": "S. Busquets",
    "Player6": "D. Suarez",
    "Player7": "L. Suarez",
    "Player8": "A. Iniesta",
    "Player9": "L. Suarez", # Duplicate handling if needed
    "Player10": "L. Messi",   # The GOAT
    "Player11": "O. Dembele",
    "Player12": "Rafinha",
    "Player13": "J. Cillessen",
    "Player14": "P. Coutinho",
    
    # Away Team (e.g., Real Madrid style)
    "Player15": "K. Navas",
    "Player16": "D. Carvajal",
    "Player17": "S. Ramos",
    "Player18": "R. Varane",
    "Player19": "L. Modric",
    "Player20": "G. Bale",
    "Player21": "Marcelo",
    "Player22": "Casemiro",
    "Player23": "T. Kroos",
    "Player24": "C. Ronaldo", # The Rival
    "Player25": "K. Benzema",
    "Player26": "Isco"
}

def analyze_motion_data(row, tracking_frame):
    """
    Returns a dictionary containing the narrative context AND the coordinates
    for the attacker, defender, and all other players.
    """
    # 1. Default / Error State
    default_result = {
        "context": "Motion data unavailable.",
        "attacker_x": 0.5, "attacker_y": 0.5,
        "defender_x": 0.0, "defender_y": 0.0,
        "teammates": [], "opponents": [],
        "has_tracking": False
    }

    if not tracking_frame:
        return default_result

    # 2. Identify Ball Carrier
    ball_carrier_id = row['From']
    
    # Logic to find ball carrier in tracking data
    # Try direct ID match or Name match
    ball_carrier = next((p for p in tracking_frame.players_coordinates.keys() 
                         if p.player_id == ball_carrier_id or p.name == ball_carrier_id), None)

    # Fallback: Try matching jersey number if ID/Name fails
    if not ball_carrier:
        try:
            p_num = ''.join(filter(str.isdigit, str(ball_carrier_id)))
            ball_carrier = next((p for p in tracking_frame.players_coordinates.keys() 
                                 if str(p.jersey_no) == p_num), None)
        except:
            pass
    
    if not ball_carrier:
        default_result["context"] = "Player positioning unclear."
        return default_result

    carrier_coords = tracking_frame.players_coordinates[ball_carrier]

    # 3. Identify Nearest Defender (The Context Generator)
    # We do this first so we know who to exclude from the general "opponents" list
    all_opps = [p for p in tracking_frame.players_coordinates if p.team != ball_carrier.team]
    nearest_opp_player = None
    min_dist = 100.0

    for opp in all_opps:
        opp_coords = tracking_frame.players_coordinates[opp]
        if opp_coords:
            # Metrica coords are 0-1. Pitch is ~105m x 68m.
            dist_x = (carrier_coords.x - opp_coords.x) * 105
            dist_y = (carrier_coords.y - opp_coords.y) * 68
            dist = (dist_x**2 + dist_y**2)**0.5
            
            if dist < min_dist:
                min_dist = dist
                nearest_opp_player = opp

    # 4. Loop through EVERYONE to build the visual lists
    teammates_coords = []
    opponents_coords = []

    for player, coords in tracking_frame.players_coordinates.items():
        # Skip the main attacker (already handled as primary focus)
        if player == ball_carrier:
            continue
        
        # Skip the main context defender (already handled as primary focus)
        if player == nearest_opp_player:
            continue
            
        # Add to appropriate list
        coord_obj = {"x": coords.x, "y": coords.y}
        
        if player.team == ball_carrier.team:
            teammates_coords.append(coord_obj)
        else:
            opponents_coords.append(coord_obj)

    # 5. Generate Narrative Context String
    context_str = ""
    if min_dist < 1.5:
        context_str = f"High pressure! Nearest defender was only {min_dist:.1f}m away."
    elif min_dist < 3.0:
        context_str = f"Moderate pressure. The attacker had {min_dist:.1f}m of space."
    else:
        context_str = f"Wide open. The defense lost the player ({min_dist:.1f}m separation)."

    # 6. Return Final Object
    return {
        "context": context_str,
        "attacker_x": carrier_coords.x,
        "attacker_y": carrier_coords.y,
        "defender_x": tracking_frame.players_coordinates[nearest_opp_player].x if nearest_opp_player else 0,
        "defender_y": tracking_frame.players_coordinates[nearest_opp_player].y if nearest_opp_player else 0,
        "teammates": teammates_coords, 
        "opponents": opponents_coords,
        "has_tracking": True
    }
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
            
        analysis = analyze_motion_data(row, related_frame)

        raw_player_id = str(row['From']) # e.g., "Player10"
        display_name = PLAYER_MAPPING.get(raw_player_id, raw_player_id) # Default to ID if not found
    
        game_event = {
            "id": i + 300, 
            "event_type": "Goal",
            "time_min": int(row['Start Time [s]'] / 60),
            "primary_player": display_name, 
            "secondary_player": "Team Effort", 
            "motion_context": analysis["context"],
            "team": str(row['Team']),
            
            # NEW FIELDS
            "attacker_x": analysis["attacker_x"],
            "attacker_y": analysis["attacker_y"],
            "defender_x": analysis["defender_x"],
            "defender_y": analysis["defender_y"],
            "teammates": analysis["teammates"],
            "opponents": analysis["opponents"],
            "has_tracking": analysis["has_tracking"]
        }
        
        output_events.append(game_event)
        print(f"   Processed Goal {i+1}: {analysis}")

    # Save to JSON
    output_path = 'src/data/realEvents.json'
    with open(output_path, 'w') as f:
        json.dump(output_events, f, indent=2)
    
    print(f"\nSuccess! Real data saved to {output_path}")

if __name__ == "__main__":
    main()