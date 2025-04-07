<script setup>
import { ref, onMounted, inject } from 'vue';
import api from '../services/api';
import currentTournament from '../store/current-tournament';
import ScheduleTable from '../components/ScheduleTable.vue';

const schedule = ref([]);
const loading = ref(true);
const error = ref(null);
const showNotification = inject('showNotification');

// Check if tournament is selected
const isTournamentSelected = () => {
  return currentTournament.hasSelectedTournament();
};

// Fetch schedule data
const fetchSchedule = async () => {
  if (!isTournamentSelected()) {
    schedule.value = [];
    loading.value = false;
    return;
  }
  
  loading.value = true;
  try {
    const response = await api.getSchedule({ 
      tournament_id: currentTournament.state.id 
    });
    schedule.value = response.data;
  } catch (err) {
    error.value = 'Error loading schedule: ' + (err.response?.data?.error || err.message);
    showNotification(error.value, 'error');
  } finally {
    loading.value = false;
  }
};

// Handle game deletion
const handleDeleteGame = async (gameId) => {
  try {
    await api.deleteScheduledGame(gameId);
    showNotification('Game removed from schedule', 'success');
    fetchSchedule(); // Refresh the schedule
  } catch (err) {
    showNotification('Error removing game: ' + (err.response?.data?.error || err.message), 'error');
  }
};

// Add handler methods for editing different game properties
const handleEditField = async ({ gameId, field }) => {
  try {
    await api.updateScheduledGame(gameId, { field });
    showNotification('Field updated successfully', 'success');
    fetchSchedule(); // Refresh data
  } catch (err) {
    showNotification('Error updating field: ' + (err.response?.data?.error || err.message), 'error');
  }
};

const handleEditDate = async ({ gameId, date }) => {
  try {
    await api.updateScheduledGame(gameId, { date });
    showNotification('Date updated successfully', 'success');
    fetchSchedule(); // Refresh data
  } catch (err) {
    showNotification('Error updating date: ' + (err.response?.data?.error || err.message), 'error');
  }
};

const handleEditTime = async ({ gameId, time }) => {
  try {
    await api.updateScheduledGame(gameId, { time });
    showNotification('Time updated successfully', 'success');
    fetchSchedule(); // Refresh data
  } catch (err) {
    showNotification('Error updating time: ' + (err.response?.data?.error || err.message), 'error');
  }
};

const handleEditStatus = async ({ gameId, status }) => {
  try {
    await api.updateScheduledGame(gameId, { status });
    showNotification('Status updated successfully', 'success');
    fetchSchedule(); // Refresh data
  } catch (err) {
    showNotification('Error updating status: ' + (err.response?.data?.error || err.message), 'error');
  }
};

onMounted(fetchSchedule);
</script>

<template>
  <div class="schedule-view">
    <h1>Game Schedule</h1>
    
    <div v-if="!isTournamentSelected()" class="no-tournament-warning">
      <p>Please select a tournament first to view its schedule.</p>
      <router-link to="/" class="btn btn-primary">Go to Tournament Selection</router-link>
    </div>
    
    <div v-else>
      <div v-if="currentTournament.state.name" class="tournament-info">
        <p>Viewing schedule for: <strong>{{ currentTournament.state.name }}</strong></p>
      </div>
      
      <div class="schedule-actions">
        <router-link to="/manage-schedule" class="btn-primary">
          Manage Schedule
        </router-link>
      </div>
      
      <div v-if="loading" class="loading">
        Loading schedule...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="schedule.length === 0" class="empty-state">
        <p>No games scheduled for this tournament yet.</p>
        <router-link to="/manage-schedule" class="btn-secondary">
          Add Games to Schedule
        </router-link>
      </div>
      
      <ScheduleTable 
        v-else 
        :games="schedule" 
        :isAdmin="true"
        @delete-game="handleDeleteGame"
        @edit-field="handleEditField"
        @edit-date="handleEditDate"
        @edit-time="handleEditTime"
        @edit-status="handleEditStatus"
      />
    </div>
  </div>
</template>

<style scoped>
.schedule-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

h1 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.schedule-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
}

.loading {
  text-align: center;
  padding: 2rem 0;
  color: #666;
}

.error {
  color: #e74c3c;
  background-color: #fad7d7;
  padding: 1rem;
  border-radius: 0.25rem;
  margin: 1rem 0;
}

.empty-state {
  text-align: center;
  padding: 2rem 0;
  color: #7f8c8d;
}

.btn-primary, .btn-secondary {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.btn-primary {
  background-color: #2980b9;
  color: white;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-primary:hover {
  background-color: #3498db;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.tournament-info {
  width: 100%;
  background-color: #e7f5ff;
  border: 1px solid #a5d8ff;
  color: #0c63e4;
  padding: 10px 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  text-align: center;
}

.no-tournament-warning {
  background-color: #fff3cd;
  border: 1px solid #ffecb5;
  color: #856404;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  margin: 20px 0;
}

.no-tournament-warning p {
  margin-bottom: 15px;
}
</style> 