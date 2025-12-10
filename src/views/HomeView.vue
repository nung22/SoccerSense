<script setup lang="ts">
import { ref, computed } from "vue";
import realEvents from "@/data/realEvents.json";
import { generateMatchReport } from "@/api/llmService";
import PromptControls from "@/components/PromptControls.vue";
import NarrativeDisplay from "@/components/NarrativeDisplay.vue";
import PitchMap from "@/components/PitchMap.vue";
import RosterTable from "@/components/RosterTable.vue";
import type { GameEvent } from "@/interfaces/GameEvent";

// State
const eventsList = realEvents as unknown as GameEvent[];

// We keep selectedEvent so the Map and Controls still work!
const selectedEvent = ref(eventsList[0]);
const selectedTone = ref("Neutral");

const narrativeText = ref(
  "Select a Tone and click Generate to analyze the full match."
);
const isLoading = ref(false);

// Derived state for the players dropdown
const allPlayers = computed(() => {
  const players = new Set<string>();
  eventsList.forEach((e) => {
    if (e.primary_player) players.add(e.primary_player);
    if (e.secondary_player) players.add(e.secondary_player);
  });
  return Array.from(players).sort();
});

// New State for the clickable links
const keyMomentIds = ref<number[]>([]);

async function handleMatchReport() {
  isLoading.value = true;
  narrativeText.value = "";
  keyMomentIds.value = []; // Reset

  try {
    const result = await generateMatchReport(eventsList, selectedTone.value);
    narrativeText.value = result.summary;
    keyMomentIds.value = result.key_moments;
  } catch (error) {
    // ... error handling
  } finally {
    isLoading.value = false;
  }
}

function jumpToEvent(id: number) {
  const evt = eventsList.find((e) => e.id === id);
  if (evt) {
    selectedEvent.value = evt;
    document
      .querySelector(".visual-context")
      ?.scrollIntoView({ behavior: "smooth" });
  }
}
</script>

<template>
  <div class="home-view">
    <div class="header-section">
      <header class="branding">
        <h1>SoccerSense <span class="badge">Demo Mode</span></h1>
        <p style="font-size: 1.3rem; font-style: italic; color: grey; margin-top: -.2rem;">Automated Match Summarization & Tactical Visualization</p>
      </header>

      <div class="control-panel">
        <div class="map-controls">
          <PromptControls
            v-if="selectedEvent"
            v-model:selectedEvent="selectedEvent"
            v-model:selectedTone="selectedTone"
            :events="eventsList"
            :players="allPlayers"
          />
        </div>

        <div class="action-stack">
          <div class="info-box">
            <strong>Instructions:</strong> Use controls to explore events. Select a tone below to customize your report.
          </div>
          
          <div class="tone-selector">
            <label>Report Tone:</label>
            <select v-model="selectedTone">
              <option>Neutral</option>
              <option>Celebratory</option>
              <option>Critical</option>
              <option>Tactical</option>
              <option>Humorous</option>
            </select>
          </div>
          
          <button
            @click="handleMatchReport"
            :disabled="isLoading"
            class="report-btn"
          >
            📝 Generate Full Match Report
          </button>
        </div>
      </div>
    </div>
      
    <main class="grid-layout">
      <section class="input-section">
        <RosterTable :events="eventsList" />

        <div class="visual-context">
          <h3>
            Context: {{ selectedEvent?.event_type }} ({{
              selectedEvent?.time_min
            }}')
          </h3>
          <PitchMap v-if="selectedEvent" :gameEvent="selectedEvent" />
        </div>
      </section>

      <section class="output-section">
        <NarrativeDisplay :narrative="narrativeText" :isLoading="isLoading" />
        <div v-if="keyMomentIds.length > 0" class="highlights-bar">
          <h4>Key Moments</h4>
          <div class="chips">
<button
              v-for="(id, index) in keyMomentIds"
              :key="id"
              @click="jumpToEvent(id)"
              class="moment-chip"
            >
              ⭐ Highlight #{{ index + 1 }}
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  font-family: "Inter", sans-serif;
}

.header-section {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 9rem;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #dee2e6;
}

.branding {
  flex: 0 0 40%;
}

.control-panel {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

.action-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* --- TONE SELECTOR STYLES --- */
.tone-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
}

.tone-selector label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #495057;
  white-space: nowrap;
}

.tone-selector select {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 1rem;
  color: #212529;
  cursor: pointer;
}
.tone-selector select:focus {
  outline: none;
}
/* ---------------------------- */

header {
  text-align: left;
  margin-top: 3rem;
}

h1 {
  font-size: 4.1rem;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
  margin-top: 0;
}

.badge {
  background: #6f42c1;
  color: white;
  font-size: 1rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  vertical-align: middle;
}

.info-box {
  background: #e9ecef;
  padding: 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #495057;
  border-left: 4px solid #6f42c1;
  line-height: 1.4;
}

.report-btn {
  width: 100%;
  padding: 1rem;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.report-btn:hover:not(:disabled) {
  background-color: #59359a;
}

.report-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.visual-context {
  margin-top: 2rem;
}
.visual-context h3 {
  font-size: 1.1rem;
  color: #495057;
  margin-bottom: 0.5rem;
}

.highlights-bar {
  margin-top: 1rem;
  padding: 1rem;
  background: #f1f3f5;
  border-radius: 8px;
}
.moment-chip {
  margin-right: 0.5rem;
  padding: 0.5rem 1rem;
  background: #fff;
  border: 1px solid #6f42c1;
  color: #6f42c1;
  border-radius: 20px;
  cursor: pointer;
}
.moment-chip:hover {
  background: #6f42c1;
  color: white;
}

@media (max-width: 1024px) {
  .header-section {
    flex-direction: column;
    gap: 2rem;
  }
  .branding {
    width: 100%;
    text-align: center;
  }
  .control-panel {
    width: 100%;
    grid-template-columns: 1fr;
  }
  .grid-layout {
    grid-template-columns: 1fr;
  }
}
</style>