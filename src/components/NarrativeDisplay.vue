<script setup lang="ts">
import type { GameEvent } from "@/interfaces/GameEvent";

const props = defineProps<{
  narrative: string;
  // Made optional since Match Reports don't have one specific event
  gameEvent?: GameEvent; 
  isLoading: boolean;
}>();

function speakNarrative() {
  if (!props.narrative) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(props.narrative);
  window.speechSynthesis.speak(utterance);
}
</script>

<template>
  <div class="display-container">
    <div class="header-row">
      <h3>AI Generated Match Summary</h3>
      <button
        v-if="narrative && !isLoading"
        @click="speakNarrative"
        class="tts-btn"
        title="Read Aloud"
      >
        🔊 Listen
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <span class="bouncer">⚽</span> Analyzing full match data...
    </div>

    <div v-else class="content-state">
      <p class="narrative-text">{{ narrative }}</p>
      
      <div v-if="gameEvent" class="meta-info">
        <span>Based on event: {{ gameEvent.event_type }}</span>
        <span>Context: Calculated from Tracking Data</span>
      </div>
      
      <div v-else class="meta-info">
        <span>Scope: Full Match Summary</span>
        <span>Source: Metrica Tracking Data</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.display-container {
  padding: 2rem;
  border: 2px solid #6f42c1;
  border-radius: 8px;
  background-color: #fff;
  min-height: 150px;
}

h3 {
  margin-top: 0;
  color: #6f42c1;
}

.narrative-text {
  font-size: .9rem;
  line-height: 1.6;
  color: #212529;
  white-space: pre-wrap;
}

.meta-info {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
  font-size: 0.85rem;
  color: #868e96;
  display: flex;
  gap: 1rem;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 1rem; 
  color: hsl(208, 7%, 46%);
  height: 2rem;
}

/* NEW: BOUNCER STYLES */
.bouncer {
  display: inline-block;
  font-size: 1.5rem;
  animation: bounce 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite alternate;
}

/* NEW: BOUNCE KEYFRAMES */
@keyframes bounce {
  from {
    transform: translateY(0); /* Start at baseline */
  }
  to {
    transform: translateY(-12px); /* Move up 12 pixels */
  }
}

.tts-btn {
  background: #e9ecef;
  border: 1px solid #ced4da;
  border-radius: 20px;
  padding: 5px 15px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.tts-btn:hover {
  background: #dee2e6;
  transform: scale(1.05);
}
</style>
