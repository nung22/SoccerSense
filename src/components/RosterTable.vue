<script setup lang="ts">
import { computed } from 'vue';
import type { GameEvent } from '@/interfaces/GameEvent';

const props = defineProps<{
  events: GameEvent[];
}>();

// Calculate stats dynamically from the events list
const playerStats = computed(() => {
  const stats: Record<string, { team: string, goals: number }> = {};

  props.events.forEach(e => {
    // Initialize primary player
    if (!stats[e.primary_player]) {
      stats[e.primary_player] = { team: e.team, goals: 0 };
    }
    
    // Count goals
    if (e.event_type === 'Goal') {
      stats[e.primary_player]!.goals++;
    }
  });

  // Convert to array and sort by goals
  return Object.entries(stats)
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.goals - a.goals);
});
</script>

<template>
  <div class="roster-container">
    <h3>Match Stats</h3>
    <table>
      <thead>
        <tr>
          <th>Player</th>
          <th>Team</th>
          <th>Goals</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in playerStats" :key="p.name">
          <td>{{ p.name }}</td>
          <td>{{ p.team }}</td>
          <td>{{ p.goals }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.roster-container {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
th, td {
  padding: 0.75rem;
  border-bottom: 1px solid #dee2e6;
  text-align: left;
}
th {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>