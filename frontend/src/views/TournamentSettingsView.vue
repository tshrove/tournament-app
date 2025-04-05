<template>
  <div class="settings-view">
    <header class="page-header">
      <h1>Tournament Settings</h1>
      <p class="subtitle">Configure your tournament details</p>
    </header>
    
    <div class="content-container">
      <section class="settings-section">
        <div class="settings-card">
          <h2>Basic Information</h2>
          <div class="settings-form">
            <div class="form-group">
              <label for="tournament-name">Tournament Name</label>
              <input 
                id="tournament-name" 
                type="text" 
                v-model="tournamentName" 
                class="form-control" 
                placeholder="Enter tournament name"
              >
            </div>
            <div class="form-group">
              <label for="tournament-description">Description (Optional)</label>
              <textarea 
                id="tournament-description" 
                v-model="tournamentDescription" 
                class="form-control" 
                placeholder="Enter tournament description"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="admin-password">Admin Password (Optional)</label>
              <input 
                id="admin-password" 
                type="password" 
                v-model="adminPassword" 
                class="form-control" 
                placeholder="Set custom admin password"
              >
              <small class="form-help">Set a custom password for admin access. If left empty, the default password will be used.</small>
            </div>
            <div class="form-actions">
              <button 
                class="btn btn-primary" 
                @click="saveSettings" 
                :disabled="saving"
              >
                {{ saving ? 'Saving...' : 'Save Settings' }}
              </button>
              <span v-if="settingsSaved" class="save-success">✓ Settings saved</span>
              <span v-if="settingsError" class="save-error">{{ settingsError }}</span>
            </div>
          </div>
        </div>
      </section>
      
      <section class="settings-section">
        <div class="settings-card danger-zone">
          <h2>Danger Zone</h2>
          <p class="warning-text">These actions cannot be undone. Proceed with caution.</p>
          
          <div class="danger-action">
            <div class="danger-description">
              <h3>Reset Tournament</h3>
              <p>This will remove all teams, games, schedules, and bracket data. The tournament will be reset to its initial state.</p>
            </div>
            <button 
              class="btn btn-danger" 
              @click="confirmReset"
              :disabled="resetting"
            >
              {{ resetting ? 'Resetting...' : 'Reset Tournament' }}
            </button>
          </div>
        </div>
      </section>
      
      <div class="actions-container">
        <button @click="navigateToAdmin" class="btn btn-outline">
          Back to Admin Dashboard
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();

// Tournament settings
const tournamentName = ref('');
const tournamentDescription = ref('');
const adminPassword = ref('');
const saving = ref(false);
const settingsSaved = ref(false);
const settingsError = ref('');
const resetting = ref(false);

// Load tournament settings
const loadSettings = async () => {
  try {
    const response = await api.getSettings();
    tournamentName.value = response.data.name;
    tournamentDescription.value = response.data.description || '';
    adminPassword.value = response.data.adminPassword || '';
  } catch (err) {
    console.error('Error loading tournament settings:', err);
    settingsError.value = 'Failed to load settings';
  }
};

// Save tournament settings
const saveSettings = async () => {
  saving.value = true;
  settingsSaved.value = false;
  settingsError.value = '';
  
  try {
    await api.updateSettings({
      name: tournamentName.value,
      description: tournamentDescription.value,
      adminPassword: adminPassword.value
    });
    settingsSaved.value = true;
    
    // Reset success message after a delay
    setTimeout(() => {
      settingsSaved.value = false;
    }, 3000);
  } catch (err) {
    console.error('Error saving tournament settings:', err);
    settingsError.value = 'Failed to save settings';
  } finally {
    saving.value = false;
  }
};

const navigateToAdmin = () => {
  router.push('/admin');
};

// Reset tournament
const confirmReset = () => {
  if (confirm("WARNING: This will delete all teams, games, and schedules. This action cannot be undone. Are you sure you want to reset the tournament?")) {
    resetTournament();
  }
};

const resetTournament = async () => {
  resetting.value = true;
  try {
    await api.resetTournament();
    alert("Tournament has been reset successfully.");
    // Reload settings to reflect changes
    await loadSettings();
  } catch (err) {
    console.error('Error resetting tournament:', err);
    alert("Failed to reset tournament. Please try again.");
  } finally {
    resetting.value = false;
  }
};

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.settings-view {
  width: 100%;
}

.page-header {
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
  text-align: center;
}

.page-header h1 {
  font-size: 2rem;
  margin-bottom: var(--space-xs);
  color: var(--color-accent);
}

.subtitle {
  color: var(--color-text-light);
  margin: 0;
}

.content-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-section {
  margin-bottom: var(--space-xl);
}

.settings-card {
  background-color: var(--color-background-card);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  box-shadow: var(--shadow-md);
}

.settings-card h2 {
  margin-top: 0;
  margin-bottom: var(--space-lg);
  color: var(--color-accent);
  font-size: 1.4rem;
  position: relative;
  padding-bottom: var(--space-sm);
}

.settings-card h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-secondary));
  border-radius: var(--radius-full);
}

.settings-form {
  margin-top: var(--space-md);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  transition: border-color var(--transition-fast);
}

.form-control:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.1);
}

.form-help {
  display: block;
  margin-top: 0.5rem;
  color: var(--color-text-light);
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: var(--space-lg);
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-primary:disabled {
  background-color: var(--color-muted);
  cursor: not-allowed;
}

.btn-outline {
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.btn-outline:hover {
  background-color: rgba(67, 97, 238, 0.05);
}

.save-success {
  color: var(--color-success);
  font-weight: 500;
}

.save-error {
  color: var(--color-danger);
  font-weight: 500;
}

.actions-container {
  text-align: center;
  margin-top: var(--space-xl);
  margin-bottom: var(--space-xl);
}

.danger-zone {
  border: 1px solid var(--color-danger);
}

.danger-zone h2 {
  color: var(--color-danger);
}

.warning-text {
  color: var(--color-danger);
  font-weight: 500;
  margin-bottom: var(--space-md);
}

.danger-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) 0;
  border-top: 1px solid var(--color-border);
}

.danger-description h3 {
  margin: 0 0 var(--space-xs) 0;
  color: var(--color-text);
}

.danger-description p {
  margin: 0;
  color: var(--color-text-light);
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-danger:disabled {
  background-color: #e4606d;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .settings-card {
    padding: var(--space-lg);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
  }
}
</style> 