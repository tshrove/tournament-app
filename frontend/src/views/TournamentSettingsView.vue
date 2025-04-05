<template>
  <div class="settings-view">
    <header class="page-header">
      <h1>Tournament Settings</h1>
      <p class="subtitle">Manage the core details and settings for this tournament.</p>
    </header>

    <div class="content-container">
      <!-- Settings Form Card -->
      <section class="card settings-card">
        <h2>Basic Information</h2>
        <form @submit.prevent="saveSettings" class="settings-form">
          <div class="form-group">
            <label for="tournament-name">Tournament Name <span class="required">*</span></label>
            <input
              id="tournament-name"
              type="text"
              v-model="tournamentName"
              required
              placeholder="Enter tournament name"
            />
          </div>
          <div class="form-group">
            <label for="tournament-description">Description</label>
            <textarea
              id="tournament-description"
              v-model="tournamentDescription"
              placeholder="Optional: Enter tournament description"
              rows="4"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="admin-password">Tournament Admin Password</label>
            <input
              id="admin-password"
              type="password"
              v-model="adminPassword"
              placeholder="Leave blank to keep current password"
              autocomplete="new-password"
            />
            <p class="help-text">Set or update the password needed for admin actions (scoring, etc.) within <strong>this tournament</strong>.</p>
          </div>
          <div class="form-actions">
            <!-- Feedback Area -->
            <transition name="fade">
                <span v-if="settingsError" class="save-error">{{ settingsError }}</span>
                <span v-else-if="settingsSaved" class="save-success">✓ Settings saved successfully!</span>
            </transition>
            <button
              class="btn btn-primary"
              type="submit"
              :disabled="saving || !isFormDirty"
            >
              <span v-if="saving" class="spinner"></span>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Danger Zone Card -->
      <section class="card danger-zone">
          <h2>Danger Zone</h2>
          <div class="danger-action">
            <div class="danger-description">
              <h3>Reset Tournament Data</h3>
              <p>Permanently removes all teams, games, schedule, and bracket data associated with this tournament. This cannot be undone.</p>
            </div>
            <button
              class="btn btn-danger"
              @click="confirmReset"
              :disabled="resetting || saving"
            >
              <span v-if="resetting" class="spinner"></span>
              {{ resetting ? 'Resetting...' : 'Reset Tournament Data' }}
            </button>
          </div>
      </section>

      <!-- Back Navigation -->
      <div class="actions-container">
        <button @click="navigateToAdmin" class="btn btn-outline">
          &larr; Back to Admin Dashboard
        </button>
      </div>
    </div>

    <!-- Confirmation Modal for Reset -->
    <transition name="fade">
      <div v-if="showResetModal" class="modal-overlay" @click.self="closeResetModal">
        <div class="modal-content card">
          <div class="modal-header">
            <h3>Confirm Tournament Reset</h3>
            <button class="modal-close-btn" @click="closeResetModal" aria-label="Close modal">&times;</button>
          </div>
          <div class="modal-body">
            <p>Are you absolutely sure you want to reset all data for:</p>
            <p class="tournament-name-emphasis">"{{ initialSettings.name }}"?</p>
            <p class="warning-text">
              <span class="warning-icon">⚠️</span>
              This action will permanently delete all associated <strong>teams, games, schedules, and bracket data</strong>. It cannot be undone.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeResetModal">Cancel</button>
            <button class="btn btn-danger" @click="resetTournament" :disabled="resetting">
              <span v-if="resetting" class="spinner"></span>
              {{ resetting ? 'Confirm Reset' : 'Yes, Reset Data' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';
import currentTournament from '../store/current-tournament'; // Assuming you need the ID

const route = useRoute();
const router = useRouter();

// Tournament ID
const tournamentId = computed(() => route.params.id || currentTournament.state.id);

// Form state
const tournamentName = ref('');
const tournamentDescription = ref('');
const adminPassword = ref('');

// Store initial settings to compare for changes
const initialSettings = ref({ name: '', description: '', adminPassword: '' });

// UI states
const loading = ref(true);
const saving = ref(false);
const settingsSaved = ref(false);
const settingsError = ref('');
const resetting = ref(false);
const showResetModal = ref(false);

// Computed property to check if form has changes
const isFormDirty = computed(() => {
  return (
    tournamentName.value !== initialSettings.value.name ||
    tournamentDescription.value !== initialSettings.value.description ||
    adminPassword.value !== '' // Only consider password dirty if it has a value
  );
});

// Load tournament settings
const loadSettings = async () => {
  if (!tournamentId.value) {
      settingsError.value = 'Tournament ID not found.';
      loading.value = false;
      return;
  }
  loading.value = true;
  settingsError.value = '';
  document.title = 'Loading Settings... - Rocketpad';

  try {
    const response = await api.getSettings({ tournament_id: tournamentId.value });
    tournamentName.value = response.data.name || '';
    tournamentDescription.value = response.data.description || '';
    adminPassword.value = ''; // Always clear password field on load

    // Store initial values
    initialSettings.value = {
        name: response.data.name || '',
        description: response.data.description || '',
        // Don't store the actual password for comparison
    };
    document.title = `Settings: ${initialSettings.value.name} - Rocketpad`;

  } catch (err) {
    console.error('Error loading tournament settings:', err);
    settingsError.value = 'Failed to load settings. Please try again.';
    document.title = 'Error Loading Settings - Rocketpad';
  } finally {
    loading.value = false;
  }
};

// Save tournament settings
const saveSettings = async () => {
  saving.value = true;
  settingsSaved.value = false;
  settingsError.value = '';

  const settingsData = {
      tournament_id: tournamentId.value,
      name: tournamentName.value,
      description: tournamentDescription.value,
      // Only include password if it's been entered
      ...(adminPassword.value && { admin_password: adminPassword.value })
  };

  try {
    await api.updateSettings(settingsData);
    settingsSaved.value = true;
    adminPassword.value = ''; // Clear password field after successful save

    // Update initial settings to reflect saved state
    initialSettings.value.name = tournamentName.value;
    initialSettings.value.description = tournamentDescription.value;

    // Update tournament name in the store if it changed
    if (currentTournament.state.id === tournamentId.value) {
        currentTournament.setTournament({ id: tournamentId.value, name: tournamentName.value });
    }

    // Reset success message after a delay
    setTimeout(() => {
      settingsSaved.value = false;
    }, 4000);

  } catch (err) {
    console.error('Error saving tournament settings:', err);
    settingsError.value = `Failed to save settings: ${err.response?.data?.message || err.message || 'Please try again.'}`;
  } finally {
    saving.value = false;
  }
};

// Navigation
const navigateToAdmin = () => {
  // Assuming AdminView route requires the tournament ID as param or uses the store
  router.push({ name: 'AdminView', params: { id: tournamentId.value } });
};

// Reset tournament logic
const confirmReset = () => {
  showResetModal.value = true;
};

const closeResetModal = () => {
    showResetModal.value = false;
}

const resetTournament = async () => {
  resetting.value = true;
  settingsError.value = ''; // Clear previous errors
  try {
    await api.resetTournament({ tournament_id: tournamentId.value });
    showResetModal.value = false;
    // Optionally show a success notification
    alert("Tournament data has been reset successfully.");
    // Might need to redirect or reload data depending on desired UX
    // For now, just close modal
  } catch (err) {
    console.error('Error resetting tournament:', err);
    settingsError.value = `Failed to reset tournament: ${err.response?.data?.message || err.message || 'Please try again.'}`;
    showResetModal.value = false; // Close modal on error too
  } finally {
    resetting.value = false;
  }
};

// Watch for route changes if needed, though ID should be stable here
// watch(() => route.params.id, (newId) => { ... });

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.settings-view {
  width: 100%;
}

.page-header {
  /* Consistent header style */
  text-align: left;
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.page-header h1 {
  /* Use global h1 style */
  margin: 0 0 var(--space-xs) 0;
}

.subtitle {
  /* Consistent subtitle style */
  font-size: 1.1rem;
  color: var(--color-text-light);
  margin: 0;
}

.content-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

/* Settings Card */
.settings-card {
  /* Inherits .card styles */
}

.settings-card h2 {
  /* Consistent section header */
  margin-top: 0;
  margin-bottom: var(--space-lg);
  color: var(--color-accent);
  font-size: 1.4rem;
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

/* Remove pseudo-element */
/* .settings-card h2::after { ... } */

.settings-form {
  /* Uses global form styles */
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-group:last-child {
    margin-bottom: 0;
}

/* Use global label styles */
/* label { ... } */

label .required {
    color: var(--color-danger);
    margin-left: var(--space-xs);
}

/* Use global input/textarea styles */
/* input, textarea { ... } */

.form-help {
  /* Consistent help text style */
  margin-top: var(--space-sm);
  font-size: 0.85rem;
  color: var(--color-text-light);
  line-height: 1.5;
}
.form-help strong {
    color: var(--color-text);
    font-weight: 600;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end; /* Align button right */
  flex-wrap: wrap; /* Allow wrapping */
  gap: var(--space-md);
  margin-top: var(--space-xl);
  padding-top: var(--space-lg);
  border-top: 1px solid var(--color-border);
}

.form-actions .spinner {
    /* Consistent spinner */
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

/* Save Feedback Styles */
.save-success,
.save-error {
  font-weight: 500;
  font-size: 0.9rem;
  margin-right: auto; /* Push feedback to the left */
}

.save-success {
  color: var(--color-success);
}

.save-error {
  color: var(--color-danger);
}

/* Back Button Container */
.actions-container {
  text-align: center;
  margin-top: 0; /* Remove extra top margin */
  margin-bottom: var(--space-lg); /* Add bottom margin */
}

/* Danger Zone Card */
.danger-zone {
  /* Inherits .card */
  border-color: var(--color-danger);
  background-color: rgba(244, 63, 94, 0.02);
}

.danger-zone h2 {
  color: var(--color-danger);
  border-bottom-color: rgba(244, 63, 94, 0.3);
}

/* Remove duplicate warning text style */
/* .warning-text { ... } */

.danger-action {
  /* Consistent danger action layout */
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
  /* No top border needed here */
}

.danger-description {
    flex-grow: 1; /* Allow text to take space */
}

.danger-description h3 {
  margin: 0 0 var(--space-xs) 0;
  color: var(--color-text);
  font-size: 1.1rem;
}

.danger-description p {
  margin: 0;
  color: var(--color-text-light);
  font-size: 0.9rem;
  max-width: 500px;
}

.danger-action .btn {
    flex-shrink: 0;
}

/* Use global button styles */
/* .btn-danger, .btn-danger:hover, .btn-danger:disabled { ... } */

/* Modal Styles (Copied from previous views) */
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
  /* Inherits .card */
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
  /* Consistent warning style */
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
  line-height: 1.5;
}

.warning-icon {
    font-size: 1.1rem;
    line-height: 1.5;
}

.warning-text strong {
    color: #92400e; /* Darker warning text */
    font-weight: 600;
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
    /* Consistent spinner */
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

/* Responsive */
@media (max-width: 768px) {
  .danger-action {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
  .danger-description p {
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
    .form-actions {
        flex-direction: column;
        align-items: stretch;
    }
    .form-actions .btn {
        order: 2;
    }
    .form-actions .save-success,
    .form-actions .save-error {
        order: 1;
        text-align: center;
        margin-right: 0;
        margin-bottom: var(--space-sm);
    }
}

</style> 