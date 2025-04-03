<template>
  <div class="game-scoring-view">
    <h1>Game Scoring Management</h1>
    <p class="subtitle">Update scores for completed games</p>
    
    <div class="filter-controls">
      <div class="filter-group">
        <label for="status-filter">Filter by Status:</label>
        <select id="status-filter" v-model="statusFilter" class="filter-select">
          <option value="all">All Games</option>
          <option value="Scheduled">Scheduled</option>
          <option value="In Progress">In Progress</option>
          <option value="Completed">Completed</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="date-filter">Filter by Date:</label>
        <input type="date" id="date-filter" v-model="dateFilter" class="filter-date">
      </div>
      
      <button @click="clearFilters" class="btn-secondary">Clear Filters</button>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading games...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="filteredGames.length === 0" class="empty-state">
      <p>No games match your filters.</p>
    </div>
    
    <div v-else class="games-container">
      <table class="games-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Time</th>
            <th>Teams</th>
            <th>Status</th>
            <th>Score</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="game in filteredGames" :key="game.id" :class="{ 'completed': game.status === 'Completed' }">
            <td>{{ formatDate(game.date) }}</td>
            <td>{{ formatTime(game.time) }}</td>
            <td class="teams-column">
              <span class="team">{{ game.team1_name }}</span>
              <span class="vs">vs</span>
              <span class="team">{{ game.team2_name }}</span>
            </td>
            <td>
              <span class="status-badge" :class="game.status.toLowerCase().replace(' ', '-')">
                {{ game.status }}
              </span>
            </td>
            <td class="score-column">
              <template v-if="game.team1_score !== null && game.team2_score !== null">
                <span>{{ game.team1_score }} - {{ game.team2_score }}</span>
              </template>
              <template v-else>
                <span class="no-score">Not scored</span>
              </template>
            </td>
            <td class="actions-column">
              <button 
                class="btn-edit"
                @click="openScoreModal(game)"
                :disabled="isEditingScores"
              >
                {{ game.team1_score !== null ? 'Update Score' : 'Add Score' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Score Modal -->
    <div class="modal-overlay" v-if="showScoreModal" @click="closeScoreModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ currentGame.team1_score !== null ? 'Update Score' : 'Add Score' }}</h2>
          <button class="modal-close" @click="closeScoreModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="game-info">
            <p class="game-date">{{ formatDate(currentGame.date) }} at {{ formatTime(currentGame.time) }}</p>
            <div class="game-teams">
              <span class="team-name">{{ currentGame.team1_name }}</span>
              <span class="vs">vs</span>
              <span class="team-name">{{ currentGame.team2_name }}</span>
            </div>
          </div>
          
          <form @submit.prevent="saveScore" class="score-form">
            <div class="score-inputs">
              <div class="score-input-group">
                <label :for="'team1-score'">{{ currentGame.team1_name }} Score:</label>
                <input 
                  type="number" 
                  :id="'team1-score'" 
                  v-model.number="scoreForm.team1Score" 
                  min="0" 
                  required
                >
              </div>
              
              <div class="score-input-group">
                <label :for="'team2-score'">{{ currentGame.team2_name }} Score:</label>
                <input 
                  type="number" 
                  :id="'team2-score'" 
                  v-model.number="scoreForm.team2Score" 
                  min="0" 
                  required
                >
              </div>
            </div>
            
            <div class="status-input">
              <label for="game-status">Game Status:</label>
              <select id="game-status" v-model="scoreForm.status" required>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="closeScoreModal">Cancel</button>
              <button type="submit" class="btn-primary" :disabled="isSaving">
                <span v-if="isSaving">Saving...</span>
                <span v-else>Save Score</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue';
import api from '../services/api';

// Notification function
const showNotification = inject('showNotification');

// Game data state
const games = ref([]);
const loading = ref(true);
const error = ref(null);

// Filters
const statusFilter = ref('all');
const dateFilter = ref('');

// Modal state
const showScoreModal = ref(false);
const currentGame = ref({});
const scoreForm = ref({
  team1Score: 0,
  team2Score: 0,
  status: 'Completed'
});
const isSaving = ref(false);
const isEditingScores = ref(false);

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'TBD';
  // Create date with timezone handling to avoid date shift
  // Parse the ISO date and add a "T00:00:00Z" to ensure it's treated as UTC
  const isoDate = dateString.includes('T') ? dateString : `${dateString}T00:00:00Z`;
  const date = new Date(isoDate);
  return date.toLocaleDateString(undefined, { timeZone: 'UTC' });
};

// Format time for display
const formatTime = (timeString) => {
  if (!timeString) return 'TBD';
  return timeString.substring(0, 5); // Format HH:MM
};

// Filter games based on selected filters
const filteredGames = computed(() => {
  return games.value.filter(game => {
    // Status filter
    if (statusFilter.value !== 'all' && game.status !== statusFilter.value) {
      return false;
    }
    
    // Date filter
    if (dateFilter.value && formatDate(game.date) !== formatDate(dateFilter.value)) {
      return false;
    }
    
    return true;
  });
});

// Clear all filters
const clearFilters = () => {
  statusFilter.value = 'all';
  dateFilter.value = '';
};

// Open modal to add/edit scores
const openScoreModal = (game) => {
  currentGame.value = { ...game };
  scoreForm.value = {
    team1Score: game.team1_score !== null ? game.team1_score : 0,
    team2Score: game.team2_score !== null ? game.team2_score : 0,
    status: game.status === 'Scheduled' ? 'Completed' : game.status
  };
  showScoreModal.value = true;
};

// Close the score modal
const closeScoreModal = () => {
  if (!isSaving.value) {
    showScoreModal.value = false;
  }
};

// Save the score
const saveScore = async () => {
  isSaving.value = true;
  isEditingScores.value = true;
  
  try {
    // Prepare the data
    const updatedGame = {
      id: currentGame.value.id,
      team1_score: scoreForm.value.team1Score,
      team2_score: scoreForm.value.team2Score,
      status: scoreForm.value.status
    };
    
    // Call API to update the game
    await api.updateGameScore(updatedGame);
    
    // Success notification
    showNotification(`Score updated for ${currentGame.value.team1_name} vs ${currentGame.value.team2_name}`, 'success');
    
    // Refresh the games data
    fetchGames();
    
    // Close the modal
    showScoreModal.value = false;
  } catch (err) {
    // Error notification
    showNotification(`Error updating score: ${err.message}`, 'error');
    console.error('Error updating score:', err);
  } finally {
    isSaving.value = false;
    setTimeout(() => {
      isEditingScores.value = false;
    }, 500);
  }
};

// Fetch games data
const fetchGames = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.getSchedule();
    games.value = response.data;
  } catch (err) {
    error.value = 'Error loading games. Please try again.';
    console.error('Error fetching games:', err);
  } finally {
    loading.value = false;
  }
};

// Initialize component
onMounted(() => {
  fetchGames();
});
</script>

<style scoped>
.game-scoring-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-md);
}

h1 {
  font-size: 2rem;
  color: var(--color-accent);
  margin-bottom: var(--space-xs);
}

.subtitle {
  color: var(--color-text-light);
  margin-top: 0;
  margin-bottom: var(--space-lg);
}

.filter-controls {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.filter-select, .filter-date {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-background-card);
  color: var(--color-text);
  min-width: 180px;
}

.btn-secondary {
  background-color: var(--color-background-dark);
  color: var(--color-text);
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-fast);
  height: fit-content;
}

.btn-secondary:hover {
  background-color: var(--color-border);
}

.loading-state, .error-state, .empty-state {
  padding: var(--space-lg);
  text-align: center;
  border-radius: var(--radius-md);
  background-color: var(--color-background-card);
  margin: var(--space-md) 0;
  box-shadow: var(--shadow-sm);
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

/* Table styling */
.games-container {
  overflow-x: auto;
  background-color: var(--color-background-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.games-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.games-table th {
  background-color: var(--color-accent);
  color: white;
  text-align: left;
  padding: var(--space-md);
  font-weight: 600;
  position: relative;
}

.games-table th:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 25%;
  height: 50%;
  width: 1px;
  background-color: rgba(255, 255, 255, 0.2);
}

.games-table td {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}

.games-table tr:last-child td {
  border-bottom: none;
}

.games-table tr.completed {
  background-color: rgba(243, 244, 246, 0.3);
}

.teams-column {
  display: flex;
  flex-direction: column;
}

.team {
  font-weight: 500;
}

.vs {
  font-size: 0.8rem;
  color: var(--color-text-light);
  margin: 0.2rem 0;
}

.score-column {
  font-weight: 600;
}

.no-score {
  font-style: italic;
  color: var(--color-text-light);
  font-weight: normal;
}

.status-badge {
  display: inline-block;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.scheduled {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.status-badge.in-progress {
  background-color: rgba(251, 191, 36, 0.1);
  color: var(--color-warning);
}

.status-badge.completed {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.actions-column {
  text-align: center;
}

.btn-edit {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-xs) var(--space-md);
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color var(--transition-fast);
}

.btn-edit:hover {
  background-color: var(--color-primary-dark);
}

.btn-edit:disabled {
  background-color: var(--color-text-lighter);
  cursor: not-allowed;
}

/* Modal styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-md);
}

.modal-content {
  background-color: var(--color-background-card);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-accent);
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: var(--space-lg);
}

.game-info {
  margin-bottom: var(--space-lg);
  text-align: center;
}

.game-date {
  color: var(--color-text-light);
  margin-bottom: var(--space-xs);
}

.game-teams {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  font-weight: 600;
}

.team-name {
  color: var(--color-accent);
}

.score-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.score-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

.score-input-group, .status-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.score-input-group input, .status-input select {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-md);
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-primary:disabled {
  background-color: var(--color-text-lighter);
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .games-table th, 
  .games-table td {
    padding: var(--space-sm);
    font-size: 0.9rem;
  }
  
  .score-inputs {
    grid-template-columns: 1fr;
  }
}
</style> 