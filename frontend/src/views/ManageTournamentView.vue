<template>
  <div class="manage-tournament-view">
    <header class="page-header">
      <h1>{{ isEditing ? 'Edit Tournament' : 'Create Tournament' }}</h1>
      <p class="subtitle">{{ isEditing ? 'Update tournament details' : 'Set up a new tournament' }}</p>
    </header>
    
    <div class="content-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading tournament data...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="btn primary" @click="goBack">Go Back</button>
      </div>
      
      <form v-else @submit.prevent="saveTournament" class="tournament-form">
        <div class="form-group">
          <label for="name">Tournament Name*</label>
          <input 
            type="text" 
            id="name" 
            v-model="formData.name" 
            required 
            placeholder="Enter tournament name"
          />
        </div>
        
        <div class="form-group">
          <label for="description">Description</label>
          <textarea 
            id="description" 
            v-model="formData.description" 
            rows="4" 
            placeholder="Enter tournament description"
          ></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="startDate">Start Date</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="formData.start_date"
            />
          </div>
          
          <div class="form-group">
            <label for="endDate">End Date</label>
            <input 
              type="date" 
              id="endDate" 
              v-model="formData.end_date"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="location">Location</label>
          <input 
            type="text" 
            id="location" 
            v-model="formData.location" 
            placeholder="Enter tournament location"
          />
        </div>
        
        <div class="form-group">
          <label for="status">Status</label>
          <select id="status" v-model="formData.status">
            <option value="Active">Active</option>
            <option value="Upcoming">Upcoming</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
        
        <div class="form-group admin-password">
          <label for="adminPassword">Admin Password</label>
          <input 
            type="password" 
            id="adminPassword" 
            v-model="formData.admin_password" 
            placeholder="Set admin password for this tournament"
          />
          <p class="help-text">This password will be required to access admin features for this tournament.</p>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn secondary" @click="goBack">Cancel</button>
          <button type="submit" class="btn primary" :disabled="saving">
            {{ saving ? 'Saving...' : (isEditing ? 'Update Tournament' : 'Create Tournament') }}
          </button>
        </div>
      </form>
      
      <div v-if="isEditing" class="danger-zone">
        <h3>Danger Zone</h3>
        <div class="danger-action">
          <div>
            <h4>Delete Tournament</h4>
            <p>Once deleted, all data including teams, games, and brackets will be permanently removed.</p>
          </div>
          <button class="btn danger" @click="confirmDelete">Delete Tournament</button>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirm Deletion</h3>
        <p>Are you sure you want to delete this tournament? This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn danger" @click="deleteTournament">Delete Tournament</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();

// Form data
const formData = ref({
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  location: '',
  status: 'Active',
  admin_password: ''
});

// UI states
const loading = ref(false);
const saving = ref(false);
const error = ref(null);
const showDeleteModal = ref(false);

// Check if we're editing an existing tournament or creating a new one
const isEditing = computed(() => {
  return route.name === 'ManageTournament' && route.params.id;
});

// Load tournament data if editing
const loadTournament = async () => {
  if (!isEditing.value) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const tournamentId = route.params.id;
    const tournamentResponse = await api.getTournament(tournamentId);
    const settingsResponse = await api.getSettings({ tournament_id: tournamentId });
    
    // Populate form with tournament data
    formData.value = {
      ...tournamentResponse.data,
      admin_password: settingsResponse.data.adminPassword || ''
    };
  } catch (err) {
    console.error('Error loading tournament:', err);
    error.value = 'Failed to load tournament data. Please try again later.';
  } finally {
    loading.value = false;
  }
};

// Save tournament data
const saveTournament = async () => {
  saving.value = true;
  error.value = null;
  
  try {
    // Create a copy of form data to avoid mutating the original
    const tournamentData = { ...formData.value };
    
    // Make sure dates are in the correct format (YYYY-MM-DD)
    // If empty string, set to null to avoid backend parsing errors
    if (tournamentData.start_date === '') {
      tournamentData.start_date = null;
    }
    
    if (tournamentData.end_date === '') {
      tournamentData.end_date = null;
    }
    
    if (isEditing.value) {
      // Update existing tournament
      const tournamentId = route.params.id;
      await api.updateTournament(tournamentId, tournamentData);
      
      // Update tournament settings
      await api.updateSettings({
        tournament_id: tournamentId,
        name: tournamentData.name,
        description: tournamentData.description,
        admin_password: tournamentData.admin_password
      });
    } else {
      // Create new tournament
      const response = await api.createTournament(tournamentData);
      const newTournamentId = response.data.id;
      
      // No need to update settings as they're created with the tournament
    }
    
    // Navigate back to tournaments list
    router.push({ name: 'Tournaments' });
  } catch (err) {
    console.error('Error saving tournament:', err);
    error.value = 'Failed to save tournament. Please try again later.';
  } finally {
    saving.value = false;
  }
};

// Delete tournament
const confirmDelete = () => {
  showDeleteModal.value = true;
};

const deleteTournament = async () => {
  saving.value = true;
  error.value = null;
  
  try {
    const tournamentId = route.params.id;
    await api.deleteTournament(tournamentId);
    showDeleteModal.value = false;
    router.push({ name: 'Tournaments' });
  } catch (err) {
    console.error('Error deleting tournament:', err);
    error.value = 'Failed to delete tournament. Please try again later.';
    showDeleteModal.value = false;
  } finally {
    saving.value = false;
  }
};

// Go back to previous page
const goBack = () => {
  router.push({ name: 'Tournaments' });
};

onMounted(() => {
  loadTournament();
  document.title = isEditing.value ? 'Edit Tournament' : 'Create Tournament';
});
</script>

<style scoped>
.manage-tournament-view {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-primary);
}

.subtitle {
  font-size: 1.2rem;
  color: var(--color-text-secondary);
  margin-bottom: 0;
}

.content-container {
  max-width: 800px;
  margin: 0 auto;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  text-align: center;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid var(--color-primary);
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.tournament-form {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

input, textarea, select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea {
  resize: vertical;
}

.help-text {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.primary {
  background-color: var(--color-primary);
  color: white;
}

.primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.secondary {
  background-color: #f0f0f0;
  color: #333;
}

.secondary:hover {
  background-color: #e0e0e0;
}

.danger {
  background-color: #f44336;
  color: white;
}

.danger:hover {
  background-color: #d32f2f;
}

.danger-zone {
  margin-top: 3rem;
  padding: 1.5rem;
  border: 1px solid #f44336;
  border-radius: 8px;
}

.danger-zone h3 {
  color: #f44336;
  margin-top: 0;
  margin-bottom: 1rem;
}

.danger-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.danger-action h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.danger-action p {
  margin-top: 0;
  color: var(--color-text-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin-top: 0;
  color: var(--color-text-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .danger-action {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style> 