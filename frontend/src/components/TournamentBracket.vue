<template>
  <div class="tournament-bracket-container">
    <div v-if="!rounds || rounds.length === 0" class="no-data">
      No bracket data available
    </div>
    <div v-else class="bracket">
      <div class="round" v-for="(round, roundIndex) in rounds" :key="roundIndex">
        <div class="round-title">Round {{ roundIndex + 1 }}</div>
        <div class="match-container" v-for="(match, matchIndex) in round.matchs" :key="matchIndex">
          <!-- Apply styling similar to vue-tournament examples -->
          <div class="match vue-tournament-match" @click="handleMatchClick(match.id)">
             <div class="match-id">{{ match.id }}</div>
            <div 
              class="team team1" 
              :class="{ winner: match.winner === match.team1.id }"
            >
              <div class="team-name">{{ match.team1.name || 'TBD' }}</div>
              <div class="team-score">{{ match.team1.score !== null && match.team1.score !== undefined ? match.team1.score : '-' }}</div>
            </div>
            <div 
              class="team team2" 
              :class="{ winner: match.winner === match.team2.id }"
            >
              <div class="team-name">{{ match.team2.name || 'TBD' }}</div>
              <div class="team-score">{{ match.team2.score !== null && match.team2.score !== undefined ? match.team2.score : '-' }}</div>
            </div>
            <!-- Add FeedIn display if needed -->
             <div v-if="match.feedIn" class="feed-in">
               Feed In: {{ match.feedIn.name }}
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TournamentBracket',
  props: {
    rounds: {
      type: Array,
      required: true,
      // Basic validation for vue-tournament format
      validator: (value) => {
        return Array.isArray(value) && value.every(round => round && Array.isArray(round.matchs));
      }
    }
  },
  emits: ['onMatchClick'], // Match the event name used by vue-tournament
  methods: {
    handleMatchClick(matchId) {
      this.$emit('onMatchClick', matchId);
    }
  }
}
</script>

<style scoped>
/* Basic styling inspired by vue-tournament / react-tournament-bracket */
.tournament-bracket-container {
  width: 100%;
  overflow-x: auto;
}

.bracket {
  display: flex;
  min-width: fit-content; /* Allow bracket to grow */
  padding: 20px 0;
}

.round {
  display: flex;
  flex-direction: column;
  min-width: 220px; /* Adjust width as needed */
  margin-right: 40px; /* Space between rounds */
  justify-content: space-around; /* Distribute matches vertically */
}

.round:last-child {
  margin-right: 0;
}

.round-title {
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
  font-size: 1.1em;
}

.match-container {
  position: relative;
  margin-bottom: 20px; /* Space between matches vertically */
}

.vue-tournament-match {
  border: 1px solid #ccc;
  background-color: #fff;
  border-radius: 5px;
  padding: 5px; /* Reduced padding */
  cursor: pointer;
  transition: box-shadow 0.2s ease;
  font-size: 0.9em;
}

.vue-tournament-match:hover {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.match-id {
  font-size: 0.75rem;
  color: #999;
  text-align: center;
  margin-bottom: 3px;
}

.team {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px; /* Adjusted padding */
  border-radius: 3px;
}

.team.winner {
  font-weight: bold;
  color: #1a1a1a; /* Darker text for winner */
  background-color: #e0f2f7; /* Light blueish background for winner */
}

.team:not(.winner) {
 color: #444;
}

.team.team1 {
  border-bottom: 1px solid #eee;
}

.team-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
  margin-right: 8px;
}

.team-score {
  font-weight: bold;
  min-width: 25px;
  text-align: right;
  background-color: #f0f0f0;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 0.85em;
}

.team.winner .team-score {
    background-color: #b3e5fc;
}

.feed-in {
    font-size: 0.8em;
    color: #666;
    text-align: center;
    margin-top: 5px;
    font-style: italic;
}

.no-data {
  text-align: center;
  padding: 40px;
  font-style: italic;
  color: #777;
}
</style> 