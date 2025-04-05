<template>
  <div class="admin-view">
    <header class="admin-header page-header">
      <h1>{{ currentTournament.state.name || 'Tournament' }} Admin</h1>
      <p class="subtitle">Manage tournament settings, teams, schedule, and results.</p>
    </header>

    <div class="admin-content">
      <!-- Section for main admin functions -->
      <section class="card admin-nav-section">
        <h2>Administrative Functions</h2>
        <div class="admin-nav-links">
          <router-link :to="`/tournament/${currentTournament.state.id}/settings`" class="admin-nav-link">
            <div class="icon-container settings-icon">⚙️</div>
            <div class="link-content">
              <h3>Tournament Settings</h3>
              <p>Configure name, dates, password, etc.</p>
            </div>
          </router-link>

          <router-link :to="`/tournament/${currentTournament.state.id}/manage-teams`" class="admin-nav-link">
            <div class="icon-container teams-icon">👥</div>
            <div class="link-content">
              <h3>Team Management</h3>
              <p>Add, edit, and manage participating teams.</p>
            </div>
          </router-link>

          <router-link :to="`/tournament/${currentTournament.state.id}/manage-schedule`" class="admin-nav-link">
            <div class="icon-container schedule-icon">📅</div>
            <div class="link-content">
              <h3>Schedule Management</h3>
              <p>Create and modify the game schedule.</p>
            </div>
          </router-link>

          <router-link :to="`/tournament/${currentTournament.state.id}/game-scoring`" class="admin-nav-link">
            <div class="icon-container scoring-icon">🏆</div>
            <div class="link-content">
              <h3>Game Scoring</h3>
              <p>Input and update game results.</p>
            </div>
          </router-link>

          <router-link :to="`/tournament/${currentTournament.state.id}/bracket`" class="admin-nav-link">
            <div class="icon-container bracket-icon">📊</div>
            <div class="link-content">
              <h3>Bracket Management</h3>
              <p>Generate and manage tournament bracket.</p>
            </div>
          </router-link>
        </div>
      </section>

      <!-- Section for quick actions and public view link -->
      <section class="quick-actions-section">
        <div class="card quick-actions-card">
          <h2>Quick Actions</h2>
          <div class="action-buttons">
            <button class="btn btn-secondary" @click="navigateToTeams">
              <span class="btn-icon">👥</span> Add/Edit Teams
            </button>
            <button class="btn btn-secondary" @click="navigateToSchedule">
              <span class="btn-icon">📅</span> Create/Edit Schedule
            </button>
            <button class="btn btn-secondary" @click="navigateToScoring">
              <span class="btn-icon">🏆</span> Enter Game Scores
            </button>
          </div>
        </div>

        <div class="card return-link-card">
          <h2>Public View</h2>
          <p>View the public-facing tournament dashboard.</p>
          <router-link :to="`/tournament/${currentTournament.state.id}`" class="btn btn-outline">
             <span class="btn-icon">➡️</span> Go to Tournament Dashboard
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter, onBeforeRouteEnter } from 'vue-router';
import { onMounted, computed } from 'vue';
import currentTournament from '../store/current-tournament';

const router = useRouter();

// Computed property for tournament ID for cleaner routes
const tournamentId = computed(() => currentTournament.state.id);

// Navigate to tournament-specific routes
const navigateToTeams = () => {
  if (tournamentId.value) router.push(`/tournament/${tournamentId.value}/manage-teams`);
};

const navigateToSchedule = () => {
  if (tournamentId.value) router.push(`/tournament/${tournamentId.value}/manage-schedule`);
};

const navigateToScoring = () => {
  if (tournamentId.value) router.push(`/tournament/${tournamentId.value}/game-scoring`);
};

onMounted(() => {
  // If no tournament is selected, redirect to the main tournaments list
  if (!currentTournament.hasSelectedTournament()) {
    router.push({ name: 'Tournaments' });
    return;
  }

  // Set page title
  document.title = `${currentTournament.state.name || 'Tournament'} Admin - Rocketpad`;
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
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
  gap: var(--space-xl);
}

.admin-nav-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.quick-actions-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
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
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--space-lg);
}

.admin-nav-link {
  display: flex;
  gap: var(--space-md);
  align-items: center;
  padding: var(--space-md);
  background-color: var(--color-background-alt);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-fast);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.admin-nav-link:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: var(--color-primary);
  background-color: var(--color-background-card);
  text-decoration: none;
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  font-size: 1.5rem;
  color: white;
}

.settings-icon { background-color: var(--color-info); }
.teams-icon { background-color: var(--color-success); }
.schedule-icon { background-color: var(--color-warning); }
.scoring-icon { background-color: var(--color-secondary); }
.bracket-icon { background-color: var(--color-primary); }

.link-content {
  flex-grow: 1;
  overflow: hidden;
}

.link-content h3 {
  margin: 0 0 2px 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-accent);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.link-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-light);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quick-actions-card .action-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.quick-actions-card .btn,
.return-link-card .btn {
  width: 100%;
  justify-content: center;
}

.quick-actions-card .btn .btn-icon,
.return-link-card .btn .btn-icon {
  margin-right: var(--space-xs);
}

.return-link-card p {
  color: var(--color-text-light);
  margin-bottom: var(--space-md);
  font-size: 0.9rem;
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-secondary:hover {
  background-color: var(--color-secondary-dark);
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
  }
}

@media (max-width: 768px) {
  .admin-header h1 {
    font-size: 1.8rem;
  }
  
  .admin-nav-links {
    grid-template-columns: 1fr;
  }
  
  .admin-nav-card, .admin-action-card {
    padding: var(--space-md);
  }
}

@media (max-width: 480px) {
  .admin-header h1 {
    font-size: 1.6rem;
  }
  .subtitle {
    font-size: 0.9rem;
  }
  .admin-nav-section h2,
  .quick-actions-card h2,
  .return-link-card h2 {
    font-size: 1.2rem;
  }
}
</style> 