<template>
  <div class="rankings-table-container">
    <h2>Team Rankings</h2>
    <table v-if="rankings.length > 0">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Team Name</th>
          <th>W</th>
          <th>L</th>
          <th>Pct</th>
          <th>Runs For</th>
          <th>Runs Against</th>
          <th>Diff</th>
          <th>GP</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="team in rankings" :key="team.id">
          <td class="rank">{{ team.rank }}</td>
          <td class="team-name">{{ team.name }}</td>
          <td>{{ team.wins }}</td>
          <td>{{ team.losses }}</td>
          <td class="win-pct">{{ formatPercentage(team.win_percentage) }}</td>
          <td>{{ team.runs_scored }}</td>
          <td>{{ team.runs_allowed }}</td>
          <td :class="{'positive': team.run_differential > 0, 'negative': team.run_differential < 0}">
            {{ team.run_differential > 0 ? '+' : '' }}{{ team.run_differential }}
          </td>
          <td>{{ team.games_played }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No ranking data available yet.</p>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  rankings: {
    type: Array,
    required: true,
    default: () => []
  }
});

// Format win percentage as a display value
const formatPercentage = (value) => {
  if (value === undefined || value === null) return '.000';
  return value.toFixed(3).replace(/^0+/, '');
};
</script>

<style scoped>
.rankings-table-container {
  margin: 20px auto;
  padding: 20px;
  max-width: 900px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

thead {
  background-color: #42b983;
  color: white;
}

th,
td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: center;
}

tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

tbody tr:hover {
  background-color: #f1f1f1;
}

p {
  text-align: center;
  color: #777;
}

.team-name {
  text-align: left;
  font-weight: 500;
}

.rank {
  font-weight: bold;
}

.win-pct {
  font-weight: 500;
}

.positive {
  color: #42b983;
  font-weight: 500;
}

.negative {
  color: #ff5252;
  font-weight: 500;
}
</style> 