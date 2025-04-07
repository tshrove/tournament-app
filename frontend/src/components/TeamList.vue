<template>
  <div class="team-list-container">
    <h3>Current Teams</h3>
    <ul v-if="teams.length > 0">
      <li v-for="team in teams" :key="team.id">
        <div class="team-info">
          {{ team.name }} (Wins: {{ team.wins }}, Losses: {{ team.losses }}, RA: {{ team.runs_allowed }})
        </div>
        <button class="delete-btn" @click="confirmDelete(team)" :disabled="deleting === team.id">
          {{ deleting === team.id ? 'Deleting...' : 'Delete' }}
        </button>
      </li>
    </ul>
    <p v-else>No teams added yet.</p>
    
    <!-- Confirmation Dialog -->
    <div v-if="showConfirmDialog" class="confirm-dialog">
      <div class="confirm-dialog-content">
        <p>Are you sure you want to delete "{{ teamToDelete?.name }}" from {{ tournamentName }}?</p>
        <p class="warning-text">This will also remove all game data associated with this team.</p>
        <div class="dialog-buttons">
          <button @click="deleteTeam" class="confirm-btn">Yes, Delete</button>
          <button @click="cancelDelete" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed } from 'vue';
import api from '../services/api';
import currentTournament from '../store/current-tournament';

const props = defineProps({
  teams: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['teamDeleted']);
const showNotification = inject('showNotification');

const deleting = ref(null);
const showConfirmDialog = ref(false);
const teamToDelete = ref(null);

// Get tournament name for the confirmation dialog
const tournamentName = computed(() => {
  return currentTournament.state.name || 'the current tournament';
});

const confirmDelete = (team) => {
  teamToDelete.value = team;
  showConfirmDialog.value = true;
};

const cancelDelete = () => {
  showConfirmDialog.value = false;
  teamToDelete.value = null;
};

const deleteTeam = async () => {
  if (!teamToDelete.value) return;
  
  deleting.value = teamToDelete.value.id;
  showConfirmDialog.value = false;
  
  try {
    await api.deleteTeam(teamToDelete.value.id);
    if (showNotification) {
      showNotification(`Team "${teamToDelete.value.name}" has been deleted from ${tournamentName.value}.`, 'success');
    }
    emit('teamDeleted');
  } catch (err) {
    console.error("Error deleting team:", err);
    if (showNotification) {
      showNotification('Failed to delete team. Please try again.', 'error');
    }
  } finally {
    deleting.value = null;
    teamToDelete.value = null;
  }
};
</script>

<style scoped>
.team-list-container {
  background-color: #f0f0f0;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  max-width: 400px;
  position: relative;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  background-color: #fff;
  margin-bottom: 5px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-info {
  flex: 1;
}

.delete-btn {
  background-color: #ff4d4d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.8em;
  cursor: pointer;
  margin-left: 10px;
}

.delete-btn:hover:not(:disabled) {
  background-color: #e60000;
}

.delete-btn:disabled {
  background-color: #ffb3b3;
  cursor: not-allowed;
}

h3 {
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

/* Confirmation Dialog Styles */
.confirm-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.confirm-dialog-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.warning-text {
  font-size: 0.9em;
  color: #c53030;
  margin-top: 10px;
}

.dialog-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
}

.confirm-btn {
  background-color: #ff4d4d;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}

.confirm-btn:hover {
  background-color: #e60000;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}

.cancel-btn:hover {
  background-color: #e6e6e6;
}
</style> 