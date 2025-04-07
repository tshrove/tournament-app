<template>
  <div class="team-management-view">
    <h1>Team Management</h1>
    <p v-if="loading">Loading teams...</p>
    <p v-if="error" class="error-message">{{ error }}</p>

    <div v-if="!currentTournament.hasSelectedTournament()" class="no-tournament-warning">
      <p>Please select a tournament first to manage its teams.</p>
      <router-link to="/" class="btn btn-primary">Go to Tournament Selection</router-link>
    </div>

    <div v-else class="management-layout">
      <div v-if="currentTournament.state.name" class="tournament-info">
        <p>Managing teams for: <strong>{{ currentTournament.state.name }}</strong></p>
      </div>
      
      <div class="form-column">
        <AddTeamForm @team-added="refreshTeams" />
      </div>
      <div class="list-column">
        <TeamList :teams="teams" @team-deleted="refreshTeams" />
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue';
import AddTeamForm from '../components/AddTeamForm.vue';
import TeamList from '../components/TeamList.vue';
import api from '../services/api';
import currentTournament from '../store/current-tournament';

const teams = ref([]);
const loading = ref(false);
const error = ref(null);
const showNotification = inject('showNotification');

const fetchTeams = async () => {
  if (!currentTournament.hasSelectedTournament()) {
    teams.value = [];
    return;
  }
  
  loading.value = true;
  error.value = null;
  try {
    const response = await api.getTeams({ 
      tournament_id: currentTournament.state.id 
    });
    // Sort teams alphabetically for display in list/dropdowns
    teams.value = response.data.sort((a, b) => a.name.localeCompare(b.name));
  } catch (err) {
    console.error("Error fetching teams:", err);
    error.value = 'Failed to load teams. Please ensure the backend server is running.';
    if (showNotification) {
      showNotification('Failed to load teams for the selected tournament.', 'error');
    }
  } finally {
    loading.value = false;
  }
};

// Function to be called when child components notify changes
const refreshTeams = () => {
  fetchTeams();
  // Potentially add a small delay if backend updates are not instantaneous
};

// Fetch teams when the component is mounted
onMounted(() => {
  fetchTeams();
});
</script>

<style scoped>
h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
}

.team-management-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.management-layout {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
  gap: 30px; /* Space between columns */
  justify-content: center; /* Center columns */
}

.form-column,
.list-column {
  flex: 1; /* Allow columns to grow */
  min-width: 300px; /* Minimum width before wrapping */
  display: flex;
  flex-direction: column;
  gap: 20px; /* Space between forms/list in the same column */
}

.error-message {
  color: red;
  text-align: center;
  margin-bottom: 15px;
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
</style> 