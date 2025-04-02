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
const saving = ref(false);
const settingsSaved = ref(false);
const settingsError = ref('');

// Load tournament settings
const loadSettings = async () => {
  try {
    const response = await api.getSettings();
    tournamentName.value = response.data.name;
    tournamentDescription.value = response.data.description || '';
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
      description: tournamentDescription.value
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

@media (max-width: 768px) {
  .settings-card {
    padding: var(--space-lg);
  }
  
  .page-header h1 {
    font-size: 1.75rem;
  }
}
</style> 