<script setup>
import { defineProps, defineEmits, ref, computed } from 'vue';

const props = defineProps({
  games: {
    type: Array,
    required: true
  },
  allowDelete: {
    type: Boolean,
    default: true
  },
  showScores: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['delete-game']);

// Game type filter
const gameTypeFilter = ref('all');

// Filtered games based on game type selection
const filteredGames = computed(() => {
  if (gameTypeFilter.value === 'all') {
    return props.games;
  }
  return props.games.filter(game => game.game_type === gameTypeFilter.value);
});

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'TBD';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// Format time for display
const formatTime = (timeString) => {
  if (!timeString) return 'TBD';
  return timeString.substring(0, 5); // Format HH:MM
};

// Handle delete button click
const handleDelete = (gameId) => {
  if (confirm('Are you sure you want to remove this game?')) {
    emit('delete-game', gameId);
  }
};

// Determine winner and loser for styling
const getGameOutcome = (game) => {
  if (game.status !== 'Completed' || game.team1_score === null || game.team2_score === null) {
    return { winner: null, loser: null };
  }
  
  if (game.team1_score > game.team2_score) {
    return { winner: 'team1', loser: 'team2' };
  } else if (game.team2_score > game.team1_score) {
    return { winner: 'team2', loser: 'team1' };
  } else {
    return { winner: 'tie', loser: 'tie' };
  }
};
</script>

<template>
  <div class="schedule-controls">
    <div class="filter-controls">
      <span class="filter-label">Filter:</span>
      <div class="filter-options">
        <button 
          @click="gameTypeFilter = 'all'" 
          :class="{ active: gameTypeFilter === 'all' }"
          class="filter-btn"
        >
          All Games
        </button>
        <button 
          @click="gameTypeFilter = 'Pool Play'" 
          :class="{ active: gameTypeFilter === 'Pool Play' }"
          class="filter-btn"
        >
          Pool Play
        </button>
        <button 
          @click="gameTypeFilter = 'Bracket'" 
          :class="{ active: gameTypeFilter === 'Bracket' }"
          class="filter-btn"
        >
          Bracket
        </button>
      </div>
    </div>
  </div>

  <div class="schedule-table-container">
    <table class="schedule-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Time</th>
          <th>Teams</th>
          <th v-if="showScores">Score</th>
          <th>Field</th>
          <th>Type</th>
          <th>Status</th>
          <th v-if="allowDelete">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="game in filteredGames" 
          :key="game.id" 
          :class="{ 
            completed: game.status === 'Completed', 
            'bracket-game': game.game_type === 'Bracket' 
          }"
        >
          <td data-label="Date">{{ formatDate(game.date) }}</td>
          <td data-label="Time">{{ formatTime(game.time) }}</td>
          <td class="teams-column">
            <div class="matchup">
              <span 
                class="team" 
                :class="{ 
                  'winner': getGameOutcome(game).winner === 'team1',
                  'loser': getGameOutcome(game).loser === 'team1'
                }"
              >
                {{ game.team1_name }}
              </span>
              
              <span v-if="!showScores && game.team1_score !== null && game.team2_score !== null" class="vs-text">vs</span>
              
              <span 
                class="team" 
                :class="{ 
                  'winner': getGameOutcome(game).winner === 'team2',
                  'loser': getGameOutcome(game).loser === 'team2'
                }"
              >
                {{ game.team2_name }}
              </span>
            </div>
          </td>
          <td v-if="showScores" class="scores-column">
            <div v-if="game.team1_score !== null && game.team2_score !== null" class="score-container">
              <span 
                class="score" 
                :class="{ 'winner-score': getGameOutcome(game).winner === 'team1' }"
              >
                {{ game.team1_score }}
              </span>
              <span class="score-divider">-</span>
              <span 
                class="score" 
                :class="{ 'winner-score': getGameOutcome(game).winner === 'team2' }"
              >
                {{ game.team2_score }}
              </span>
            </div>
            <span v-else class="no-score">Pending</span>
          </td>
          <td data-label="Field">{{ game.field }}</td>
          <td data-label="Type">
            <span class="game-type-badge" :class="game.game_type.toLowerCase().replace(' ', '-')">
              {{ game.game_type }}
            </span>
          </td>
          <td data-label="Status">
            <span class="status-badge" :class="game.status.toLowerCase()">
              {{ game.status }}
            </span>
          </td>
          <td v-if="allowDelete" class="actions" data-label="Actions">
            <button 
              @click="handleDelete(game.id)" 
              class="btn-delete" 
              title="Remove game"
              :disabled="game.game_type === 'Bracket'"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 4H3.33333H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M5.33333 4V2.66667C5.33333 2.31304 5.47381 1.97391 5.72386 1.72386C5.97391 1.47381 6.31304 1.33333 6.66667 1.33333H9.33333C9.68696 1.33333 10.0261 1.47381 10.2761 1.72386C10.5262 1.97391 10.6667 2.31304 10.6667 2.66667V4M12.6667 4V13.3333C12.6667 13.687 12.5262 14.0261 12.2761 14.2761C12.0261 14.5262 11.687 14.6667 11.3333 14.6667H4.66667C4.31304 14.6667 3.97391 14.5262 3.72386 14.2761C3.47381 14.0261 3.33333 13.687 3.33333 13.3333V4H12.6667Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>Delete</span>
            </button>
          </td>
        </tr>
        <tr v-if="filteredGames.length === 0">
          <td colspan="8" class="empty-message">
            No games found for the selected filter.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.schedule-controls {
  margin-bottom: var(--space-md);
  display: flex;
  justify-content: flex-end;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.filter-label {
  font-weight: 500;
  color: var(--color-text-light);
}

.filter-options {
  display: flex;
  gap: 5px;
}

.filter-btn {
  background: none;
  border: 1px solid var(--color-border);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
  color: var(--color-text-light);
}

.filter-btn:hover {
  background-color: var(--color-background-dark);
}

.filter-btn.active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.schedule-table-container {
  overflow-x: auto;
  margin: var(--space-md) 0;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.schedule-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background-color: var(--color-background-card);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.schedule-table th,
.schedule-table td {
  padding: var(--space-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.schedule-table th {
  background-color: var(--color-accent);
  font-weight: 600;
  color: white;
  position: relative;
}

.schedule-table th:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 25%;
  height: 50%;
  width: 1px;
  background-color: rgba(255, 255, 255, 0.2);
}

.schedule-table tr:last-child td {
  border-bottom: none;
}

.schedule-table tbody tr {
  transition: background-color var(--transition-fast);
}

.schedule-table tbody tr:hover {
  background-color: var(--color-background-dark);
}

.teams-column {
  min-width: 200px;
}

.matchup {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.team {
  font-weight: 500;
  padding: var(--space-xs) 0;
  transition: all var(--transition-fast);
}

.team.winner {
  color: var(--color-success);
  font-weight: 600;
}

.team.loser {
  color: var(--color-text-light);
}

.scores-column {
  text-align: center;
}

.score-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  margin: var(--space-xs) 0;
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-background-dark);
  border-radius: var(--radius-sm);
  width: fit-content;
  margin: 0 auto;
}

.score {
  font-weight: 700;
  color: var(--color-accent);
}

.winner-score {
  color: var(--color-success);
  font-size: 1.1rem;
}

.score-divider {
  color: var(--color-text-light);
}

.no-score {
  font-size: 0.8rem;
  color: var(--color-text-light);
  font-style: italic;
}

.vs-text {
  text-align: center;
  font-size: 0.9rem;
  color: var(--color-text-light);
  margin: 0 auto;
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

.game-type-badge {
  display: inline-block;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.game-type-badge.pool-play {
  background-color: rgba(147, 51, 234, 0.1);
  color: #8033cc;
}

.game-type-badge.bracket {
  background-color: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-badge.scheduled {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.status-badge.in.progress, .status-badge.in.progress {
  background-color: rgba(251, 191, 36, 0.1);
  color: var(--color-warning);
}

.status-badge.completed {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.status-badge.cancelled {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.actions {
  text-align: center;
  white-space: nowrap;
}

.btn-delete {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-xs) var(--space-sm);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-delete:hover:not(:disabled) {
  background-color: var(--color-danger);
  color: white;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: rgba(156, 163, 175, 0.1);
  color: var(--color-text-light);
}

.btn-delete svg {
  width: 16px;
  height: 16px;
}

tr.completed {
  background-color: rgba(243, 244, 246, 0.3);
}

tr.bracket-game {
  background-color: rgba(255, 237, 213, 0.3);
}

tr.bracket-game:hover {
  background-color: rgba(255, 237, 213, 0.5);
}

.empty-message {
  text-align: center;
  padding: var(--space-lg);
  color: var(--color-text-light);
  font-style: italic;
}

@media (max-width: 768px) {
  .schedule-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }
  
  .filter-options {
    flex-wrap: wrap;
    width: 100%;
  }
  
  .filter-btn {
    flex: 1;
    text-align: center;
    padding: var(--space-sm);
  }
  
  .schedule-table {
    display: block; /* Convert from table to block for mobile */
  }
  
  .schedule-table thead {
    display: none; /* Hide table headers on mobile */
  }
  
  .schedule-table tbody {
    display: block;
  }
  
  .schedule-table tr {
    display: block;
    margin-bottom: var(--space-md);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    padding: var(--space-sm);
  }
  
  .schedule-table td {
    display: block;
    text-align: right;
    padding: var(--space-xs) var(--space-sm);
    position: relative;
    border-bottom: 1px solid var(--color-border);
  }
  
  .schedule-table td:last-child {
    border-bottom: none;
  }
  
  /* Add labels for each cell */
  .schedule-table td::before {
    content: attr(data-label);
    float: left;
    font-weight: 600;
    color: var(--color-text-light);
  }
  
  /* Specific styling for cards */
  .teams-column {
    border-bottom: 1px solid var(--color-border);
  }
  
  .teams-column::before {
    content: "Teams:";
    float: left;
    font-weight: 600;
    color: var(--color-text-light);
  }
  
  .matchup {
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
    margin-left: auto;
    width: 65%;
    text-align: left;
  }
  
  .scores-column::before {
    content: "Score:";
    float: left;
    font-weight: 600;
    color: var(--color-text-light);
  }
  
  .schedule-table td:nth-child(3)::before {
    content: "Field:";
  }
  
  .schedule-table td:nth-child(4)::before {
    content: "Type:";
  }
  
  .schedule-table td:nth-child(5)::before {
    content: "Status:";
  }
  
  .btn-delete {
    margin-left: auto;
  }
  
  .btn-delete span {
    display: none;
  }
}

/* Additional improvements for very small screens */
@media (max-width: 480px) {
  .filter-options {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-btn {
    width: 100%;
  }
  
  .schedule-table td {
    font-size: 0.85rem;
  }
  
  .matchup {
    width: 70%;
  }
  
  .status-badge, .game-type-badge {
    font-size: 0.7rem;
  }
}
</style> 