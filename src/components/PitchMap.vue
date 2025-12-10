<script setup lang="ts">
import type { GameEvent } from '@/interfaces/GameEvent';

defineProps<{
  gameEvent: GameEvent;
}>();
</script>

<template>
  <div class="pitch-container" v-if="gameEvent.has_tracking">
    <div class="pitch">
      <div class="half-line"></div>
      <div class="center-circle"></div>
      <div class="box-left"></div>
      <div class="box-right"></div>
      
      <div class="goal-left"></div>
      <div class="goal-right"></div>

      <div 
        v-for="(tm, index) in gameEvent.teammates" 
        :key="'tm-'+index"
        class="player-dot teammate"
        :style="{ left: (tm.x * 100) + '%', top: (tm.y * 100) + '%' }"
      ></div>

      <div 
        v-for="(opp, index) in gameEvent.opponents" 
        :key="'opp-'+index"
        class="player-dot opponent"
        :style="{ left: (opp.x * 100) + '%', top: (opp.y * 100) + '%' }"
      ></div>

      <div 
        class="player-dot attacker-main"
        :style="{ left: (gameEvent.attacker_x! * 100) + '%', top: (gameEvent.attacker_y! * 100) + '%' }"
      >
        <span class="tooltip">Attacker</span>
      </div>

      <div 
        class="player-dot defender-main"
        :style="{ left: (gameEvent.defender_x! * 100) + '%', top: (gameEvent.defender_y! * 100) + '%' }"
      >
        <span class="tooltip">Primary Defender</span>
      </div>
    </div>
    <p class="caption">Tactical Snapshot at {{ gameEvent.time_min }}' <br>
      <span class="sub-caption">
        AI Context: {{ gameEvent.motion_context.split('.')[0] }}
      </span>
    </p>
  </div>
  
  <div v-else class="no-data">
    Visual tracking unavailable for this event.
  </div>
</template>

<style scoped>
.pitch-container {
  margin-top: 1rem;
  width: 100%;
}

.pitch {
  position: relative;
  width: 100%;
  aspect-ratio: 105/68; /* Standard pitch ratio */
  background-color: #4a9c59; /* Grass Green */
  border: 2px solid white;
  border-radius: 4px;
  overflow: hidden; /* Keeps players inside the box */
}

/* === PITCH MARKINGS CSS (Restored) === */
.half-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255,255,255,0.5);
  transform: translateX(-50%);
}

.center-circle {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 18%; /* Relative size */
  padding-bottom: 18%; /* Force circle aspect ratio */
  border: 2px solid rgba(255,255,255,0.5);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.box-left, .box-right {
  position: absolute;
  top: 50%;
  width: 16%;
  height: 40%;
  border: 2px solid rgba(255,255,255,0.5);
  transform: translateY(-50%);
}

.box-left {
  left: -2px; /* Hug the border */
}

.box-right {
  right: -2px; /* Hug the border */
}

/* === GOALS (New) === */
.goal-left, .goal-right {
  position: absolute;
  top: 50%;
  width: 4px;
  height: 11%; /* Roughly 7.32m goal on 68m width */
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0,0,0,0.1);
  transform: translateY(-50%);
  z-index: 1;
}

.goal-left {
  left: 0;
  box-shadow: 2px 0 5px rgba(0,0,0,0.2); /* Depth effect */
}

.goal-right {
  right: 0;
  box-shadow: -2px 0 5px rgba(0,0,0,0.2); /* Depth effect */
}

/* === PLAYER STYLES === */
.player-dot {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.5s ease;
  z-index: 10;
}

.teammate {
  background-color: #a6c4e8;
  border: 1px solid rgba(255,255,255,0.6);
}

.opponent {
  background-color: #e8a6a6;
  border: 1px solid rgba(255,255,255,0.6);
}

.attacker-main {
  width: 14px;
  height: 14px;
  background-color: #007bff;
  border: 2px solid white;
  z-index: 20;
  box-shadow: 0 0 10px rgba(0, 123, 255, 0.6);
}

.defender-main {
  width: 14px;
  height: 14px;
  background-color: #dc3545;
  border: 2px solid white;
  z-index: 20;
  box-shadow: 0 0 10px rgba(220, 53, 69, 0.6);
}

/* Tooltips */
.tooltip {
  visibility: hidden;
  position: absolute;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.85);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
  pointer-events: none;
}

.player-dot:hover .tooltip {
  visibility: visible;
}

.caption {
  text-align: center;
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 0.5rem;
}

.no-data {
  padding: 2rem;
  text-align: center;
  background: #f8f9fa;
  color: #adb5bd;
  border-radius: 8px;
}

.sub-caption {
  font-size: 0.75rem;
  color: #28a745; /* Green to show it's data-driven */
  font-weight: bold;
}
</style>