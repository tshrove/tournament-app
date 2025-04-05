<template>
  <div class="home-view">
    <header class="page-header">
      <div class="header-content">
        <div class="back-link">
          <button @click="goBackToTournaments" class="btn btn-sm btn-outline back-button">
            &larr; All Tournaments
          </button>
        </div>
        <h2>{{ tournamentName }}</h2>
        <p class="subtitle">Tournament Dashboard</p>
      </div>
    </header>
    
    <div class="content-container">
      <section class="card schedule-section">
        <div class="section-header">
          <h3>Upcoming & Recent Games</h3>
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
            :isAdmin="false"
          />
        </div>
      </section>
      
      <!-- Game Results Section -->
      <section class="card game-results-section">
        <div class="section-header">
          <h3>Game Results</h3>
          <div class="badge" v-if="playedGames.length > 0">{{ playedGames.length }} Played</div>
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
            <div v-for="game in playedGames" :key="game.id" class="result-card-item">
              <div class="result-header">
                <div class="result-date">{{ formatDate(game.date) }}</div>
                <span class="status-pill complete">{{ game.status }}</span>
              </div>
              <div class="result-teams">
                <div class="team" :class="{'winner': game.team1_score > game.team2_score}">
                  <span class="team-name">{{ game.team1_name }}</span>
                  <span class="team-score">{{ game.team1_score }}</span>
                </div>
                <div class="vs-divider">vs</div>
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
      
      <!-- Tournament Bracket Section -->
      <section class="card bracket-section">
        <div class="section-header">
          <h3>Tournament Bracket</h3>
        </div>
        
        <div v-if="bracketLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading tournament bracket...</p>
        </div>
        
        <div v-else-if="bracketError" class="error-state">
          <p>{{ bracketError }}</p>
        </div>
        
        <div v-else-if="!bracketData || !bracketData.rounds || Object.keys(bracketData.rounds).length === 0" class="empty-state">
          <p>Tournament bracket has not been generated yet.</p>
        </div>
        
        <div v-else class="bracket-container">
          <ReadOnlyBracketDisplay :bracketData="bracketData" />
        </div>
      </section>
      
      <section class="card rankings-section">
        <div class="section-header">
          <h3>Current Rankings</h3>
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
          <div class="table-wrapper desktop-rankings">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Team Name</th>
                  <th>W</th>
                  <th>L</th>
                  <th>Pct</th>
                  <th>RF</th>
                  <th>RA</th>
                  <th>Diff</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(team, index) in rankings" :key="team.id">
                  <td class="rank-cell">{{ index + 1 }}</td>
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
          
          <div class="mobile-rankings">
            <div v-for="(team, index) in rankings" :key="team.id" class="ranking-card-item">
              <div class="ranking-card-header">
                <span class="rank-badge">{{ index + 1 }}</span>
                <h4 class="team-name">{{ team.name }}</h4>
              </div>
              <div class="ranking-card-content">
                <div class="ranking-stat">
                  <span class="stat-label">Record</span>
                  <span class="stat-value">{{ team.wins }}-{{ team.losses }}</span>
                </div>
                <div class="ranking-stat">
                  <span class="stat-label">Win %</span>
                  <span class="stat-value win-pct">{{ formatPercentage(team.win_percentage) }}</span>
                </div>
                <div class="ranking-stat">
                  <span class="stat-label">Run Diff</span>
                  <span class="stat-value" :class="{'positive': team.run_differential > 0, 'negative': team.run_differential < 0}">
                    {{ team.run_differential > 0 ? '+' : '' }}{{ team.run_differential }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';
import ScheduleTable from '../components/ScheduleTable.vue';
import ReadOnlyBracketDisplay from '../components/ReadOnlyBracketDisplay.vue';
import currentTournament from '../store/current-tournament';

const route = useRoute();
const router = useRouter();

// Tournament ID and data
const tournamentId = computed(() => route.params.id);
const tournamentName = ref('Tournament');
const tournamentData = ref(null);
const tournamentLoading = ref(true);
const tournamentError = ref(null);

// Schedule data
const schedule = ref([]);
const scheduleLoading = ref(true);
const scheduleError = ref(null);

// Rankings data
const rankings = ref([]);
const rankingsLoading = ref(true);
const rankingsError = ref(null);

// Bracket data
const bracketData = ref(null);
const bracketLoading = ref(true);
const bracketError = ref(null);

// Computed property to filter played games
const playedGames = computed(() => {
  return schedule.value.filter(game => 
    game.team1_score !== null && 
    game.team2_score !== null && 
    game.status === 'Completed'
  ).sort((a, b) => new Date(b.date) - new Date(a.date)); // Sort by date, newest first
});

// Fetch tournament data
const fetchTournament = async () => {
  if (!tournamentId.value) return;
  
  tournamentLoading.value = true;
  tournamentError.value = null;
  
  try {
    const response = await api.getTournament(tournamentId.value);
    tournamentData.value = response.data;
    tournamentName.value = tournamentData.value.name;
    
    // Update the document title
    document.title = `${tournamentName.value} - Rocketpad`;
  } catch (err) {
    console.error('Error loading tournament:', err);
    tournamentError.value = 'Failed to load tournament data.';
    // Fallback to default name if tournament can't be loaded
    tournamentName.value = 'Tournament';
  } finally {
    tournamentLoading.value = false;
  }
};

// Fetch tournament settings
const fetchSettings = async () => {
  if (!tournamentId.value) return;
  
  try {
    const response = await api.getSettings({ tournament_id: tournamentId.value });
    // If we already have the tournament name from the tournament data, don't override it
    if (!tournamentData.value) {
      tournamentName.value = response.data.name;
      // Update the document title
      document.title = `${tournamentName.value} - Rocketpad`;
    }
  } catch (err) {
    console.error('Error loading tournament settings:', err);
    // If we don't already have a name from the tournament data, use the fallback
    if (!tournamentData.value) {
      tournamentName.value = 'Baseball Tournament';
    }
  }
};

// Fetch schedule data
const fetchSchedule = async () => {
  scheduleLoading.value = true;
  scheduleError.value = null;
  
  try {
    const response = await api.getSchedule({ tournament_id: tournamentId.value });
    schedule.value = response.data;
  } catch (err) {
    console.error('Error loading schedule:', err);
    scheduleError.value = 'Failed to load schedule data.';
  } finally {
    scheduleLoading.value = false;
  }
};

// Fetch rankings data
const fetchRankings = async () => {
  rankingsLoading.value = true;
  rankingsError.value = null;
  
  try {
    const response = await api.getRankings({ tournament_id: tournamentId.value });
    rankings.value = response.data;
  } catch (err) {
    console.error('Error loading rankings:', err);
    rankingsError.value = 'Failed to load rankings data.';
  } finally {
    rankingsLoading.value = false;
  }
};

// Fetch bracket data
const fetchBracket = async () => {
  bracketLoading.value = true;
  bracketError.value = null;
  
  try {
    const response = await api.getBracket({ tournament_id: tournamentId.value });
    bracketData.value = response.data;
  } catch (err) {
    console.error('Error loading bracket:', err);
    bracketError.value = 'Failed to load bracket data.';
  } finally {
    bracketLoading.value = false;
  }
};

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'TBD';
  // Create date with timezone handling to avoid date shift
  // Parse the ISO date and add a "T00:00:00Z" to ensure it's treated as UTC
  const isoDate = dateString.includes('T') ? dateString : `${dateString}T00:00:00Z`;
  const date = new Date(isoDate);
  return date.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric',
    timeZone: 'UTC' // Force UTC timezone interpretation
  });
};

// Format time for display
const formatTime = (timeString) => {
  if (!timeString) return 'TBD';
  
  let hours, minutes;
  if (timeString.includes('T')) {
    // Full ISO datetime string
    const date = new Date(timeString);
    hours = date.getHours();
    minutes = date.getMinutes();
  } else if (timeString.includes(':')) {
    // Simple time string like "14:30:00"
    [hours, minutes] = timeString.split(':').map(Number);
  } else {
    return timeString; // Unknown format, return as is
  }
  
  // Format in 12-hour time with AM/PM
  const period = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12; // Convert to 12-hour format
  minutes = minutes.toString().padStart(2, '0');
  
  return `${hours}:${minutes} ${period}`;
};

// Format win percentage as a decimal (e.g., 0.750)
const formatPercentage = (value) => {
  if (value === undefined || value === null) return '0.000';
  return value.toFixed(3);
};

// Load all data when the component mounts or tournamentId changes
const loadAllData = async () => {
  await fetchTournament();
  await fetchSettings();
  await fetchSchedule();
  await fetchRankings();
  await fetchBracket();
};

// Watch for changes in the tournament ID
watch(tournamentId, (newId) => {
  if (newId) {
      loadAllData();
  } else {
      // Handle case where ID becomes invalid/null (e.g., navigating away)
      console.log("Tournament ID cleared, potentially navigating away.");
      // Optionally clear existing data
      tournamentName.value = 'Tournament';
      schedule.value = [];
      rankings.value = [];
      bracketData.value = null;
  }
}, { immediate: true }); // immediate: true to run on initial load

// Add this function to navigate back to tournaments list
const goBackToTournaments = () => {
  // Clear the current tournament selection
  currentTournament.clearTournament();
  router.push({ name: 'Tournaments' });
};
</script>

<style scoped>
.home-view {
  width: 100%;
  overflow-x: hidden; /* Prevent horizontal overflow */
  max-width: 100%; /* Ensure content doesn't exceed viewport width */
  display: flex;
  flex-direction: column;
  align-items: center; /* Center content horizontally */
}

.page-header {
  text-align: left; /* Align header left */
  margin-bottom: var(--space-xl);
  width: 100%;
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.back-link {
  margin-bottom: var(--space-md);
}

/* Style for the back button */
.back-button {
  /* Using btn-outline styles from global CSS */
  /* Add specific adjustments if needed */
  font-size: 0.85rem;
}

.page-header h2 {
  /* Use global h2 styles */
  margin-bottom: var(--space-xs);
  /* Remove gradient text */
}

.subtitle {
  color: var(--color-text-light);
  font-size: 1rem; /* Adjusted size */
  margin-top: 0;
}

.content-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-xl);
  width: 100%;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Space out title and badge */
  margin-bottom: var(--space-lg); /* More space below header */
  gap: var(--space-sm);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border); /* Add subtle separator */
}

.section-header h3 {
  /* Use global h3 styles */
  margin: 0;
  color: var(--color-text); /* Standard text color for section titles */
}

.badge {
  background-color: var(--color-primary-light);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap; /* Prevent badge text wrapping */
}

.schedule-section, .rankings-section, .game-results-section, .bracket-section {
  /* Specific styles for sections if needed */
  overflow: hidden; /* Still needed */
}

.bracket-container {
  padding: 0;
  background-color: transparent;
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: calc(var(--space-md) * -1); /* Offset card padding */
  padding: var(--space-md); /* Add padding back inside */
}

/* Consistent loading/error/empty states */
.loading-state, .error-state, .empty-state {
  padding: var(--space-xl) var(--space-lg);
  text-align: center;
  background-color: var(--color-background-alt);
  border-radius: var(--radius-md);
  margin-top: var(--space-md);
  color: var(--color-text-light);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

/* Simplified spinner */
.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-primary-light);
  border-left-color: transparent; /* Make it a semi-circle */
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: var(--color-danger);
  background-color: rgba(244, 63, 94, 0.05); /* Subtle danger background */
  border: 1px solid rgba(244, 63, 94, 0.2);
}

.empty-state {
  font-style: normal; /* Remove italic */
}

/* Game Results refined styles */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
}

.result-card-item {
  background-color: var(--color-background-alt);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  /* Removed shadow, parent card has it */
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  border: 1px solid var(--color-border);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xs);
  padding-bottom: var(--space-sm);
  border-bottom: 1px dashed var(--color-border);
}

.result-date {
  font-size: 0.85rem;
  color: var(--color-text-light);
  font-weight: 500;
}

.status-pill {
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  border: 1px solid transparent;
}

.status-pill.complete {
  background-color: rgba(52, 211, 153, 0.1);
  color: #047857; /* Darker success */
  border-color: rgba(52, 211, 153, 0.3);
}

.result-teams {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  margin: var(--space-sm) 0;
}

.team {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xs) 0;
}

.team.winner .team-name {
  font-weight: 700;
  color: var(--color-text);
}

.team.winner .team-score {
  color: var(--color-success);
  font-weight: 700;
}

.team-name {
  font-weight: 500;
  color: var(--color-text-light);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-grow: 1;
  padding-right: var(--space-sm);
}

.team-score {
  font-weight: 600;
  font-size: 1.1rem;
  min-width: 2.5rem; /* Ensure space */
  text-align: right;
  color: var(--color-text);
}

.vs-divider {
  text-align: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  margin: var(--space-xs) auto;
  width: fit-content;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-sm);
  font-size: 0.8rem;
  color: var(--color-text-lighter);
  padding-top: var(--space-sm);
  border-top: 1px dashed var(--color-border);
}

/* Rankings specific styles */
.rankings-container {
  /* No specific styles needed now, handled by table wrapper / mobile cards */
}

/* Wrapper for desktop table to handle overflow */
.table-wrapper {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* Leverage global table styles by default */
.rankings-container table {
  /* width: 100%; // Handled globally */
  /* border-collapse: separate; // Handled globally */
  /* ... other base styles ... */
}

.rankings-container th {
  /* background-color: var(--color-background-alt); // Handled globally */
  /* color: var(--color-text-light); // Handled globally */
  /* ... other header styles ... */
  text-align: center; /* Center align table headers */
  white-space: nowrap;
}

.rankings-container td {
  /* padding: var(--space-md) var(--space-lg); // Handled globally */
  text-align: center;
  vertical-align: middle;
}

.rankings-container tbody tr:hover {
  /* background-color: var(--color-background-alt); // Handled globally */
}

.rankings-container .rank-cell {
  font-weight: 700;
  color: var(--color-primary);
  width: 50px; /* Fixed width for rank */
}

.rankings-container .team-name-cell {
  text-align: left;
  font-weight: 600;
  color: var(--color-text);
  white-space: normal; /* Allow team names to wrap if needed */
}

.rankings-container .win-pct {
  color: var(--color-text-light);
  font-size: 0.9rem;
  font-family: monospace; /* Use monospace for consistent alignment */
}

.rankings-container .positive {
  color: var(--color-success);
  font-weight: 600;
}

.rankings-container .negative {
  color: var(--color-danger);
  font-weight: 600;
}

/* Mobile rankings card view */
.mobile-rankings {
  display: none;
  flex-direction: column;
  gap: var(--space-md);
}

.ranking-card-item {
  background-color: var(--color-background-alt);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.ranking-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px dashed var(--color-border);
}

.rank-badge {
  background-color: var(--color-primary);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1rem;
  flex-shrink: 0;
}

.ranking-card-header .team-name {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text);
}

.ranking-card-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); /* Responsive columns */
  gap: var(--space-md);
  padding-top: var(--space-sm);
}

.ranking-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center; /* Center align stats */
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-light);
  text-transform: uppercase;
  font-weight: 500;
}

.stat-value {
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text);
}

.stat-value.win-pct {
    font-family: monospace;
}

.stat-value.positive {
  color: var(--color-success);
}

.stat-value.negative {
  color: var(--color-danger);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-header {
    /* text-align: center; */ /* Keep left aligned */
    padding-bottom: var(--space-md);
  }

  .page-header h2 {
    font-size: 2rem; /* Adjust if needed based on global h2 */
  }

  .subtitle {
    font-size: 0.95rem;
  }

  .section-header h3 {
    font-size: 1.3rem; /* Adjust if needed based on global h3 */
  }

  /* Switch from table to cards on mobile */
  .desktop-rankings {
    display: none;
  }

  .mobile-rankings {
    display: flex;
  }

  /* Remove responsive table column hiding as we use cards now */
  /* .rankings-table th:nth-child(n+5), */
  /* .rankings-table td:nth-child(n+5) { */
  /*   display: none; */
  /* } */
}

@media (max-width: 480px) {

  .page-header h2 {
      font-size: 1.8rem;
  }

  .section-header h3 {
      font-size: 1.2rem;
  }

  .results-grid {
      grid-template-columns: 1fr; /* Single column on small screens */
      gap: var(--space-md);
  }

  .ranking-card-content {
      grid-template-columns: repeat(3, 1fr); /* Keep 3 columns */
      gap: var(--space-sm);
  }
  
  .ranking-card-header .team-name {
      font-size: 1.1rem;
  }
  
  .stat-value {
      font-size: 0.9rem;
  }
}

/* Remove unused admin button styles */
/* .header-actions { ... } */
/* .admin-btn { ... } */

</style> 