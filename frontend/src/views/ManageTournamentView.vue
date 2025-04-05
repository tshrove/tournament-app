<template>
  <div class="manage-tournament-view">
    <header class="page-header">
      <h1>{{ isEditing ? 'Edit Tournament' : 'Create New Tournament' }}</h1>
      <p class="subtitle">{{ isEditing ? 'Update the details for this tournament.' : 'Fill in the details to set up a new tournament.' }}</p>
    </header>
    
    <div class="content-container">
      <div v-if="loading && isEditing" class="loading-state card">
        <div class="loading-spinner"></div>
        <p>Loading tournament data...</p>
      </div>
      
      <div v-else-if="error" class="error-state card">
        <p>{{ error }}</p>
        <button class="btn btn-secondary" @click="goBack">Go Back</button>
      </div>
      
      <form v-else @submit.prevent="saveTournament" class="tournament-form card">
        <div class="form-section">
          <div class="form-group">
            <label for="name">Tournament Name <span class="required">*</span></label>
            <input 
              type="text" 
              id="name" 
              v-model="formData.name" 
              required 
              placeholder="e.g., Spring Softball Classic"
            />
          </div>
          
          <div class="form-group">
            <label for="description">Description</label>
            <textarea 
              id="description" 
              v-model="formData.description" 
              rows="4" 
              placeholder="Optional: Provide a brief description or details about the tournament"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="startDate">Start Date</label>
              <input 
                type="date" 
                id="startDate" 
                v-model="formData.start_date"
                class="date-picker"
              />
            </div>
            
            <div class="form-group">
              <label for="endDate">End Date</label>
              <input 
                type="date" 
                id="endDate" 
                v-model="formData.end_date"
                class="date-picker"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="location">Location</label>
            <input 
              type="text" 
              id="location" 
              v-model="formData.location" 
              placeholder="e.g., City Park Fields"
            />
          </div>
          
          <div class="form-group">
            <label for="status">Status</label>
            <select id="status" v-model="formData.status">
              <option value="Upcoming">Upcoming</option>
              <option value="Active">Active</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </div>
        
        <div class="form-section admin-section">
          <h4>Admin Settings</h4>
          <div class="form-group admin-password">
            <label for="adminPassword">Tournament Admin Password</label>
            <input 
              type="password" 
              id="adminPassword" 
              v-model="formData.admin_password" 
              placeholder="Leave blank to keep unchanged (if editing)"
              autocomplete="new-password"
            />
            <p class="help-text">Set or update the password required to access admin functions (like scoring, scheduling) for <strong>this specific tournament</strong>.</p>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="goBack" :disabled="saving">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <span v-if="saving" class="spinner"></span>
            {{ saving ? 'Saving...' : (isEditing ? 'Update Tournament' : 'Create Tournament') }}
          </button>
        </div>
      </form>
      
      <div v-if="isEditing" class="danger-zone card">
        <div class="danger-header">
          <h3>Danger Zone</h3>
        </div>
        <div class="danger-content">
          <div class="danger-action">
            <div>
              <h4>Delete this Tournament</h4>
              <p>Once deleted, all associated data (teams, games, schedule, results, bracket) will be permanently removed. This action cannot be undone.</p>
            </div>
            <button class="btn btn-danger" @click="confirmDelete" :disabled="saving">
              Delete Tournament
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <transition name="fade">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-content card">
          <div class="modal-header">
            <h3>Confirm Deletion</h3>
            <button class="modal-close-btn" @click="closeDeleteModal" aria-label="Close modal">&times;</button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to permanently delete the tournament:</p>
            <p class="tournament-name-emphasis">"{{ formData.name }}"?</p>
            <p class="warning-text">
              <span class="warning-icon">⚠️</span>
              This action cannot be undone. All associated data will be permanently removed.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeDeleteModal">Cancel</button>
            <button class="btn btn-danger" @click="deleteTournament" :disabled="saving">
              <span v-if="saving" class="spinner"></span>
              {{ saving ? 'Deleting...' : 'Confirm Delete' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
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
  status: 'Upcoming',
  admin_password: ''
});

// UI states
const loading = ref(false);
const saving = ref(false);
const error = ref(null);
const showDeleteModal = ref(false);

// Check if we're editing an existing tournament
const isEditing = computed(() => !!route.params.id);

// Format date for input type=date (YYYY-MM-DD)
const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    // Adjust for timezone offset to get the correct local date
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().split('T')[0];
  } catch (e) {
    console.error("Error formatting date:", e);
    return ''; // Return empty if date is invalid
  }
};

// Load tournament data if editing
const loadTournament = async () => {
  if (!isEditing.value) {
    document.title = 'Create Tournament - Rocketpad';
    return;
  }

  loading.value = true;
  error.value = null;
  document.title = 'Loading Tournament... - Rocketpad';

  try {
    const tournamentId = route.params.id;
    // Fetch tournament details and settings concurrently
    const [tournamentResponse, settingsResponse] = await Promise.all([
      api.getTournament(tournamentId),
      api.getSettings({ tournament_id: tournamentId })
    ]);

    // Populate form data, formatting dates correctly for input fields
    formData.value = {
      ...tournamentResponse.data,
      start_date: formatDateForInput(tournamentResponse.data.start_date),
      end_date: formatDateForInput(tournamentResponse.data.end_date),
      admin_password: '' // Clear password field for security
      // admin_password: settingsResponse.data.adminPassword || '' // Or fetch if needed, but generally avoid pre-filling passwords
    };
    document.title = `Edit: ${formData.value.name} - Rocketpad`;

  } catch (err) {
    console.error('Error loading tournament:', err);
    error.value = 'Failed to load tournament data. Please check the ID or try again later.';
    document.title = 'Error Loading Tournament - Rocketpad';
  } finally {
    loading.value = false;
  }
};

// Save tournament data
const saveTournament = async () => {
  saving.value = true;
  error.value = null;
  
  try {
    // Prepare data for API (handle dates)
    const apiData = {
      ...formData.value,
      start_date: formData.value.start_date || null,
      end_date: formData.value.end_date || null,
    };
    // Don't send empty password string if not changing
    if (!apiData.admin_password && isEditing.value) {
      delete apiData.admin_password;
    }

    let tournamentId = route.params.id;

    if (isEditing.value) {
      // Update existing tournament
      await api.updateTournament(tournamentId, apiData);
      // Update settings (only if password is provided)
      if (apiData.admin_password) {
        await api.updateSettings({
          tournament_id: tournamentId,
          admin_password: apiData.admin_password
        });
      }
    } else {
      // Create new tournament
      const response = await api.createTournament(apiData);
      tournamentId = response.data.id;
      // Settings like password might be handled during creation by the backend
      // or require a separate settings call if needed immediately after creation
    }

    // Navigate back to the admin list (or the new tournament?)
    router.push({ name: 'TournamentAdmin' }); // Go back to admin list
    // Optionally navigate to the newly created/edited tournament dashboard:
    // router.push({ name: 'TournamentHome', params: { id: tournamentId } });

  } catch (err) {
    console.error('Error saving tournament:', err);
    // More specific error handling based on API response if possible
    error.value = `Failed to save tournament: ${err.response?.data?.message || err.message || 'Please try again.'}`;
  } finally {
    saving.value = false;
  }
};

// Delete tournament
const confirmDelete = () => {
  showDeleteModal.value = true;
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
};

const deleteTournament = async () => {
  if (!isEditing.value) return;

  saving.value = true; // Use saving state to disable buttons
  error.value = null;

  try {
    const tournamentId = route.params.id;
    await api.deleteTournament(tournamentId);
    showDeleteModal.value = false;
    // Navigate back to the admin list after successful deletion
    router.push({ name: 'TournamentAdmin' });
  } catch (err) {
    console.error('Error deleting tournament:', err);
    error.value = `Failed to delete tournament: ${err.response?.data?.message || err.message || 'Please try again.'}`;
    showDeleteModal.value = false; // Close modal even on error
  } finally {
    saving.value = false;
  }
};

// Go back to previous page
const goBack = () => {
  // Go back to the tournament admin list view
  router.push({ name: 'TournamentAdmin' });
};

onMounted(() => {
  loadTournament();
});
</script>

<style scoped>
.manage-tournament-view {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
  text-align: left;
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
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
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.loading-state, .error-state {
  padding: var(--space-xl) var(--space-lg);
  text-align: center;
  background-color: var(--color-background-alt);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-primary-light);
  border-left-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: var(--color-danger);
  background-color: rgba(244, 63, 94, 0.05);
  border: 1px solid rgba(244, 63, 94, 0.2);
}
.error-state p {
  margin-bottom: var(--space-md);
}

.tournament-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.form-section {
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--space-xl);
}
.form-section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.admin-section h4 {
  margin-top: 0;
  margin-bottom: var(--space-lg);
  color: var(--color-accent);
  font-size: 1.1rem;
}

.form-group {
  margin-bottom: var(--space-lg);
}
.form-group:last-child {
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
  align-items: start;
}

.form-row .form-group {
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

label .required {
  color: var(--color-danger);
  margin-left: var(--space-xs);
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
  margin-top: var(--space-sm);
  font-size: 0.85rem;
  color: var(--color-text-light);
  line-height: 1.5;
}
.help-text strong {
  color: var(--color-text);
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: var(--space-lg);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

.form-actions .spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: var(--space-xs);
  vertical-align: text-bottom;
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

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

.danger-zone {
  border-color: var(--color-danger);
  background-color: rgba(244, 63, 94, 0.02);
}

.danger-header {
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid rgba(244, 63, 94, 0.3);
  margin-bottom: var(--space-md);
}

.danger-zone h3 {
  color: var(--color-danger);
  margin: 0;
  font-size: 1.2rem;
}

.danger-action {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.danger-action h4 {
  margin: 0 0 var(--space-xs) 0;
  color: var(--color-text);
}

.danger-action p {
  margin: 0;
  color: var(--color-text-light);
  font-size: 0.9rem;
  max-width: 450px;
}

.danger-action .btn {
  flex-shrink: 0;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(17, 24, 39, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: var(--z-modal);
  padding: var(--space-md);
}

.modal-content {
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-md);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-accent);
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  line-height: 1;
  padding: 0 var(--space-xs);
  color: var(--color-text-light);
  cursor: pointer;
  transition: color var(--transition-fast);
}
.modal-close-btn:hover {
  color: var(--color-text);
}

.modal-body {
  overflow-y: auto;
  margin-bottom: var(--space-lg);
}

.tournament-name-emphasis {
  font-weight: 600;
  color: var(--color-primary-dark);
  margin: var(--space-xs) 0 var(--space-md) 0;
}

.warning-text {
  background-color: rgba(251, 191, 36, 0.1);
  color: #b45309;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  border: 1px solid rgba(251, 191, 36, 0.3);
  margin-top: var(--space-md);
}

.warning-icon {
  font-size: 1.1rem;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
  margin-top: auto;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.modal-footer .spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: var(--space-xs);
  vertical-align: text-bottom;
}

@media (max-width: 768px) {
  .danger-action {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
  .danger-action p {
    max-width: none;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.8rem;
  }
  .subtitle {
    font-size: 1rem;
  }
  .form-row {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }
  .form-actions {
    flex-direction: column-reverse;
    gap: var(--space-sm);
  }
  .form-actions .btn {
    width: 100%;
  }
}
</style> 