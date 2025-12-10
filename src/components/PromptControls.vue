<script setup lang="ts">
import type { GameEvent } from '@/interfaces/GameEvent';

// Props
const props = defineProps<{
  events: GameEvent[];
  players: string[];
  selectedEvent: GameEvent;
}>();

// Emits
const emit = defineEmits<{
  (e: 'update:selectedEvent', value: GameEvent): void;
}>();

// --- Helper function to ensure type safety ---
function onEventChange(payload: Event) {
  const target = payload.target as HTMLSelectElement;
  const newId = Number(target.value);
  
  // Find the event in the list
  const foundEvent = props.events.find(e => e.id === newId);
  
  // Only emit if we actually found a valid GameEvent
  if (foundEvent) {
    emit('update:selectedEvent', foundEvent);
  }
}
</script>

<template>
  <div class="controls-container">
    <div class="header">
      <h4>Map Controls</h4>
    </div>

    <div class="control-group">
      <label>Select Event to Visualize:</label>
      <select 
        :value="selectedEvent.id" 
        @change="onEventChange"
      >
        <option v-for="event in events" :key="event.id" :value="event.id">
          {{ event.time_min }}' - {{ event.event_type }} ({{ event.primary_player }})
        </option>
      </select>
      
      <small class="context-preview">
        <strong>Context:</strong> {{ selectedEvent?.motion_context || 'No context available' }}
      </small>
    </div>
  </div>
</template>

<style scoped>
.controls-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background-color: #ffffff; /* Cleaner white background */
  border-radius: 8px;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header h4 {
  margin: 0;
  color: #495057;
  font-size: 1rem;
  border-bottom: 2px solid #6f42c1; /* Purple accent */
  display: inline-block;
  padding-bottom: 5px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #343a40;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.context-preview {
  display: block;
  font-size: 0.8rem;
  color: #28a745; /* Green for "Data Driven" feel */
  background: #f1f3f5;
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 3px solid #28a745;
  margin-top: 0.25rem;
}

select {
  padding: 0.6rem;
  border-radius: 4px;
  border: 1px solid #ced4da;
  font-size: 0.95rem;
}

select:focus {
  outline: none;
  border-color: #6f42c1;
  box-shadow: 0 0 0 3px rgba(111, 66, 193, 0.1);
}
</style>