<script setup lang="ts">
import { ref, computed } from 'vue';
import realEvents from '@/data/realEvents.json';
import { generateNarrativeTwoStage } from '@/api/llmService';
import PromptControls from '@/components/PromptControls.vue';
import NarrativeDisplay from '@/components/NarrativeDisplay.vue';
import type { GameEvent } from '@/interfaces/GameEvent';

// State
// Cast the JSON to your Type
const eventsList = realEvents as unknown as GameEvent[]; 

const selectedEvent = ref(eventsList[0]);
const selectedTone = ref('Neutral');

// Initialize focus player with the primary player of the first event (Safe access)
const focusPlayer = ref(eventsList[0]?.primary_player || 'Unknown Player');

const narrativeText = ref('Select options and click Generate to see the AI output.');
const isLoading = ref(false);

// Derived state for the players dropdown (unique list from REAL data)
const allPlayers = computed(() => {
  const players = new Set<string>();
  eventsList.forEach(e => {
    // Only add valid player names
    if (e.primary_player) players.add(e.primary_player);
    if (e.secondary_player) players.add(e.secondary_player);
  });
  // Sort alphabetically for better UX
  return Array.from(players).sort();
});

async function handleGenerate() {
  isLoading.value = true;
  narrativeText.value = '';

  try {
    // Call the new, real two-stage API function
    const result = await generateNarrativeTwoStage(
      selectedEvent.value, 
      selectedTone.value, 
      focusPlayer.value
    );
    
    narrativeText.value = result;

  } catch (error) {
    narrativeText.value = `Error generating narrative: ${(error as Error).message}. Check the console for details.`;
    console.error(error);
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="home-view">
    <header>
      <h1>SoccerSense <span class="badge">AI Demo</span></h1>
      <p>Context-Aware Sports Narrative Generator</p>
    </header>

    <main class="grid-layout">
      <section class="input-section">
        <PromptControls 
          v-model:selectedEvent="selectedEvent"
          v-model:selectedTone="selectedTone"
          v-model:focusPlayer="focusPlayer"
          :events="eventsList"
          :players="allPlayers"
        />
        <button 
          @click="handleGenerate" 
          :disabled="isLoading" 
          class="generate-btn"
        >
          {{ isLoading ? 'Processing...' : 'Generate Narrative' }}
        </button>
      </section>

      <section class="output-section">
        <NarrativeDisplay 
          :narrative="narrativeText"
          :event="selectedEvent"
          :isLoading="isLoading"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Inter', sans-serif;
}

header {
  margin-bottom: 3rem;
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.badge {
  background: #28a745;
  color: white;
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  vertical-align: middle;
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
}

.generate-btn {
  margin-top: 1rem;
  width: 100%;
  padding: 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.generate-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .grid-layout {
    grid-template-columns: 1fr;
  }
}
</style>