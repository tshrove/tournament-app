<template>
  <div class="bracket-container">
    <h2>Tournament Bracket</h2>
    <div class="bracket-rounds" v-if="bracketData && bracketData.rounds && Object.keys(bracketData.rounds).length > 0">
       <div v-for="(roundMatches, roundNumber) in bracketData.rounds" :key="roundNumber" class="round">
           <h4>Round {{ roundNumber }}</h4>
           <ul>
               <li v-for="match in roundMatches" :key="match.matchId" :class="match.status.toLowerCase()" class="match">
                   <!-- Match details content -->
                    <div class="match-content">
                        <div class="match-info">
                            <span class="match-id">M{{ match.matchId }}:</span>
                            <span :class="['team', 'team1', { 'winner': match.winner && match.winner.id === match.team1?.id }]">
                            {{ match.team1 ? `(#${match.team1.seed || '?'}) ${match.team1.name}` : 'TBD' }}
                            <strong v-if="match.status === 'Complete' && match.team1_score !== null"> {{ match.team1_score }}</strong>
                            </span>
                            <span v-if="match.status === 'Bye'" class="vs">BYE</span>
                            <span v-else class="vs">vs</span>
                            <span :class="['team', 'team2', { 'winner': match.winner && match.winner.id === match.team2?.id }]">
                            <strong v-if="match.status === 'Complete' && match.team2_score !== null">{{ match.team2_score }} </strong>
                            {{ match.team2 ? `(#${match.team2.seed || '?'}) ${match.team2.name}` : (match.status === 'Bye' ? '' : 'TBD') }}
                            </span>
                        </div>
                        <!-- Score Input -->
                        <div v-if="match.status === 'Scheduled' && match.team1 && match.team2" class="score-input-section">
                            <input type="number" min="0" placeholder="S1" v-model.number="scores[match.matchId].team1_score" @input="clearError(match.matchId)">
                            <input type="number" min="0" placeholder="S2" v-model.number="scores[match.matchId].team2_score" @input="clearError(match.matchId)">
                            <button @click="submitScore(match.matchId)" :disabled="isSubmitting[match.matchId]">
                                {{ isSubmitting[match.matchId] ? '...' : 'Save' }}
                            </button>
                            <p v-if="submitErrors[match.matchId]" class="submit-error">{{ submitErrors[match.matchId] }}</p>
                        </div>
                        <!-- Winner Display -->
                        <div v-if="match.status === 'Complete' && match.winner" class="winner-display">
                            Winner: {{ match.winner.name }}
                        </div>
                   </div>
                   <!-- Connector placeholder -->
                   <!-- <div class="connector"></div> -->
               </li>
           </ul>
       </div>
    </div>
    <p v-else>Bracket data is not available or is empty.</p>
  </div>
</template>

<script setup>
import { ref, defineProps, watch, defineEmits } from 'vue';

const props = defineProps({
  bracketData: {
    type: Object, // Expecting { rounds: { '1': [...], '2': [...] } }
    required: true,
    default: () => ({ rounds: {} })
  }
});

const emit = defineEmits(['updateScore']);

const scores = ref({});
const isSubmitting = ref({});
const submitErrors = ref({});

watch(() => props.bracketData, (newBracketData) => {
  if (newBracketData && newBracketData.rounds) {
    Object.values(newBracketData.rounds).flat().forEach(match => {
      if (!scores.value[match.matchId]) {
        scores.value[match.matchId] = { team1_score: null, team2_score: null };
        isSubmitting.value[match.matchId] = false;
        submitErrors.value[match.matchId] = null;
      }
      if (match.status === 'Complete') {
          scores.value[match.matchId].team1_score = match.team1_score;
          scores.value[match.matchId].team2_score = match.team2_score;
      }
    });
  }
}, { immediate: true, deep: true });

const submitScore = (matchId) => {
  const scoreData = scores.value[matchId];
  if (scoreData.team1_score === null || scoreData.team1_score < 0 || scoreData.team2_score === null || scoreData.team2_score < 0) {
    submitErrors.value[matchId] = 'Valid scores required.';
    return;
  }
  isSubmitting.value[matchId] = true;
  submitErrors.value[matchId] = null;
  emit('updateScore', matchId, scoreData);
};

const clearError = (matchId) => {
    if (submitErrors.value[matchId]) {
        submitErrors.value[matchId] = null;
    }
}

const resetSubmittingState = (matchId) => {
  if (isSubmitting.value[matchId]) {
      isSubmitting.value[matchId] = false;
  }
};

const setSubmitError = (matchId, errorMsg) => {
    submitErrors.value[matchId] = errorMsg;
}

defineExpose({ resetSubmittingState, setSubmitError });

</script>

<style scoped>
.bracket-container {
  padding: 20px;
  background-color: #f4f4f4; /* Light background for the whole area */
}

h2 {
    text-align: center;
    margin-bottom: 20px;
}

.bracket-rounds {
  display: flex;
  flex-direction: row; /* Rounds side-by-side */
  overflow-x: auto; /* Allow horizontal scrolling if needed */
  gap: 40px; /* Space between rounds */
  padding-bottom: 20px; /* Space for scrollbar */
}

.round {
  display: flex;
  flex-direction: column;
  gap: 30px; /* Vertical space between matches in a round */
  min-width: 300px; /* Minimum width for a round */
}

.round h4 {
    text-align: center;
    margin-bottom: 15px;
    color: #555;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 30px; /* Consistent gap */
}

.match {
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  position: relative; /* For connectors if added later */
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.match-content {
    /* Styles for the main content area of the match */
     display: flex;
     flex-direction: column;
     gap: 8px;
}

.match-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.9em;
}

.match-id { font-weight: bold; margin-right: 5px; color: #888; font-size: 0.8em; }
.team { flex-basis: 40%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.team.winner { font-weight: bold; color: #1a6a30; }
.team1 { text-align: right; }
.team2 { text-align: left; }
.vs { font-weight: bold; color: #777; font-size: 0.85em; margin: 0 3px; }

/* Bye status styling */
.match.bye .match-info {
    color: #666;
}
.match.bye .team1 {
    font-weight: bold;
}
.match.bye .vs {
    color: #999;
}

/* Complete status styling */
.match.complete {
    border-left: 4px solid #4CAF50; /* Green indicator */
}

/* Scheduled status styling */
.match.scheduled {
     border-left: 4px solid #FFC107; /* Amber indicator */
}

.score-input-section {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 5px;
}

.score-input-section input[type="number"] {
  width: 45px;
  padding: 4px;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 0.9em;
}

.score-input-section button {
  padding: 4px 8px;
  font-size: 0.8em;
  background-color: #2196F3; color: white; border: none; border-radius: 3px; cursor: pointer;
}
.score-input-section button:disabled { background-color: #aaa; cursor: not-allowed; }
.score-input-section button:hover:not(:disabled) { background-color: #1976D2; }

.winner-display { font-weight: bold; color: #388E3C; font-size: 0.85em; margin-top: 5px; text-align: center; }
.submit-error { color: red; font-size: 0.8em; margin-top: 4px; text-align: left; width: 100%; }

/* Basic Connectors (Placeholder - requires more work) */
/* .match::after {
    content: '';
    position: absolute;
    right: -20px; 
    top: 50%;
    width: 20px;
    height: 2px;
    background-color: #ccc;
}
.round:last-child .match::after { display: none; } */

p {
  text-align: center;
  color: #777;
  margin-top: 15px;
}
</style> 