<template>
  <div class="bracket-container">
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
                        
                        <!-- Match Status Indicator -->
                        <div v-if="match.status === 'Scheduled'" class="match-status scheduled">
                            <p>Game scheduled</p>
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
    <p v-else>Tournament bracket is not available yet.</p>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  bracketData: {
    type: Object, // Expecting { rounds: { '1': [...], '2': [...] } }
    required: true,
    default: () => ({ rounds: {} })
  }
});
</script>

<style scoped>
.bracket-container {
  padding: 20px;
  background-color: #f4f4f4; /* Light background for the whole area */
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

/* Match status indicator */
.match-status {
  padding: 5px 8px;
  border-radius: 4px;
  margin-top: 5px;
  text-align: center;
}

.match-status.scheduled {
  background-color: rgba(255, 193, 7, 0.1);
}

.match-status p {
  margin: 0;
  font-size: 0.8rem;
  font-style: italic;
  color: #ff9800;
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

.winner-display { 
  font-weight: bold; 
  color: #388E3C; 
  font-size: 0.85em; 
  margin-top: 5px; 
  text-align: center; 
}

p {
  text-align: center;
  color: #777;
  margin-top: 15px;
}

/* Responsive styles for better mobile display */
@media (max-width: 768px) {
  .bracket-rounds {
    flex-direction: column;
    gap: 20px;
  }
  
  .round {
    min-width: auto;
  }
  
  .match-info {
    font-size: 0.8em;
  }
}
</style> 