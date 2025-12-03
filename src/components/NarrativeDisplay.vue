<script setup lang="ts">
import type { GameEvent } from '@/interfaces/GameEvent';

defineProps<{
  narrative: string;
  event: GameEvent;
  isLoading: boolean;
}>();
</script>

<template>
  <div class="display-container">
    <h3>AI Generated Commentary</h3>
    
    <div v-if="isLoading" class="loading-state">
      <span class="spinner">⚽</span> Generating insights...
    </div>
    
    <div v-else class="content-state">
      <p class="narrative-text">{{ narrative }}</p>
      <div class="meta-info">
        <span>Based on event: {{ event.event_type }}</span>
        <span>Context Used: Motion Analysis (FootBots Sim)</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.display-container {
  margin-top: 2rem;
  padding: 2rem;
  border: 2px solid #28a745;
  border-radius: 8px;
  background-color: #fff;
  min-height: 150px;
}

h3 {
  margin-top: 0;
  color: #28a745;
}

.narrative-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #212529;
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
  gap: 0.5rem;
  color: #6c757d;
  font-style: italic;
}

.spinner {
  animation: spin 1s infinite linear;
}

@keyframes spin { 
  from { transform: rotate(0deg); } 
  to { transform: rotate(360deg); } 
}
</style>