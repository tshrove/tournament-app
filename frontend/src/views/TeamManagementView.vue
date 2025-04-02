<template>
  <div class="team-management-view">
    <h1>Team Management</h1>
    <p v-if="loading">Loading teams...</p>
    <p v-if="error" class="error-message">{{ error }}</p>

    <div class="management-layout">
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
import { ref, onMounted } from 'vue';
import AddTeamForm from '../components/AddTeamForm.vue';
import TeamList from '../components/TeamList.vue';
import api from '../services/api';

const teams = ref([]);
const loading = ref(false);
const error = ref(null);

const fetchTeams = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await api.getTeams();
    // Sort teams alphabetically for display in list/dropdowns
    teams.value = response.data.sort((a, b) => a.name.localeCompare(b.name));
  } catch (err) {
    console.error("Error fetching teams:", err);
    error.value = 'Failed to load teams. Please ensure the backend server is running.';
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
</style> 