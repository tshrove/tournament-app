<template>
  <div class="home-view">
    <header class="page-header">
      <h1>{{ tournamentName }}</h1>
      <p class="subtitle">Welcome to the tournament dashboard</p>
    </header>
    
    <div class="content-container">
      <section class="schedule-section">
        <div class="section-header">
          <h2>Upcoming & Recent Games</h2>
          <div class="badge" v-if="schedule.length > 0">{{ schedule.length }} Games</div>
        </div>
        
        <div v-if="scheduleLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading schedule...</p>
        </div>
        
        <div v-else-if="scheduleError" class="error-state">
          <p>{{ scheduleError }}</p>
        </div>
        
        <div v-else-if="schedule.length === 0" class="empty-state">
          <p>No games scheduled yet.</p>
        </div>
        
        <div v-else class="schedule-container">
          <ScheduleTable 
            :games="schedule" 
            :allowDelete="false"
            :showScores="true"
          />
        </div>
      </section>
      
      <!-- Game Results Section -->
      <section class="game-results-section">
        <div class="section-header">
          <h2>Game Results</h2>
          <div class="badge" v-if="playedGames.length > 0">{{ playedGames.length }} Games</div>
        </div>
        
        <div v-if="scheduleLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading game results...</p>
        </div>
        
        <div v-else-if="scheduleError" class="error-state">
          <p>{{ scheduleError }}</p>
        </div>
        
        <div v-else-if="playedGames.length === 0" class="empty-state">
          <p>No completed games yet.</p>
        </div>
        
        <div v-else class="results-container">
          <div class="results-grid">
            <div v-for="game in playedGames" :key="game.id" class="result-card">
              <div class="result-header">
                <div class="result-date">{{ formatDate(game.date) }}</div>
                <span class="status-pill">{{ game.status }}</span>
              </div>
              <div class="result-teams">
                <div class="team" :class="{'winner': game.team1_score > game.team2_score}">
                  <span class="team-name">{{ game.team1_name }}</span>
                  <span class="team-score">{{ game.team1_score }}</span>
                </div>
                <div class="vs-divider">VS</div>
                <div class="team" :class="{'winner': game.team2_score > game.team1_score}">
                  <span class="team-name">{{ game.team2_name }}</span>
                  <span class="team-score">{{ game.team2_score }}</span>
                </div>
              </div>
              <div class="result-meta">
                <span class="field">{{ game.field }}</span>
                <span class="game-time">{{ formatTime(game.time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <section class="rankings-section">
        <div class="section-header">
          <h2>Current Rankings</h2>
          <div class="badge" v-if="rankings.length > 0">{{ rankings.length }} Teams</div>
        </div>
        
        <div v-if="rankingsLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading rankings...</p>
        </div>
        
        <div v-else-if="rankingsError" class="error-state">
          <p>{{ rankingsError }}</p>
        </div>
        
        <div v-else-if="rankings.length === 0" class="empty-state">
          <p>No ranking data available yet.</p>
        </div>
        
        <div v-else class="rankings-container">
          <table class="rankings-table">
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
              </tr>
            </thead>
            <tbody>
              <tr v-for="team in rankings" :key="team.id">
                <td class="rank-cell">{{ team.rank }}</td>
                <td class="team-name-cell">{{ team.name }}</td>
                <td>{{ team.wins }}</td>
                <td>{{ team.losses }}</td>
                <td class="win-pct">{{ formatPercentage(team.win_percentage) }}</td>
                <td>{{ team.runs_scored }}</td>
                <td>{{ team.runs_allowed }}</td>
                <td :class="{'positive': team.run_differential > 0, 'negative': team.run_differential < 0}">
                  {{ team.run_differential > 0 ? '+' : '' }}{{ team.run_differential }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      
      <section class="admin-link-section">
        <div class="admin-card">
          <h3>Tournament Administration</h3>
          <p>Manage teams, schedule, and brackets</p>
          <router-link to="/admin" class="btn btn-primary">Admin Dashboard</router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../services/api';
import ScheduleTable from '../components/ScheduleTable.vue';

// Tournament settings
const tournamentName = ref('Tournament');

// Schedule data
const schedule = ref([]);
const scheduleLoading = ref(true);
const scheduleError = ref(null);

// Rankings data
const rankings = ref([]);
const rankingsLoading = ref(true);
const rankingsError = ref(null);

// Computed property to filter played games
const playedGames = computed(() => {
  return schedule.value.filter(game => 
    game.team1_score !== null && 
    game.team2_score !== null && 
    game.status === 'Completed'
  ).sort((a, b) => new Date(b.date) - new Date(a.date)); // Sort by date, newest first
});

// Fetch tournament settings
const fetchSettings = async () => {
  try {
    const response = await api.getSettings();
    tournamentName.value = response.data.name;
    // Update the document title
    document.title = `${tournamentName.value} - Tournament App`;
  } catch (err) {
    console.error('Error loading tournament settings:', err);
    // Fallback to default name if settings can't be loaded
    tournamentName.value = 'Baseball Tournament';
  }
};

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'TBD';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric' 
  });
};

// Format time for display
const formatTime = (timeString) => {
  if (!timeString) return 'TBD';
  return timeString.substring(0, 5); // Format HH:MM
};

// Format win percentage for display
const formatPercentage = (value) => {
  if (value === undefined || value === null) return '.000';
  return value.toFixed(3).replace(/^0+/, '');
};

// Fetch schedule data
const fetchSchedule = async () => {
  scheduleLoading.value = true;
  try {
    const response = await api.getSchedule();
    schedule.value = response.data;
  } catch (err) {
    scheduleError.value = 'Error loading schedule data';
    console.error(err);
  } finally {
    scheduleLoading.value = false;
  }
};

// Fetch rankings data
const fetchRankings = async () => {
  rankingsLoading.value = true;
  try {
    const response = await api.getRankings();
    rankings.value = response.data;
  } catch (err) {
    rankingsError.value = 'Error loading rankings data';
    console.error(err);
  } finally {
    rankingsLoading.value = false;
  }
};

onMounted(() => {
  fetchSettings();
  fetchSchedule();
  fetchRankings();
});
</script>

<style scoped>
.home-view {
  width: 100%;
}

.page-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.page-header h1 {
  font-size: 2.25rem;
  margin-bottom: var(--space-xs);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  font-weight: 700;
}

.subtitle {
  color: var(--color-text-light);
  font-size: 1.1rem;
  margin-top: 0;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-xl);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-md);
  gap: var(--space-sm);
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-accent);
}

.badge {
  background-color: var(--color-primary-light);
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
}

.schedule-section, .rankings-section, .admin-link-section, .game-results-section {
  background-color: var(--color-background-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
}

.loading-state, .error-state, .empty-state {
  padding: var(--space-lg);
  text-align: center;
  border-radius: var(--radius-md);
  background-color: var(--color-background);
  margin: var(--space-md) 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(67, 97, 238, 0.2);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: var(--color-danger);
}

.empty-state {
  color: var(--color-text-light);
  font-style: italic;
}

/* Game Results specific styles */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-md);
}

.result-card {
  background-color: var(--color-background);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  position: relative;
  overflow: hidden;
}

.result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, var(--color-primary), var(--color-secondary));
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xs);
}

.result-date {
  font-size: 0.9rem;
  color: var(--color-text-light);
  font-weight: 500;
}

.result-teams {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.team {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  background-color: rgba(243, 244, 246, 0.5);
}

.team.winner {
  background-color: rgba(16, 185, 129, 0.1);
  font-weight: 600;
}

.team.winner .team-score {
  color: var(--color-success);
  font-weight: 700;
}

.team-name {
  font-weight: 500;
}

.team-score {
  font-weight: 600;
  font-size: 1.1rem;
  background-color: var(--color-background-dark);
  border-radius: var(--radius-sm);
  padding: 0.1rem 0.5rem;
  min-width: 2rem;
  text-align: center;
}

.vs-divider {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-light);
  margin: 0 auto;
  background-color: var(--color-background-dark);
  padding: 0.1rem 0.5rem;
  border-radius: var(--radius-full);
  width: fit-content;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-xs);
  font-size: 0.85rem;
}

.field {
  color: var(--color-text-light);
}

.status-pill {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.game-time {
  color: var(--color-text-light);
  font-size: 0.85rem;
}

/* Rankings table specific styles */
.rankings-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.rankings-table th {
  background-color: var(--color-accent);
  color: white;
  font-weight: 600;
  text-align: center;
  padding: var(--space-sm) var(--space-md);
  position: relative;
}

.rankings-table th:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 25%;
  height: 50%;
  width: 1px;
  background-color: rgba(255, 255, 255, 0.2);
}

.rankings-table td {
  padding: var(--space-sm) var(--space-md);
  text-align: center;
  border-bottom: 1px solid var(--color-border);
}

.rankings-table tbody tr:hover {
  background-color: var(--color-background-dark);
}

.rankings-table .rank-cell {
  font-weight: 700;
  color: var(--color-accent);
}

.rankings-table .team-name-cell {
  text-align: left;
  font-weight: 500;
}

.rankings-table .win-pct {
  color: var(--color-text-light);
  font-size: 0.85rem;
}

.rankings-table .positive {
  color: var(--color-success);
  font-weight: 600;
}

.rankings-table .negative {
  color: var(--color-danger);
  font-weight: 600;
}

/* Admin card */
.admin-card {
  text-align: center;
  padding: var(--space-md);
  background-color: rgba(67, 97, 238, 0.05);
  border-radius: var(--radius-md);
}

.admin-card h3 {
  margin-bottom: var(--space-xs);
  color: var(--color-accent);
}

.admin-card p {
  color: var(--color-text-light);
  margin-bottom: var(--space-md);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-header {
    margin-bottom: var(--space-lg);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .section-header h2 {
    font-size: 1.25rem;
  }
  
  .rankings-table th,
  .rankings-table td {
    padding: var(--space-xs) var(--space-sm);
    font-size: 0.875rem;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style> 