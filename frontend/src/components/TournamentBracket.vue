<template>
  <div class="tournament-bracket-container">
    <div v-if="!rounds || rounds.length === 0" class="no-data">
      No bracket data available
    </div>
    <div v-else class="bracket">
      <div class="round" v-for="(round, roundIndex) in rounds" :key="roundIndex">
        <div class="round-title">Round {{ roundIndex + 1 }}</div>
        <div class="match-container" v-for="(match, matchIndex) in round.matchs" :key="matchIndex">
          <div class="match" @click="handleMatchClick(match.id)">
            <div class="match-id">Match {{ match.id }}</div>
            <div 
              class="team team1" 
              :class="{ winner: match.winner === match.team1.id }"
            >
              <div class="team-name">{{ match.team1.name }}</div>
              <div class="team-score">{{ match.team1.score !== null ? match.team1.score : '-' }}</div>
            </div>
            <div 
              class="team team2" 
              :class="{ winner: match.winner === match.team2.id }"
            >
              <div class="team-name">{{ match.team2.name }}</div>
              <div class="team-score">{{ match.team2.score !== null ? match.team2.score : '-' }}</div>
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
      required: true
    }
  },
  methods: {
    handleMatchClick(matchId) {
      this.$emit('onMatchClick', matchId);
    }
  }
}
</script>

<style scoped>
.tournament-bracket-container {
  width: 100%;
  overflow-x: auto;
}

.bracket {
  display: flex;
  min-width: 600px;
}

.round {
  display: flex;
  flex-direction: column;
  min-width: 200px;
  margin-right: 30px;
}

.round-title {
  font-weight: bold;
  text-align: center;
  margin-bottom: 15px;
  padding: 5px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.match-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 10px 0;
}

.match {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.match:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.match-id {
  font-size: 0.8rem;
  color: #777;
  margin-bottom: 5px;
  text-align: center;
}

.team {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  margin-bottom: 5px;
  border-radius: 3px;
}

.team.winner {
  background-color: #e8f5e9;
  font-weight: bold;
}

.team.team1 {
  border-bottom: 1px solid #f0f0f0;
}

.team-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.team-score {
  font-weight: bold;
  margin-left: 10px;
  min-width: 20px;
  text-align: center;
}

.no-data {
  text-align: center;
  padding: 40px;
  font-style: italic;
  color: #777;
}
</style> 