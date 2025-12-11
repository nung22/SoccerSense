<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { GameEvent } from '@/interfaces/GameEvent';
import allEvents from '@/data/realEvents.json';
import PitchMap from '@/components/PitchMap.vue';
import { generateMatchReport } from '@/api/llmService';

// Load events and filter goals
const events = (allEvents as GameEvent[]);
const goals = events.filter(e => e.event_type === 'Goal');

const selectedGoalId = ref<number | null>(goals.length ? goals[0]!.id : null);
const router = useRouter();

function goHome() {
  router.push({ name: 'home' });
}
const selectedGoal = computed(() => goals.find(g => g.id === selectedGoalId.value) || null);

// Derived reactive summaries to use in template (avoid repeated function calls)
const assistName = computed(() => (selectedGoal.value ? inferAssist(selectedGoal.value) : null));
const passesCount = computed(() => (selectedGoal.value ? inferPassesInBuildUp(selectedGoal.value) : 0));
const nearestDistance = computed(() => (selectedGoal.value ? nearestOpponentDistance(selectedGoal.value as GameEvent) : null));

function generateWrittenAnalysis(goal: any) {
  if (!goal) return '';
  const player = goal.primary_player || 'The scorer';
  const minute = goal.time_min != null ? `${goal.time_min}'` : '';
  const team = goal.team || '';

  const parts: string[] = [];
  // Intro
  parts.push(`${player} scored ${minute} for ${team}.`);

  // Motion context
  if (goal.motion_context) {
    parts.push(`${goal.motion_context}`);
  }

  // Build-up
  const passes = inferPassesInBuildUp(goal);
  const assist = inferAssist(goal);
  if (passes > 0) {
    parts.push(`The goal came after a build-up of ${passes} pass${passes === 1 ? '' : 'es'}.`);
    if (assist) {
      parts.push(`${assist} played the last pass before the finish.`);
    }
  } else {
    parts.push('There are no recorded passes in the immediate build-up (dataset may be limited).');
  }

  // Pressure and spacing
  if (goal.has_tracking) {
    const nd = nearestOpponentDistance(goal);
    if (nd !== null) {
      const ndVal = Number(nd).toFixed(2);
      if (nd <= 0.5) {
        parts.push(`This was scored under high pressure — the nearest defender was only ${ndVal} (normalized) away.`);
      } else if (nd <= 1.5) {
        parts.push(`There was moderate pressure; the nearest defender was about ${ndVal} (normalized) away.`);
      } else {
        parts.push(`The scorer had space to operate; nearest defender ~ ${ndVal} (normalized) away.`);
      }
    }

    const oppClose = opponentsWithin(goal, 0.08);
    if (oppClose > 0) parts.push(`${oppClose} opponent(s) were within close proximity to the scorer.`);
  }

  // Heuristic summary
  const through = scoredThroughDefenders(goal);
  if (through === true) parts.push('He navigated through defenders to finish (heuristic).');
  else if (through === false) parts.push('He finished with relative space (heuristic).');

  return parts.join(' ');
}

const writtenAnalysis = computed(() => (selectedGoal.value ? generateWrittenAnalysis(selectedGoal.value) : ''));

// Convert neutral analysis into soccer jargon / idiomatic phrasing
function jargonify(text: string) {
  if (!text) return text;

  // Phrase substitutions: longer phrases first
  const subs: Array<[RegExp, string]> = [
    [/build-up of (\d+) pass(?:es)?/gi, 'link-up play involving $1 pass$1s'],
    [/build-up/gi, 'link-up play'],
    [/played the last pass before the finish/gi, 'stepped up with the final ball'],
    [/played the last pass/gi, 'fed the final ball'],
    [/last pass/gi, 'final ball'],
    [/scored/gi, 'tucked away'],
    [/scorer/gi, 'finisher'],
    [/nearest defender/gi, 'nearest marker'],
    [/opponent\(s\) were within close proximity to the scorer/gi, 'opposition were closing in on the finisher'],
    [/navigated through defenders/gi, 'splintered the backline'],
    [/finished with relative space/gi, 'finished with time and space'],
    [/passed the ball/gi, 'slotted the pass'],
    [/pass(?:es)?/gi, 'pass'],
    [/team/gi, 'side'],
  ];

  let out = text;
  for (const [rx, repl] of subs) out = out.replace(rx, repl);

  // Add footbally adjectives and tighten sentences
  out = out.replace(/This was scored under high pressure[\s\S]*?\./i, match => match + ' A composed finish under duress.');
  out = out.replace(/There are no recorded passes in the immediate link-up play \(dataset may be limited\)\./i, 'The move looks more like a direct break rather than a constructed passing sequence.');

  // Small stylistic touches
  out = out.replace(/\s+\./g, '.');
  out = out.replace(/\s+,/g, ',');

  return out;
}

const writtenAnalysisJargon = computed(() => (selectedGoal.value ? jargonify(writtenAnalysis.value) : ''));

// LLM driven polished summary state
const tone = ref('Neutral');
const llmSummary = ref<string | null>(null);
const llmLoading = ref(false);
const llmError = ref<string | null>(null);

// Compute current match score up to the selected goal (inclusive)
const matchScore = computed(() => {
  if (!selectedGoal.value) return null;

  // Sort goals chronologically (by minute, then id as tiebreaker)
  const sorted = [...goals].sort((a, b) => (a.time_min || 0) - (b.time_min || 0) || (a.id - b.id));
  const idx = sorted.findIndex(g => g.id === selectedGoal.value!.id);
  if (idx === -1) return null;

  const slice = sorted.slice(0, idx + 1);
  const homeCount = slice.filter(g => g.team === 'Home').length;
  const awayCount = slice.filter(g => g.team === 'Away').length;

  const homeName = selectedGoal.value.home_team || 'Home';
  const awayName = selectedGoal.value.away_team || 'Away';

  return {
    homeCount,
    awayCount,
    homeName,
    awayName,
    label: `${homeName} ${homeCount} — ${awayCount} ${awayName}`,
  };
});

async function polishWithLLM() {
  if (!selectedGoal.value) return;
  llmLoading.value = true;
  llmError.value = null;
  llmSummary.value = null;

  try {
    // Send the selected goal as an array to the Stage-2 generator
    const result = await generateMatchReport([selectedGoal.value as GameEvent], tone.value);
    llmSummary.value = result.summary;
  } catch (e: any) {
    llmError.value = e?.message || String(e);
  } finally {
    llmLoading.value = false;
  }
}

function selectGoal(id: number) {
  selectedGoalId.value = id;
}

function distance(a: { x: number; y: number }, b: { x: number; y: number }) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx*dx + dy*dy);
}

// Analysis helpers
function nearestOpponentDistance(goal: GameEvent) {
  if (!goal.has_tracking || goal.attacker_x === undefined || goal.attacker_y === undefined || !goal.opponents) return null;
  const attacker = { x: goal.attacker_x, y: goal.attacker_y };
  const dists = goal.opponents.map(o => distance(attacker, o));
  return Math.min(...dists);
}

function teammatesNearby(goal: GameEvent, radius = 0.08) {
  if (!goal.has_tracking || goal.attacker_x === undefined || goal.attacker_y === undefined || !goal.teammates) return 0;
  const attacker = { x: goal.attacker_x, y: goal.attacker_y };
  return goal.teammates.filter(t => distance(attacker, t) <= radius).length;
}

function opponentsWithin(goal: GameEvent, radius = 0.08) {
  if (!goal.has_tracking || goal.attacker_x === undefined || goal.attacker_y === undefined || !goal.opponents) return 0;
  const attacker = { x: goal.attacker_x, y: goal.attacker_y };
  return goal.opponents.filter(o => distance(attacker, o) <= radius).length;
}

// Try to infer assist / passes in build-up using available event list (best-effort)
function inferAssist(goal: any) {
  // Prefer explicit secondary_player if set
  if (goal.secondary_player && goal.secondary_player !== 'Team Effort') return goal.secondary_player;

  // Use attached build_up_events (last 10 events) produced by the ETL
  const bu = goal.build_up_events || [];
  // Search most-recent-first for a pass-like event
  for (let i = bu.length - 1; i >= 0; i--) {
    const ev = bu[i];
    const t = (ev.type || '').toString().toLowerCase();
    const subtype = (ev.subtype || '').toString().toLowerCase();
    if (t.includes('pass') || subtype.includes('pass')) {
      // If the 'to' field matches the scorer, return the passer; otherwise return the passer as best-effort
      if (ev.to && ev.to === goal.primary_player) return ev.from || null;
      return ev.from || null;
    }
  }

  return null;
}

function inferPassesInBuildUp(goal: any) {
  const bu = goal.build_up_events || [];
  return bu.filter((ev: any) => {
    const t = (ev.type || '').toString().toLowerCase();
    const subtype = (ev.subtype || '').toString().toLowerCase();
    return t.includes('pass') || subtype.includes('pass');
  }).length;
}

function scoredThroughDefenders(goal: GameEvent) {
  // Heuristic: if attacker is closer to an opponent than 0.05 (tight), then likely scored through/under pressure
  const nearest = nearestOpponentDistance(goal);
  if (nearest === null) return null;
  return nearest <= 0.05;
}
</script>

<template>
  <div class="goals-container" style="font-family: Arial;">
    <aside class="goals-list card">
      <div class="goals-list-header">
        <h2>Goals</h2>
        <p class="subtle">Select a goal to see a tactical snapshot and analysis</p>
      </div>

      <ul class="goals-items">
        <li v-for="g in goals" :key="g.id" :class="['goals-item', { selected: g.id === selectedGoalId }]">
          <button class="goal-btn" @click="selectGoal(g.id)">
            <div class="goal-left-col">
              <strong class="player">{{ g.primary_player }}</strong>
              <span class="meta">{{ g.time_min }}' · {{ g.team }}</span>
            </div>
            <div class="goal-right-col">
              <span class="badge">{{ g.event_type }}</span>
            </div>
          </button>
        </li>
      </ul>

      <div class="home-row">
        <button class="btn-home large" @click="goHome">← Home</button>
      </div>
    </aside>

    <main class="goal-analysis" v-if="selectedGoal">
      <div class="analysis-with-pitch">
        <div class="pitch-panel large">
          <div v-if="matchScore" class="score-bar card">
            <div class="score-home">
              <span class="team-name">{{ matchScore.homeName }}</span>
              <span class="score-num">{{ matchScore.homeCount }}</span>
            </div>
            <div class="score-center">
              <span class="dash">—</span>
            </div>
            <div class="score-away">
              <span class="score-num">{{ matchScore.awayCount }}</span>
              <span class="team-name">{{ matchScore.awayName }}</span>
            </div>
          </div>
          <PitchMap v-if="selectedGoal" :gameEvent="selectedGoal as unknown as GameEvent" />
          <div class="written-analysis card" v-if="selectedGoal">
            <h3>Written Analysis</h3>
            <div v-if="llmLoading">Generating polished analysis…</div>
            <p v-else v-html="llmSummary ? llmSummary : writtenAnalysisJargon"></p>

            <div class="llm-controls">
              <label for="tone-select">Tone:</label>
              <select id="tone-select" v-model="tone">
                <option>Neutral</option>
                <option>Celebratory</option>
                <option>Critical</option>
              </select>
              <button class="btn-primary" @click="polishWithLLM" :disabled="llmLoading || !selectedGoal">{{ llmLoading ? 'Generating...' : 'Polish with LLM' }}</button>
            </div>

            <div class="llm-error" v-if="llmError">Error: {{ llmError }}</div>
          </div>
        </div>

        <div class="analysis-panel">
          <div class="analysis-header">
            <h2>Analysis</h2>
            <p class="subtle">{{ selectedGoal.primary_player }} · {{ selectedGoal.time_min }}' · {{ selectedGoal.team }}</p>
          </div>

          <div class="summary-cards">
            <div class="card small">
              <div class="card-title">Pressure</div>
              <div class="card-value">{{ selectedGoal.motion_context.split('.')[0] }}</div>
            </div>
            <div class="card small">
              <div class="card-title">Passes</div>
              <div class="card-value">{{ passesCount }}</div>
            </div>
            <div class="card small">
              <div class="card-title">Assist</div>
              <div class="card-value">{{ assistName || '—' }}</div>
            </div>
          </div>

          <section class="tracking">
            <h3>Tracking-based insights</h3>
            <ul class="insights">
              <li><strong>Nearest defender distance:</strong>
                <span v-if="nearestDistance !== null">{{ (nearestDistance as number).toFixed(2) }} (norm.)</span>
                <span v-else>Unknown</span>
              </li>
              <li><strong>Opponents within 0.08:</strong> {{ selectedGoal.has_tracking ? opponentsWithin(selectedGoal, 0.08) : '—' }}</li>
              <li><strong>Teammates nearby:</strong> {{ selectedGoal.has_tracking ? teammatesNearby(selectedGoal, 0.08) : '—' }}</li>
              <li><strong>Through defenders (heuristic):</strong>
                <span v-if="scoredThroughDefenders(selectedGoal) === true">Yes</span>
                <span v-else-if="scoredThroughDefenders(selectedGoal) === false">No</span>
                <span v-else>Unknown</span>
              </li>
            </ul>
          </section>

          <section class="build-up">
            <h3>Build-up (last events)</h3>
            <ul class="timeline">
              <li v-for="(ev, idx) in (selectedGoal.build_up_events || [])" :key="idx">
                <span class="ev-time">{{ ev.time_min }}'</span>
                <span class="ev-type">{{ ev.type || ev.subtype }}</span>
                <span class="ev-desc">{{ ev.from }} → {{ ev.to || '—' }}</span>
              </li>
            </ul>
          </section>
        </div>
      </div>
    </main>

    <main v-else class="goal-analysis empty">
      <p>No goals found in dataset.</p>
    </main>
  </div>
</template>

<style scoped>
.goals-container {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem 0.5rem; /* reduce horizontal padding so content can extend further */
  width: 100%;
  box-sizing: border-box;
}

.goals-list {
  width: 280px;
  background: linear-gradient(180deg,#ffffff,#fcfdff);
  border: 1px solid #eef1f6;
  border-radius: 12px;
  padding: 1rem;
}
.goals-list-header { margin-bottom: 0.5rem }
.goals-list h2 { margin: 0 }
.goals-list .subtle { margin: 4px 0 0; color: #6c757d; font-size: 0.85rem }
.goals-items { list-style: none; padding: 0; margin: 0; max-height: 56vh; overflow: auto }
.goals-item { margin-bottom: 0.5rem; }
.goal-btn { width: 100%; display:flex; align-items:center; justify-content:space-between; padding:0.6rem; border-radius:8px; border:1px solid transparent; background:transparent; cursor:pointer }
.goal-btn:hover { background: #f8fafc }
.goals-item.selected .goal-btn { background:#f0eefc; border-color: #e5dbff }
.goal-left-col { display:flex; flex-direction:column; align-items:flex-start }
.player { font-size:0.95rem }
.meta { color:#6c757d; font-size:0.85rem }
.goal-right-col .badge { background:#eef2ff; color:#4f46e5; padding:0.15rem 0.5rem; border-radius:999px; font-size:0.75rem }

.analysis-with-pitch {
  display: grid;
  /* reduce pitch width and give the analysis column more room */
  grid-template-columns: 360px 1fr;
  gap: 1.75rem;
  align-items: start;
}
.pitch-panel.large { width:100% }
.analysis-panel { width: 100%; }
.analysis-panel { background:#fff; border:1px solid #eef1f6; border-radius:12px; padding:1.5rem; box-shadow: 0 6px 20px rgba(16,24,40,0.04); min-width:0 }

.analysis-header { margin-bottom: 0.75rem }
.subtle { color:#6c757d; font-size:0.9rem }

.home-row { margin-top: 1rem; display:flex; justify-content:center }
.btn-home.large { width: 100%; padding:0.9rem 1rem; font-size:1rem; border-radius:10px; background:#fff; border:1px solid #e6e9ef; box-shadow:0 6px 18px rgba(16,24,40,0.06); font-weight:700 }
.btn-home.large:hover { background:#fbfbfe }

.summary-cards { display:flex; gap:1rem; margin-bottom:1rem; align-items:stretch }
.card.small { background:#f8fafc; padding:0.9rem; border-radius:10px; flex:1; border:1px solid #eef1f6; min-width:0 }
.card-title { font-size:0.75rem; color:#6c757d }
.card-value { font-size:1rem; font-weight:700 }
.insights { list-style:none; padding:0; margin:0.6rem 0; line-height:1.5 }
.timeline { list-style:none; padding:0; margin:0.6rem 0; max-height:260px; overflow:auto }
.timeline li { display:flex; gap:0.8rem; padding:0.6rem 0; border-bottom:1px dashed #f1f3f5 }
.ev-time { width:48px; color:#6c757d; flex:0 0 48px }
.ev-type { width:110px; font-weight:600; flex:0 0 110px }
.ev-desc { color:#495057; word-break:break-word }

.written-analysis { margin-top:0.9rem; background:#fff; border:1px solid #eef1f6; padding:1rem; border-radius:10px }
.written-analysis h3 { margin:0 0 0.5rem 0 }
.written-analysis p { margin:0; color:#333; line-height:1.6 }

.score-bar { display:flex; justify-content:space-between; align-items:center; padding:0.5rem 1rem; margin-bottom:0.75rem; background: linear-gradient(90deg,#ffffff,#fbfbff); border:1px solid #eef1f6; border-radius:8px }
.score-home { display:flex; align-items:center; gap:0.8rem; font-weight:800; font-size:1.35rem }
.score-center { display:flex; align-items:center; }
.score-away { display:flex; align-items:center; gap:0.8rem; font-weight:800; font-size:1.35rem; justify-content: flex-end; text-align: right; }
.team-name { color:#374151; font-size:1.10rem }
.score-num { color:#111827; font-size:2rem }
.dash { color:#6b7280; margin: 0 0.4rem; }

.llm-controls { display:flex; gap:0.5rem; align-items:center; margin-top:0.75rem }
.llm-controls select { padding:0.35rem; border-radius:6px }
.btn-primary { background:#4f46e5; color:white; border:none; padding:0.55rem 0.9rem; border-radius:8px; cursor:pointer }
.btn-primary:disabled { opacity:0.6; cursor:not-allowed }
.llm-output { margin-top:0.75rem; padding:0.8rem; border-radius:8px; border:1px solid #eef1f6 }
.llm-output h3 { margin:0 0 0.5rem 0 }
.llm-error { color: #b91c1c; margin-top:0.5rem }

/* Responsive */
@media (max-width: 900px) {
  .goals-container { flex-direction: column }
  .analysis-with-pitch { grid-template-columns: 1fr; }
  .goals-list { width: 100% }
}

</style>
