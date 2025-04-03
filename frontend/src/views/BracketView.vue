<template>
  <div>
    <h1>Tournament Bracket</h1>
    
    <!-- Admin controls -->
    <div class="admin-controls">
      <div class="button-group">
        <button class="btn btn-primary" @click="generateBracket" :disabled="generating || clearing">
          {{ generating ? 'Generating...' : 'Generate Bracket' }}
        </button>
        <button class="btn btn-danger" @click="clearBracket" :disabled="clearing || generating">
          {{ clearing ? 'Clearing...' : 'Clear Bracket' }}
        </button>
      </div>
      <div class="hints">
        <p class="hint">Generate will create a new bracket based on team rankings and automatically create bracket games in the schedule.</p>
        <p class="hint">Teams will be seeded based on their win percentage, and byes will be assigned to top-seeded teams if needed.</p>
        <p class="hint"><strong>Byes:</strong> Teams with byes in the first round will advance to the second round to play against winners of first-round games.</p>
        <p class="hint"><strong>Note:</strong> Clearing the bracket will remove all bracket games from the schedule.</p>
      </div>
    </div>
    
    <BracketDisplay :bracketData="bracketData" @update-score="handleUpdateScore" ref="bracketDisplayRef" />
    <p v-if="loading">Loading bracket...</p>
    <p v-if="error" class="error-message">{{ error }}</p>
    
    <!-- Information about bracket games and schedule -->
    <div class="bracket-info" v-if="bracketData && bracketData.rounds && Object.keys(bracketData.rounds).length > 0">
      <h3>Bracket Games</h3>
      <p>When you update scores in the bracket, the corresponding games in the schedule are also updated.</p>
      <p>As teams advance in the bracket, new games are automatically created in the schedule.</p>
      <p>Teams with byes automatically advance to the next round where they'll face winners of first-round games.</p>
      <p><router-link to="/schedule" class="schedule-link">View the schedule</router-link> to see all bracket games.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import BracketDisplay from '../components/BracketDisplay.vue';
import api from '../services/api';

const bracketData = ref({ rounds: {} });
const loading = ref(false);
const error = ref(null);
const bracketDisplayRef = ref(null);
const generating = ref(false);
const clearing = ref(false);

const fetchBracket = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await api.getBracket();
    bracketData.value = response.data;
  } catch (err) {
    console.error("Error fetching bracket:", err);
    error.value = err.response?.data?.error || 'Failed to load bracket. Ensure enough teams exist and backend is running.';
  } finally {
    loading.value = false;
  }
};

const generateBracket = async () => {
  generating.value = true;
  error.value = null;
  try {
    await api.generateBracket();
    await fetchBracket();
  } catch (err) {
    console.error("Error generating bracket:", err);
    error.value = err.response?.data?.error || 'Failed to generate bracket. Ensure enough teams exist.';
  } finally {
    generating.value = false;
  }
};

const clearBracket = async () => {
  clearing.value = true;
  error.value = null;
  try {
    await api.clearBracket();
    await fetchBracket();
  } catch (err) {
    console.error("Error clearing bracket:", err);
    error.value = err.response?.data?.error || 'Failed to clear bracket.';
  } finally {
    clearing.value = false;
  }
};

const handleUpdateScore = async (matchId, scoreData) => {
  try {
    await api.updateBracketMatch(matchId, scoreData);
    await fetchBracket();
  } catch (err) {
    console.error(`Error updating match ${matchId}:`, err);
    const errorMsg = err.response?.data?.error || 'Failed to save score.';
    if (bracketDisplayRef.value && typeof bracketDisplayRef.value.setSubmitError === 'function') {
      bracketDisplayRef.value.setSubmitError(matchId, errorMsg);
    } else {
      error.value = `Error saving score for Match ${matchId}: ${errorMsg}`;
    }
  } finally {
    if (bracketDisplayRef.value && typeof bracketDisplayRef.value.resetSubmittingState === 'function') {
      bracketDisplayRef.value.resetSubmittingState(matchId);
    }
  }
};

onMounted(() => {
  fetchBracket();
});
</script>

<style scoped>
h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.admin-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 5px;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.hints {
  text-align: center;
  max-width: 800px;
}

.btn {
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background-color: #3e8e41;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.hint {
  font-size: 0.85rem;
  color: #666;
  margin: 0.3rem 0;
}

.error-message {
  text-align: center;
  color: red;
  margin-top: 15px;
}

.bracket-info {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #e6f7ff;
  border-left: 4px solid #1890ff;
  border-radius: 4px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.bracket-info h3 {
  margin-top: 0;
  color: #1890ff;
}

.bracket-info p {
  margin: 0.5rem 0;
  color: #444;
}

.schedule-link {
  color: #1890ff;
  text-decoration: none;
  font-weight: 500;
}

.schedule-link:hover {
  text-decoration: underline;
}
</style> 