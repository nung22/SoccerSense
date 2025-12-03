<script setup lang="ts">
import type { GameEvent } from '@/interfaces/GameEvent';

// Props: Data passed down from the parent view
defineProps<{
  events: GameEvent[];
  players: string[];
  selectedEvent: GameEvent;
  selectedTone: string;
  focusPlayer: string;
}>();

// Emits: Signals sent up to the parent when user changes settings
defineEmits<{
  (e: 'update:selectedEvent', value: GameEvent): void;
  (e: 'update:selectedTone', value: string): void;
  (e: 'update:focusPlayer', value: string): void;
}>();
</script>

<template>
  <div class="controls-container">
    <div class="control-group">
      <label>Select Game Event (C2):</label>
      <select 
        :value="selectedEvent.id" 
        @change="$emit('update:selectedEvent', events.find(e => e.id === +($event.target as HTMLSelectElement).value)!)"
      >
        <option v-for="event in events" :key="event.id" :value="event.id">
          {{ event.time_min }}' - {{ event.event_type }} ({{ event.primary_player }})
        </option>
      </select>
      <small class="context-preview">Context: "{{ selectedEvent.motion_context }}"</small>
    </div>

    <div class="control-group">
      <label>Narrative Tone (C3):</label>
      <div class="radio-group">
        <label v-for="tone in ['Celebratory', 'Critical', 'Neutral']" :key="tone">
          <input 
            type="radio" 
            name="tone" 
            :value="tone" 
            :checked="selectedTone === tone"
            @change="$emit('update:selectedTone', tone)"
          />
          {{ tone }}
        </label>
      </div>
    </div>

    <div class="control-group">
      <label>Focus Player (C3):</label>
      <select 
        :value="focusPlayer" 
        @change="$emit('update:focusPlayer', ($event.target as HTMLSelectElement).value)"
      >
        <option v-for="player in players" :key="player" :value="player">
          {{ player }}
        </option>
      </select>
    </div>
  </div>
</template>

<style scoped>
.controls-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #343a40;
}

.context-preview {
  display: block;
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
  margin-top: 0.25rem;
}

select, input[type="radio"] {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ced4da;
}

.radio-group {
  display: flex;
  gap: 1rem;
}
</style>