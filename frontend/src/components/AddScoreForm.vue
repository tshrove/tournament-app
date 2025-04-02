<template>
  <div class="form-container add-score-form">
    <h3>Add Game Score</h3>
    <form @submit.prevent="submitScore">
      <div class="form-group">
        <label for="team1">Team 1:</label>
        <select id="team1" v-model="selectedTeam1" required>
          <option disabled value="">Please select Team 1</option>
          <option v-for="team in availableTeams1" :key="team.id" :value="team.id">
            {{ team.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="team1_score">Team 1 Score:</label>
        <input type="number" id="team1_score" v-model.number="team1Score" min="0" required />
      </div>

      <div class="form-group">
        <label for="team2">Team 2:</label>
        <select id="team2" v-model="selectedTeam2" required>
          <option disabled value="">Please select Team 2</option>
          <option v-for="team in availableTeams2" :key="team.id" :value="team.id">
            {{ team.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="team2_score">Team 2 Score:</label>
        <input type="number" id="team2_score" v-model.number="team2Score" min="0" required />
      </div>

      <button type="submit" :disabled="submitting">{{ submitting ? 'Adding...' : 'Add Score' }}</button>
      <p v-if="message" :class="{ 'success-message': isSuccess, 'error-message': !isSuccess }">{{ message }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits, inject } from 'vue';
import api from '../services/api';

// Inject the notification function
const showNotification = inject('showNotification');

const props = defineProps({
  teams: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['scoreAdded']);

const selectedTeam1 = ref('');
const selectedTeam2 = ref('');
const team1Score = ref(0);
const team2Score = ref(0);
const submitting = ref(false);
const message = ref('');
const isSuccess = ref(false);

// Ensure a team cannot be selected for both Team 1 and Team 2
const availableTeams1 = computed(() => {
  return props.teams.filter(team => team.id !== selectedTeam2.value);
});

const availableTeams2 = computed(() => {
  return props.teams.filter(team => team.id !== selectedTeam1.value);
});

const submitScore = async () => {
  if (!selectedTeam1.value || !selectedTeam2.value) {
    message.value = 'Please select both teams.';
    isSuccess.value = false;
    return;
  }
   if (selectedTeam1.value === selectedTeam2.value) {
    message.value = 'Teams cannot play against themselves.';
    isSuccess.value = false;
    return;
  }
   if (team1Score.value < 0 || team2Score.value < 0) {
     message.value = 'Scores cannot be negative.';
     isSuccess.value = false;
     return;
   }

  submitting.value = true;
  message.value = '';
  const gameData = {
    team1_id: selectedTeam1.value,
    team2_id: selectedTeam2.value,
    team1_score: team1Score.value,
    team2_score: team2Score.value,
  };

  try {
    const response = await api.addGame(gameData);
    // Use global notification for success
    if (showNotification) {
      showNotification(response.data.message || 'Score added successfully!', 'success');
    }
    message.value = ''; // Clear local message
    isSuccess.value = true;
    // Reset form
    selectedTeam1.value = '';
    selectedTeam2.value = '';
    team1Score.value = 0;
    team2Score.value = 0;
    emit('scoreAdded');
  } catch (err) {
    console.error("Error adding score:", err);
    if (err.response && err.response.data && err.response.data.error) {
        message.value = err.response.data.error; // Show error locally
        if (showNotification) {
            showNotification(err.response.data.error, 'error');
        }
    } else {
        message.value = 'An unexpected error occurred while adding the score.';
        if (showNotification) {
             showNotification(message.value, 'error');
        }
    }
    isSuccess.value = false;
  } finally {
    submitting.value = false;
    // Remove local timeout
    // setTimeout(() => { message.value = ''; }, 5000);
  }
};
</script>

<style scoped>
/* Use same styles as AddTeamForm, maybe refactor later */
.form-container {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  max-width: 400px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input[type="text"],
input[type="number"],
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

.success-message {
  color: green;
  margin-top: 10px;
}

.error-message {
  color: red;
  margin-top: 10px;
}

h3 {
  text-align: center;
  margin-bottom: 15px;
  color: #333;
}
</style> 