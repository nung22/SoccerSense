<script setup lang="ts">
import { ref, computed } from 'vue';
import { demoEvents } from '@/data/demoEvents';
import { buildPrompt } from '@/api/promptBuilder';
import { generateNarrativeTwoStage } from '@/api/llmService';
// import { generateNarrativeMock } from '@/api/llmService';
import PromptControls from '@/components/PromptControls.vue';
import NarrativeDisplay from '@/components/NarrativeDisplay.vue';

// State
const selectedEvent = ref(demoEvents[0]);
const selectedTone = ref('Neutral');
const focusPlayer = ref(demoEvents[0].primary_player);
const narrativeText = ref('Select options and click Generate to see the AI output.');
const isLoading = ref(false);

// Derived state for the players dropdown (unique list)
const allPlayers = computed(() => {
  const players = new Set<string>();
  demoEvents.forEach(e => {
    players.add(e.primary_player);
    players.add(e.secondary_player);
  });
  return Array.from(players);
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
          :events="demoEvents"
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