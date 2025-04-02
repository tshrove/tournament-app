<script setup>
import { ref, onMounted, inject } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import ScheduleTable from '../components/ScheduleTable.vue';
// Import flatpickr
import flatPickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';
import 'flatpickr/dist/themes/material_green.css';

const router = useRouter();
const showNotification = inject('showNotification');

const teams = ref([]);
const schedule = ref([]);
const loading = ref(true);
const showForm = ref(false);

// New game form data
const newGame = ref({
  team1_id: '',
  team2_id: '',
  date: '',
  time: '',
  field: '',
  status: 'Scheduled'
});

// Flatpickr options
const flatpickrOptions = {
  dateFormat: 'Y-m-d',
  altFormat: 'F j, Y',
  altInput: true,
  allowInput: true,
  appendTo: document.body, // Prevents positioning issues
  static: true,
  theme: 'material_green'
};

// Form validation errors
const errors = ref({});

// Load teams and schedule data
const loadData = async () => {
  loading.value = true;
  try {
    const [teamsResponse, scheduleResponse] = await Promise.all([
      api.getTeams(),
      api.getSchedule()
    ]);
    teams.value = teamsResponse.data;
    schedule.value = scheduleResponse.data;
  } catch (err) {
    showNotification('Error loading data: ' + (err.response?.data?.error || err.message), 'error');
  } finally {
    loading.value = false;
  }
};

// Validate form fields
const validateForm = () => {
  errors.value = {};
  
  if (!newGame.value.team1_id) {
    errors.value.team1_id = 'Please select the first team';
  }
  
  if (!newGame.value.team2_id) {
    errors.value.team2_id = 'Please select the second team';
  } else if (newGame.value.team1_id === newGame.value.team2_id) {
    errors.value.team2_id = 'Teams cannot play against themselves';
  }
  
  if (!newGame.value.date) {
    errors.value.date = 'Date is required';
  }
  
  if (!newGame.value.time) {
    errors.value.time = 'Time is required';
  }
  
  if (!newGame.value.field) {
    errors.value.field = 'Field name is required';
  }
  
  return Object.keys(errors.value).length === 0;
};

// Add a new game to the schedule
const addGame = async () => {
  if (!validateForm()) {
    return;
  }
  
  try {
    await api.createScheduledGame(newGame.value);
    showNotification('Game added to schedule', 'success');
    resetForm();
    loadData(); // Refresh data
  } catch (err) {
    showNotification('Error adding game: ' + (err.response?.data?.error || err.message), 'error');
  }
};

// Reset form to default values
const resetForm = () => {
  newGame.value = {
    team1_id: '',
    team2_id: '',
    date: '',
    time: '',
    field: '',
    status: 'Scheduled'
  };
  errors.value = {};
  showForm.value = false;
};

// Delete a game from the schedule
const handleDeleteGame = async (gameId) => {
  try {
    await api.deleteScheduledGame(gameId);
    showNotification('Game removed from schedule', 'success');
    loadData(); // Refresh data
  } catch (err) {
    showNotification('Error removing game: ' + (err.response?.data?.error || err.message), 'error');
  }
};

// Initialize component
onMounted(loadData);
</script>

<template>
  <div class="manage-schedule">
    <div class="page-header">
      <h1>Manage Schedule</h1>
      <div class="header-actions">
        <button 
          v-if="!showForm" 
          @click="showForm = true" 
          class="btn btn-primary"
        >
          <i class="icon">+</i> Add New Game
        </button>
        <button 
          v-else 
          @click="resetForm" 
          class="btn btn-secondary"
        >
          <i class="icon">×</i> Cancel
        </button>
        <router-link to="/schedule" class="btn btn-outline">
          View Schedule
        </router-link>
      </div>
    </div>
    
    <!-- Game Form -->
    <transition name="slide-fade">
      <div v-if="showForm" class="card game-form">
        <h2 class="card-title">Add New Game</h2>
        <form @submit.prevent="addGame">
          <div class="form-section">
            <h3 class="section-title">Team Information</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="team1">Home Team</label>
                <select 
                  id="team1" 
                  v-model="newGame.team1_id" 
                  :class="{ 'is-invalid': errors.team1_id }"
                >
                  <option value="">Select Home Team</option>
                  <option 
                    v-for="team in teams" 
                    :key="team.id" 
                    :value="team.id"
                  >
                    {{ team.name }}
                  </option>
                </select>
                <div v-if="errors.team1_id" class="error-message">
                  {{ errors.team1_id }}
                </div>
              </div>
              
              <div class="form-group">
                <label for="team2">Away Team</label>
                <select 
                  id="team2" 
                  v-model="newGame.team2_id" 
                  :class="{ 'is-invalid': errors.team2_id }"
                >
                  <option value="">Select Away Team</option>
                  <option 
                    v-for="team in teams" 
                    :key="team.id" 
                    :value="team.id"
                    :disabled="team.id === newGame.team1_id"
                  >
                    {{ team.name }}
                  </option>
                </select>
                <div v-if="errors.team2_id" class="error-message">
                  {{ errors.team2_id }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">Game Details</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="date">Date</label>
                <!-- Use flatpickr for the date picker -->
                <flat-pickr
                  v-model="newGame.date"
                  :config="flatpickrOptions"
                  :class="{ 'is-invalid': errors.date }"
                  class="date-picker"
                  placeholder="Select date..."
                />
                <div v-if="errors.date" class="error-message">
                  {{ errors.date }}
                </div>
              </div>
              
              <div class="form-group">
                <label for="time">Time</label>
                <input 
                  type="time" 
                  id="time" 
                  v-model="newGame.time" 
                  :class="{ 'is-invalid': errors.time }"
                />
                <div v-if="errors.time" class="error-message">
                  {{ errors.time }}
                </div>
              </div>
              
              <div class="form-group">
                <label for="field">Field</label>
                <input 
                  type="text" 
                  id="field" 
                  v-model="newGame.field" 
                  placeholder="Field name"
                  :class="{ 'is-invalid': errors.field }"
                />
                <div v-if="errors.field" class="error-message">
                  {{ errors.field }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="resetForm" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Add to Schedule</button>
          </div>
        </form>
      </div>
    </transition>
    
    <!-- Schedule Table -->
    <div v-if="loading" class="loading-container">
      <div class="loader"></div>
      <p>Loading data...</p>
    </div>
    
    <div v-else-if="schedule.length === 0" class="empty-state card">
      <div class="empty-icon">📅</div>
      <h2>No Games Scheduled</h2>
      <p>There are no games in the schedule yet. Get started by adding your first game.</p>
      <button @click="showForm = true" class="btn btn-primary btn-lg">
        <i class="icon">+</i> Add Your First Game
      </button>
    </div>
    
    <div v-else class="schedule-container">
      <div class="card">
        <h2 class="card-title">Current Schedule</h2>
        <ScheduleTable 
          :games="schedule" 
          @delete-game="handleDeleteGame"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.manage-schedule {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.page-header h1 {
  margin-bottom: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

.icon {
  display: inline-block;
  margin-right: var(--space-xs);
  font-style: normal;
}

/* Form styling */
.game-form {
  margin-bottom: var(--space-xl);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: var(--space-lg);
  color: var(--color-accent);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--space-sm);
}

.form-section {
  margin-bottom: var(--space-lg);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: var(--space-md);
  color: var(--color-text);
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-lg);
  margin-bottom: var(--space-md);
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.error-message {
  color: var(--color-danger);
  font-size: 0.875rem;
  margin-top: var(--space-xs);
}

.is-invalid {
  border-color: var(--color-danger);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-xl);
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-lg);
}

/* Style the flatpickr input */
.date-picker {
  height: 42px;
}

/* Empty state styling */
.empty-state {
  text-align: center;
  padding: var(--space-xxl) var(--space-xl);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--space-md);
}

.empty-state h2 {
  margin-bottom: var(--space-sm);
}

.empty-state p {
  color: var(--color-text-light);
  max-width: 500px;
  margin: 0 auto var(--space-lg);
}

/* Loading state */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xxl) 0;
}

.loader {
  border: 4px solid var(--color-background-dark);
  border-radius: 50%;
  border-top: 4px solid var(--color-primary);
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-md);
}

.loading-container p {
  color: var(--color-text-light);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Transition animations */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* Schedule container */
.schedule-container {
  margin-top: var(--space-xl);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    margin-top: var(--space-md);
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}
</style> 