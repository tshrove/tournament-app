<script setup>
import { ref, onMounted, inject } from 'vue';
import api from '../services/api';
import ScheduleTable from '../components/ScheduleTable.vue';

const schedule = ref([]);
const loading = ref(true);
const error = ref(null);
const showNotification = inject('showNotification');

// Fetch schedule data
const fetchSchedule = async () => {
  loading.value = true;
  try {
    const response = await api.getSchedule();
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

const handleEditTeam = async ({ gameId, teamNum, teamName }) => {
  try {
    // We need to get the teams first to find the team ID
    const teamsResponse = await api.getTeams();
    const teams = teamsResponse.data;
    
    // Find the team ID from the name
    const team = teams.find(t => t.name === teamName);
    if (!team) {
      showNotification(`Team "${teamName}" not found`, 'error');
      return;
    }
    
    const updateData = {};
    if (teamNum === 1) {
      updateData.team1_id = team.id;
    } else {
      updateData.team2_id = team.id;
    }
    
    await api.updateScheduledGame(gameId, updateData);
    showNotification('Team updated successfully', 'success');
    fetchSchedule(); // Refresh data
  } catch (err) {
    showNotification('Error updating team: ' + (err.response?.data?.error || err.message), 'error');
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
      <p>No games scheduled yet.</p>
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
      @edit-team="handleEditTeam"
      @edit-status="handleEditStatus"
    />
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

.btn-primary {
  background-color: #42b983;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #3aa876;
}

.btn-secondary {
  background-color: #606c76;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-secondary:hover {
  background-color: #4e5a63;
}

.loading, .error, .empty-state {
  padding: 2rem;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin: 1rem 0;
}

.error {
  color: #dc3545;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
</style> 