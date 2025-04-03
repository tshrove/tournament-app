<template>
  <div class="bracket-container">
    <h2>Tournament Bracket</h2>
    <div class="bracket-rounds" v-if="bracketData && bracketData.rounds && Object.keys(bracketData.rounds).length > 0">
       <div v-for="(roundMatches, roundNumber) in bracketData.rounds" :key="roundNumber" class="round">
           <h4>Round {{ roundNumber }}</h4>
           <ul>
               <li v-for="match in roundMatches" :key="match.matchId" :class="[match.status.toLowerCase(), {'has-bye': match.status === 'Bye'}]" class="match">
                   <!-- Match details content -->
                    <div class="match-content">
                        <div class="match-info">
                            <span class="match-id">M{{ match.matchId }}:</span>
                            
                            <!-- Team 1 -->
                            <span :class="['team', 'team1', { 'winner': match.winner && match.winner.id === match.team1?.id, 'bye-team': match.status === 'Bye' && match.team1 }]">
                                <span v-if="match.team1" class="seed-number">#{{ match.team1.seed || '?' }}</span>
                                {{ match.team1 ? match.team1.name : 'TBD' }}
                                <strong v-if="match.status === 'Complete' && match.team1_score !== null"> {{ match.team1_score }}</strong>
                            </span>
                            
                            <!-- VS or BYE indicator -->
                            <span v-if="match.status === 'Bye'" class="vs bye-indicator">
                                <span class="bye-icon">➠</span> BYE
                            </span>
                            <span v-else class="vs">vs</span>
                            
                            <!-- Team 2 -->
                            <span :class="['team', 'team2', { 'winner': match.winner && match.winner.id === match.team2?.id, 'bye-team': match.status === 'Bye' && match.team2 }]">
                                <strong v-if="match.status === 'Complete' && match.team2_score !== null">{{ match.team2_score }} </strong>
                                {{ match.team2 ? match.team2.name : (match.status === 'Bye' ? '' : 'TBD') }}
                                <span v-if="match.team2" class="seed-number">#{{ match.team2.seed || '?' }}</span>
                            </span>
                        </div>
                        
                        <!-- Bye explanation -->
                        <div v-if="match.status === 'Bye'" class="bye-explanation">
                            <p>Team advances to next round automatically</p>
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
  /* Add -webkit-overflow-scrolling for smooth scrolling on iOS */
  -webkit-overflow-scrolling: touch;
  /* Add scroll snap for better mobile scroll experience */
  scroll-snap-type: x mandatory;
}

.round {
  display: flex;
  flex-direction: column;
  gap: 30px; /* Vertical space between matches in a round */
  min-width: 300px; /* Minimum width for a round */
  /* Add scroll snap for better mobile experience */
  scroll-snap-align: start;
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

/* Seed number styling */
.seed-number {
  display: inline-block;
  background-color: #f0f0f0;
  color: #444;
  border-radius: 3px;
  padding: 0.1rem 0.3rem;
  margin: 0 0.3rem;
  font-size: 0.7rem;
  font-weight: bold;
}

.team1 .seed-number {
  margin-right: 0.5rem;
}

.team2 .seed-number {
  margin-left: 0.5rem;
}

/* Bye styling */
.has-bye {
  background-color: #f8f4ff;
  border-left: 4px solid #9c5eda;
}

.bye-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9c5eda;
  font-weight: bold;
}

.bye-icon {
  margin-right: 5px;
  font-size: 1rem;
}

.bye-team {
  font-weight: bold;
  color: #9c5eda;
}

.bye-explanation {
  background-color: rgba(156, 94, 218, 0.1);
  padding: 5px 8px;
  border-radius: 4px;
  margin-top: 5px;
}

.bye-explanation p {
  margin: 0;
  color: #9c5eda;
  font-size: 0.8rem;
  font-style: italic;
  text-align: center;
}

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

p {
  text-align: center;
  color: #777;
  margin-top: 15px;
}

/* Mobile responsiveness improvements */
@media (max-width: 768px) {
  .bracket-container {
    padding: 10px;
  }
  
  .bracket-rounds {
    gap: 20px; /* Reduce space between rounds */
  }
  
  .round {
    min-width: 280px; /* Slightly smaller minimum width */
  }
  
  .match {
    padding: 8px;
  }
  
  .match-info {
    font-size: 0.85em;
  }
  
  .team1, .team2 {
    max-width: 100px; /* Limit width to prevent overflow */
  }
  
  .score-input-section {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .score-input-section button {
    width: 100%;
    margin-top: 5px;
    padding: 6px 0; /* Increase touch target */
  }
}

/* Small phone screens */
@media (max-width: 480px) {
  .bracket-rounds {
    gap: 15px;
  }
  
  .round {
    min-width: 250px;
    gap: 20px;
  }
  
  .team1, .team2 {
    max-width: 80px;
  }
  
  .seed-number {
    font-size: 0.65rem;
    padding: 0.1rem 0.2rem;
  }
}
</style> 