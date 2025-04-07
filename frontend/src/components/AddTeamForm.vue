<template>
  <div class="form-container add-team-form">
    <h3>Add New Team</h3>
    <form @submit.prevent="submitTeam">
      <div class="form-group">
        <label for="teamName">Team Name:</label>
        <input type="text" id="teamName" v-model="teamName" required />
      </div>
      <button type="submit" :disabled="submitting">{{ submitting ? 'Adding...' : 'Add Team' }}</button>
      <p v-if="message" :class="{ 'success-message': isSuccess, 'error-message': !isSuccess }">{{ message }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import api from '../services/api';
import currentTournament from '../store/current-tournament';

// Inject the notification function
const showNotification = inject('showNotification');

const teamName = ref('');
const submitting = ref(false);
const message = ref('');
const isSuccess = ref(false);

// Define emit for notifying parent component
const emit = defineEmits(['teamAdded']);

const submitTeam = async () => {
  if (!teamName.value.trim()) {
    message.value = 'Team name cannot be empty.';
    isSuccess.value = false;
    return;
  }
  
  if (!currentTournament.hasSelectedTournament()) {
    message.value = 'No tournament selected. Please select a tournament first.';
    isSuccess.value = false;
    if (showNotification) {
      showNotification('No tournament selected. Please select a tournament first.', 'error');
    }
    return;
  }

  submitting.value = true;
  message.value = '';
  try {
    const response = await api.addTeam({ 
      name: teamName.value,
      tournament_id: currentTournament.state.id 
    });
    // Use global notification for success
    if (showNotification) {
      showNotification(response.data.message || 'Team added successfully!', 'success');
    }
    message.value = ''; // Clear local message on success
    isSuccess.value = true;
    teamName.value = ''; // Clear the input
    emit('teamAdded');
  } catch (err) {
    console.error("Error adding team:", err);
    if (err.response && err.response.data && err.response.data.error) {
        message.value = err.response.data.error; // Show error locally
        if (showNotification) {
            showNotification(err.response.data.error, 'error'); // Optionally show error globally too
        }
    } else {
        message.value = 'An unexpected error occurred while adding the team.';
        if (showNotification) {
             showNotification(message.value, 'error');
        }
    }
    isSuccess.value = false;
  } finally {
    submitting.value = false;
    // Remove the timeout for the local message, rely on toast
    // setTimeout(() => { message.value = ''; }, 5000);
  }
};
</script>

<style scoped>
/* Add some basic styling for the forms */
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
  box-sizing: border-box; /* Prevents padding from affecting width */
}

button {
  background-color: #4CAF50; /* Green */
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