<template>
  <div class="admin-view">
    <header class="admin-header">
      <h1>{{ currentTournament.state.name }} Admin Dashboard</h1>
      <p class="subtitle">Manage all aspects of your tournament</p>
    </header>
    
    <div class="admin-content">
      <section class="admin-nav-section">
        <div class="admin-nav-card">
          <h2>Administrative Functions</h2>
          
          <div class="admin-nav-links">
            <router-link :to="`/tournament/${currentTournament.state.id}/settings`" class="admin-nav-link">
              <div class="icon-container">⚙️</div>
              <div class="admin-nav-link-content">
                <h3>Tournament Settings</h3>
                <p>Configure tournament details</p>
              </div>
            </router-link>
            
            <router-link :to="`/tournament/${currentTournament.state.id}/manage-teams`" class="admin-nav-link">
              <div class="icon-container">👥</div>
              <div class="admin-nav-link-content">
                <h3>Team Management</h3>
                <p>Add, edit, and manage teams</p>
              </div>
            </router-link>
            
            <router-link :to="`/tournament/${currentTournament.state.id}/manage-schedule`" class="admin-nav-link">
              <div class="icon-container">📅</div>
              <div class="admin-nav-link-content">
                <h3>Schedule Management</h3>
                <p>Create and edit game schedule</p>
              </div>
            </router-link>
            
            <router-link :to="`/tournament/${currentTournament.state.id}/game-scoring`" class="admin-nav-link">
              <div class="icon-container">🏆</div>
              <div class="admin-nav-link-content">
                <h3>Game Scoring</h3>
                <p>Add scores to scheduled games</p>
              </div>
            </router-link>
            
            <router-link :to="`/tournament/${currentTournament.state.id}/bracket`" class="admin-nav-link">
              <div class="icon-container">🎯</div>
              <div class="admin-nav-link-content">
                <h3>Bracket Management</h3>
                <p>Manage tournament bracket</p>
              </div>
            </router-link>
          </div>
        </div>
      </section>
      
      <section class="quick-actions-section">
        <div class="admin-action-card">
          <h2>Quick Actions</h2>
          <div class="action-buttons">
            <button class="btn btn-primary" @click="navigateToTeams">
              Add New Team
            </button>
            <button class="btn btn-primary" @click="navigateToSchedule">
              Schedule Game
            </button>
            <button class="btn btn-primary" @click="navigateToScoring">
              Update Game Scores
            </button>
            <button class="btn btn-primary" @click="navigateToSettings">
              Edit Tournament Settings
            </button>
          </div>
        </div>
        
        <div class="admin-action-card">
          <h2>Return to Public View</h2>
          <p>Go back to the public tournament dashboard</p>
          <router-link :to="`/tournament/${currentTournament.state.id}`" class="btn btn-outline">
            Tournament Dashboard
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter, onBeforeRouteEnter } from 'vue-router';
import { onMounted } from 'vue';
import currentTournament from '../store/current-tournament';

const router = useRouter();

// Navigate to tournament-specific routes
const navigateToTeams = () => {
  router.push(`/tournament/${currentTournament.state.id}/manage-teams`);
};

const navigateToSchedule = () => {
  router.push(`/tournament/${currentTournament.state.id}/manage-schedule`);
};

const navigateToScoring = () => {
  router.push(`/tournament/${currentTournament.state.id}/game-scoring`);
};

const navigateToSettings = () => {
  router.push(`/tournament/${currentTournament.state.id}/settings`);
};

onMounted(() => {
  // If no tournament is selected, redirect to tournaments page
  if (!currentTournament.hasSelectedTournament()) {
    router.push('/');
  }
  
  // Set page title to include tournament name
  document.title = `${currentTournament.state.name} Admin - Rocketpad`;
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

.btn-outline {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  text-decoration: none;
  text-align: center;
  transition: all var(--transition-fast);
}

.btn-outline:hover {
  background-color: rgba(67, 97, 238, 0.05);
  text-decoration: none;
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