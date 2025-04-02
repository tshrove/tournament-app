<template>
  <div class="admin-view">
    <header class="admin-header">
      <h1>Tournament Admin Dashboard</h1>
      <p class="subtitle">Manage all aspects of your tournament</p>
    </header>
    
    <div class="admin-content">
      <!-- Tournament Settings Section -->
      <section class="tournament-settings-section">
        <div class="admin-nav-card">
          <h2>Tournament Settings</h2>
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
      
      <section class="admin-nav-section">
        <div class="admin-nav-card">
          <h2>Administrative Functions</h2>
          
          <div class="admin-nav-links">
            <router-link to="/manage-teams" class="admin-nav-link">
              <div class="icon-container">👥</div>
              <div class="admin-nav-link-content">
                <h3>Team Management</h3>
                <p>Add, edit, and manage teams</p>
              </div>
            </router-link>
            
            <router-link to="/manage-schedule" class="admin-nav-link">
              <div class="icon-container">📅</div>
              <div class="admin-nav-link-content">
                <h3>Schedule Management</h3>
                <p>Create and edit game schedule</p>
              </div>
            </router-link>
            
            <router-link to="/game-scoring" class="admin-nav-link">
              <div class="icon-container">🏆</div>
              <div class="admin-nav-link-content">
                <h3>Game Scoring</h3>
                <p>Add scores to scheduled games</p>
              </div>
            </router-link>
            
            <router-link to="/bracket" class="admin-nav-link">
              <div class="icon-container">🎯</div>
              <div class="admin-nav-link-content">
                <h3>Bracket Management</h3>
                <p>Manage tournament bracket</p>
              </div>
            </router-link>
            
            <router-link to="/rankings" class="admin-nav-link">
              <div class="icon-container">📊</div>
              <div class="admin-nav-link-content">
                <h3>Rankings</h3>
                <p>View team standings and statistics</p>
              </div>
            </router-link>
          </div>
        </div>
      </section>
      
      <section class="quick-actions-section">
        <div class="admin-action-card">
          <h2>Quick Actions</h2>
          <div class="action-buttons">
            <button class="btn btn-primary" @click="navigateTo('/manage-teams')">
              Add New Team
            </button>
            <button class="btn btn-primary" @click="navigateTo('/manage-schedule')">
              Schedule Game
            </button>
            <button class="btn btn-primary" @click="navigateTo('/game-scoring')">
              Update Game Scores
            </button>
          </div>
        </div>
        
        <div class="admin-action-card">
          <h2>Return to Public View</h2>
          <p>Go back to the public tournament dashboard</p>
          <router-link to="/" class="btn btn-outline">
            Tournament Dashboard
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';
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

const navigateTo = (path) => {
  router.push(path);
};

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
.admin-view {
  width: 100%;
}

.admin-header {
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.admin-header h1 {
  font-size: 2rem;
  margin-bottom: var(--space-xs);
  color: var(--color-accent);
}

.subtitle {
  color: var(--color-text-light);
  margin: 0;
}

.admin-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-xl);
}

.tournament-settings-section {
  grid-column: 1 / -1;
  margin-bottom: var(--space-lg);
}

.settings-form {
  margin-top: var(--space-md);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-primary:disabled {
  background-color: var(--color-muted);
  cursor: not-allowed;
}

.save-success {
  color: var(--color-success, #4CAF50);
}

.save-error {
  color: var(--color-error, #f44336);
}

.admin-nav-section, .quick-actions-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.admin-nav-card, .admin-action-card {
  background-color: var(--color-background-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
}

.admin-nav-card h2, .admin-action-card h2 {
  margin-top: 0;
  margin-bottom: var(--space-lg);
  color: var(--color-accent);
  font-size: 1.4rem;
  position: relative;
  padding-bottom: var(--space-sm);
}

.admin-nav-card h2::after, .admin-action-card h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-secondary));
  border-radius: var(--radius-full);
}

.admin-nav-links {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-md);
}

.admin-nav-link {
  display: flex;
  gap: var(--space-md);
  align-items: center;
  padding: var(--space-md);
  background-color: var(--color-background);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text);
  transition: all var(--transition-fast);
  border: 1px solid var(--color-border);
}

.admin-nav-link:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
  text-decoration: none;
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background-color: rgba(67, 97, 238, 0.1);
  border-radius: var(--radius-md);
  font-size: 1.5rem;
}

.admin-nav-link-content h3 {
  margin: 0 0 var(--space-xs) 0;
  font-size: 1.1rem;
  color: var(--color-accent);
}

.admin-nav-link-content p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-light);
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.admin-action-card p {
  color: var(--color-text-light);
  margin-bottom: var(--space-md);
}

/* Responsive Adjustments */
@media (max-width: 992px) {
  .admin-content {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }
}

@media (max-width: 768px) {
  .admin-header h1 {
    font-size: 1.75rem;
  }
  
  .admin-nav-links {
    grid-template-columns: 1fr;
  }
  
  .admin-nav-card, .admin-action-card {
    padding: var(--space-md);
  }
}
</style> 