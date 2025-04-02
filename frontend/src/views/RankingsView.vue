<template>
  <div>
    <h1>Rankings Page</h1>
    <RankingsTable :rankings="rankings" />
    <p v-if="loading">Loading rankings...</p>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import RankingsTable from '../components/RankingsTable.vue';
import api from '../services/api'; // Import the api service

const rankings = ref([]);
const loading = ref(false);
const error = ref(null);

const fetchRankings = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await api.getRankings();
    rankings.value = response.data;
  } catch (err) {
    console.error("Error fetching rankings:", err);
    error.value = 'Failed to load rankings. Please ensure the backend server is running.';
    // Handle specific errors if needed (e.g., err.response.status)
  } finally {
    loading.value = false;
  }
};

// Fetch rankings when the component is mounted
onMounted(() => {
  fetchRankings();
});
</script>

<style scoped>
h1 {
  text-align: center;
  color: #2c3e50;
}
p {
  text-align: center;
  color: red;
}
</style> 