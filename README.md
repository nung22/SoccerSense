# SoccerSense ⚽🧠

**Context-Aware Sports Narrative Generator**

SoccerSense is an AI-powered analytics dashboard that transforms raw soccer data into rich, expert-level commentary. By grounding Large Language Models (LLMs) in physical tracking data, it eliminates hallucinations and generates tactical, physically accurate match reports.

---

## 🚀 Key Features

- **Automated Match Reports**: Generates 3-paragraph post-game summaries using Google Gemini 2.5 Flash-Lite.
- **Tactical Grounding**: Calculates real "Motion Context" (e.g., High Pressure: 0.5m separation) using 25Hz player tracking data to prevent AI hallucinations.
- **Interactive Visualization**: A dynamic 2D Pitch Map that visualizes the exact state of play for every key moment (Attacker vs. Defender positioning).
- **Deep Linking**: "Key Moment" chips in the report instantly update the map to visualize the specific play described in the text.
- **Tone Personalization**: Users can toggle narrative styles (e.g., Tactical, Celebratory, Critical) to change the AI's vocabulary and focus.
- **Accessibility**: Built-in Text-to-Speech (TTS) engine for audio commentary.

---

## 🛠️ Tech Stack

### Frontend

- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Scoped CSS / Flexbox & Grid Layouts

### Backend & Data Engineering

- **Language**: Python 3.9+
- **Libraries**: `kloppy` (Sports Tracking), `pandas` (Data Analysis)
- **Data Source**: Metrica Sports Open Data (Events + 25Hz Tracking)

### AI & Cloud

- **Model**: Google Gemini 2.5 Flash-Lite
- **API**: Google GenAI SDK
- **Strategy**: Zero-Shot Prompting with Strict Schema Constraints (JSON Mode)

---

## 📦 Installation & Setup

### 1. Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- A Google Gemini API Key

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/soccersense.git
cd soccersense
```

### 3. Backend Setup (Data Processing)

We use a Python script to ingest raw Metrica data, sync the tracking frames, and calculate spatial context.
```bash
# Install Python dependencies
pip install pandas kloppy

# Run the ETL script
# This fetches data, applies player name mappings (Messi/Ronaldo), and generates src/data/realEvents.json
python scripts/process_data.py
```

### 4. Frontend Setup
```bash
# Install Node dependencies
npm install

# Create environment file
touch .env.local
```

Open `.env.local` and add your API key:
```
VITE_GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Application
```bash
npm run dev
```

Open your browser to `http://localhost:5173`.

---

## 🎮 Usage Guide

1. **Generate Report**: Select a Tone (e.g., "Tactical") from the dropdown on the right and click "Generate Full Match Report".
2. **Read & Listen**: The AI will generate a summary. Click the "Listen" button to hear it read aloud.
3. **Explore Highlights**: Click the "Key Moment #X" buttons below the text. The Pitch Map on the left will jump to that specific goal, showing the calculated positioning of the attacker (Blue) and defender (Red).
4. **Check Stats**: Review the Roster Table to see the goal stats derived from the event data.

---

## 🏗️ Architecture

1. **Data Ingestion (Python)**: `kloppy` loads the Metrica Match 2 dataset. We filter for goals and synchronize the event timestamp with the 25Hz tracking frame.

2. **Context Calculation**: We compute the Euclidean distance between the ball carrier and the nearest opponent. This generates a "Context String" (e.g., "High Pressure, 1.2m away").

3. **Prompt Engineering**: The frontend sends this structured JSON to Gemini with strict instructions to generate a summary and identify key moment IDs.

4. **Rendering**: Vue renders the narrative and uses the returned IDs to link the text back to the visualization state.