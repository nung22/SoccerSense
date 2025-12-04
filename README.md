# SoccerSense
**Context-Aware Generative AI for Sports Narratives**

> **CS 6180 Project - Fall 2025**
> *An implementation of grounded, controllable, and personalized Natural Language Generation (NLG) for sports analytics.*

---

## 📖 Overview

**SoccerSense** is a full-stack generative AI application that converts structured soccer match events into rich, human-like narratives. Unlike standard LLM wrappers that can hallucinate details, SoccerSense uses a **Two-Stage Generation Pipeline** grounded in mathematically calculated tracking data.

The system processes raw computer vision data (player coordinates) to determine "physical context" (e.g., defensive pressure) and uses this to constrain a Large Language Model (Gemini), allowing users to dynamically control the **Tone**, **Focus**, and **Perspective** of the commentary.

---

## 🚀 Key Contributions & Features

### 1. Simulated Context Integration (Grounding)
We do not rely on the LLM to interpret raw coordinates. Instead, we perform **offline feature engineering** using Python (`kloppy`, `pandas`) on the **Metrica Sports Open Dataset**.
* **Methodology:** We synchronize event logs with 25Hz tracking data to calculate the Euclidean distance between the ball carrier and the nearest defender at the moment of a goal.
* **Result:** A deterministic "Motion Context" string (e.g., *"High pressure! Nearest defender was only 0.5m away"*) is injected into the prompt, grounding the AI in physical reality.

### 2. Two-Stage Generative Pipeline (Reasoning vs. Styling)
To prevent robotic or hallucinated outputs, we implement a split-logic pipeline using the **Google Gemini API**:
* **Stage 1 (Reasoning):** The model analyzes the structured data and motion context to output a **JSON object** containing sentiment analysis and key action identification.
* **Stage 2 (Styling):** The model takes the Stage 1 JSON + User Preferences to generate the final narrative text.

### 3. Personalized Content Adaptation (Control)
Users can steer the generation without retraining the model via **Dynamic Prompt Engineering**.
* **Variables:** Tone (Celebratory, Critical, Neutral) and Focus Player.
* **Logic:** The prompt structure changes dynamically to re-orient the narrative perspective (e.g., focusing on a defender's failure vs. an attacker's success).

---

## 🛠️ Technology Stack

* **Frontend:** Vue 3 (Composition API), TypeScript, Vite.
* **AI Model:** Google Gemini (`gemini-2.5-flash`) via `@google/genai` SDK.
* **Data Engineering:** Python 3.12, `pandas`, `kloppy` (for tracking data standardization).
* **Data Source:** Metrica Sports Open Data (Match 2).

---

## 📂 Project Structure

```text
soccer-sense/
├── scripts/
│   └── process_data.py        # Python ETL pipeline (Raw Data -> JSON)
├── src/
│   ├── api/
│   │   ├── llmService.ts      # Two-Stage API logic
│   │   └── promptBuilder.ts   # Prompt engineering templates
│   ├── components/            # UI Components
│   ├── data/
│   │   └── realEvents.json    # The processed output from scripts/
│   └── views/
│       └── HomeView.vue       # Main UI Orchestration
└── README.md
```
---

## ⚡ Installation & Setup

### Prerequisites
* Node.js & Yarn
* Python 3.x (with `pip`)
* Google AI Studio API Key

### 1. Clone and Install Dependencies
```bash
git clone https://github.com/nung22/SoccerSense.git
cd soccer-sense

# Install Frontend Dependencies
yarn install
```

### 2. Run the Data Pipeline (Python)
This step downloads raw match data and calculates the "Motion Context" features.

```bash
# Install Python libraries
pip install kloppy pandas

# Run the ETL script
python scripts/process_data.py
```
*Output:* `Success! Real data saved to src/data/realEvents.json`

### 3. Configure API Key
Create a `.env.local` file in the project root:
```bash
VITE_GEMINI_API_KEY="[insert-your-key-here]"
```

### 4. Run the Application
```bash
yarn dev
```
Open your browser to http://localhost:5173.

## 🎮 How to Use
1. **Select Game Event:** Choose a real goal from the match. Note the Context string displayed below the dropdown—this is the mathematically calculated pressure derived from tracking data.

2. **Select Tone:** Choose the narrative style (e.g., Critical will emphasize mistakes, Celebratory will emphasize skill).

3. **Select Focus Player:** Choose who the camera should follow. Selecting "Team Effort" or a secondary player will shift the narrative perspective.

4. **Generate:** Click the button to trigger the Two-Stage AI pipeline.

## 📚 References & Inspiration
- **Metrica Sports:** For providing the open-source tracking and event datasets.

- **FootBots (ArXiv):** Inspired our approach to separating social/motion attention from trajectory prediction.

- **SoccerChat (ArXiv):** Inspired our instruction-tuning approach for domain-specific language generation.
