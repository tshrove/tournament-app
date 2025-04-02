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
      <p class="hint">Generate will create a new bracket based on team rankings. Clear will remove all matches.</p>
    </div>
    
    <BracketDisplay :bracketData="bracketData" @update-score="handleUpdateScore" ref="bracketDisplayRef" />
    <p v-if="loading">Loading bracket...</p>
    <p v-if="error" class="error-message">{{ error }}</p>
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
  font-size: 0.8rem;
  color: #666;
  margin: 0;
}

.error-message {
  text-align: center;
  color: red;
  margin-top: 15px;
}
</style> 