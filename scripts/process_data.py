import json
import os
import pandas as pd
import requests
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
            "home_team": "PRIME Barcelona",
            "away_team": "PRIME Real Madrid",
            
            # NEW FIELDS
            "attacker_x": analysis["attacker_x"],
            "attacker_y": analysis["attacker_y"],
            "defender_x": analysis["defender_x"],
            "defender_y": analysis["defender_y"],
            "teammates": analysis["teammates"],
            "opponents": analysis["opponents"],
            "has_tracking": analysis["has_tracking"]
        }
        
        # --- COLLECT LAST 10 EVENTS LEADING UP TO THE GOAL ---
        timestamp = row['Start Time [s]']
        prior_events = events_df[events_df['Start Time [s]'] < timestamp].sort_values('Start Time [s]')
        last_10 = prior_events.tail(10)

        # Keep a compact representation of each prior event
        build_up = []
        for _, ev in last_10.iterrows():
            ev_obj = {
                'time_s': float(ev['Start Time [s]']),
                'time_min': int(ev['Start Time [s]'] / 60),
                'type': str(ev.get('Type', '')),
                'subtype': str(ev.get('Subtype', '')),
                'from': PLAYER_MAPPING.get(str(ev.get('From', '')), str(ev.get('From', ''))),
                'to': PLAYER_MAPPING.get(str(ev.get('To', '')), str(ev.get('To', ''))),
                'team': str(ev.get('Team', ''))
            }
            build_up.append(ev_obj)

        game_event['build_up_events'] = build_up

        output_events.append(game_event)
        print(f"   Processed Goal {i+1}: {analysis}")

        # --- PREPARE PROMPT FOR GEMINI (best-effort) ---
        prompt = prepare_gemini_prompt(game_event)

        # If gemini config provided, call API; otherwise persist payloads for review
        gemini_key = os.environ.get('GEMINI_API_KEY')
        gemini_endpoint = os.environ.get('GEMINI_ENDPOINT')
        if gemini_key and gemini_endpoint:
            try:
                send_to_gemini(prompt, gemini_endpoint, gemini_key)
            except Exception as e:
                print(f"Warning: failed to call Gemini API: {e}")
        else:
            # Save prompts locally for later ingestion
            payloads_path = os.path.join(os.path.dirname(__file__), 'gemini_payloads.json')
            save_gemini_payload(payloads_path, game_event['id'], prompt)

    # Save to JSON
    output_path = 'src/data/realEvents.json'
    with open(output_path, 'w') as f:
        json.dump(output_events, f, indent=2)
    
    print(f"\nSuccess! Real data saved to {output_path}")


def prepare_gemini_prompt(game_event: dict) -> str:
    """Create a plain-text prompt summarizing the goal and the preceding events
    for use with a generative model (Gemini)."""
    lines = []
    lines.append(f"Analyze the following goal event and its build-up. Provide an in-depth analysis of how the goal was scored, including who passed the ball, whether defenders were near the scorer, how many passes were in the build-up, and whether the scorer passed through defenders.")
    lines.append("")
    lines.append("GOAL EVENT:")
    lines.append(json.dumps({
        'id': game_event.get('id'),
        'time_min': game_event.get('time_min'),
        'primary_player': game_event.get('primary_player'),
        'team': game_event.get('team'),
        'motion_context': game_event.get('motion_context')
    }, indent=2))
    lines.append("")
    lines.append("BUILD-UP (most recent first):")
    for ev in reversed(game_event.get('build_up_events', [])):
        lines.append(json.dumps(ev))

    # Add tracking summary if available
    if game_event.get('has_tracking'):
        lines.append("")
        lines.append("TRACKING SUMMARY:")
        lines.append(json.dumps({
            'attacker_x': game_event.get('attacker_x'),
            'attacker_y': game_event.get('attacker_y'),
            'defender_x': game_event.get('defender_x'),
            'defender_y': game_event.get('defender_y'),
            'teammates_count': len(game_event.get('teammates', [])),
            'opponents_count': len(game_event.get('opponents', []))
        }, indent=2))

    lines.append("")
    lines.append("Please return a JSON object with these fields: 'summary', 'pass_sequence', 'pressure_assessment', 'key_players', 'recommendations'. Keep answers factual and reference the events and tracking data provided.")

    return "\n".join(lines)


def send_to_gemini(prompt: str, endpoint: str, api_key: str):
    """Send the prompt to a configured Gemini-like endpoint using a POST request.
    The `endpoint` should accept JSON {"prompt": "..."} and Bearer auth.
    This is intentionally generic to support different deployment setups.
    """
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = { 'prompt': prompt }
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    # You may wish to persist or process the response; here we print a truncated confirmation
    try:
        data = resp.json()
        print(f"Gemini response received (truncated): {str(data)[:200]}")
    except Exception:
        print(f"Gemini response status: {resp.status_code}")


def save_gemini_payload(path: str, event_id: int, prompt: str):
    """Append the prompt to a local JSON file for manual ingestion by a model or later processing."""
    entry = { 'event_id': event_id, 'prompt': prompt }
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved Gemini payload for event {event_id} to {path}")
    except Exception as e:
        print(f"Failed to save Gemini payload: {e}")

if __name__ == "__main__":
    main()