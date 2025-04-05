<template>
  <div class="tournaments-view">
    <header class="page-header">
      <div class="header-content">
        <h1>Available Tournaments</h1>
        <p class="subtitle">Select a tournament to view its dashboard</p>
      </div>
      <!-- Optional: Add actions like Create Tournament if needed -->
      <!-- <div class="header-actions"> -->
      <!--   <button class="btn btn-primary">Create Tournament</button> -->
      <!-- </div> -->
    </header>

    <div class="content-container">
      <!-- Apply .card styling directly -->
      <section class="card tournaments-section">
        <div class="section-header">
          <h2>Tournament List</h2>
          <div class="badge" v-if="tournaments.length > 0">{{ tournaments.length }} Found</div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading tournaments...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
        </div>

        <div v-else-if="tournaments.length === 0" class="empty-state">
          <p>No tournaments available at this time.</p>
          <!-- Optional: Add create button here if applicable -->
        </div>

        <div v-else class="tournaments-container">
          <div class="tournaments-grid">
            <!-- Use a more descriptive class name -->
            <div v-for="tournament in tournaments" :key="tournament.id" class="tournament-card-item" @click="navigateToTournament(tournament.id)">
              <div class="tournament-header">
                <h3>{{ tournament.name }}</h3>
                <span class="status-pill" :class="getStatusClass(tournament.status)">{{ tournament.status }}</span>
              </div>
              <div class="tournament-details">
                <p class="tournament-description">{{ tournament.description || 'No description provided.' }}</p>
                <div class="tournament-metadata">
                  <div v-if="tournament.location" class="metadata-item">
                    <span class="icon location">📍</span> <!-- Simple icon -->
                    <span>{{ tournament.location }}</span>
                  </div>
                  <div v-if="tournament.start_date" class="metadata-item">
                    <span class="icon calendar">📅</span> <!-- Simple icon -->
                    <span>{{ formatDateRange(tournament.start_date, tournament.end_date) }}</span>
                  </div>
                </div>
              </div>
              <div class="tournament-footer">
                <button class="btn btn-sm btn-primary view-btn">View Details</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
// import auth from '../store/auth'; // Removed if isAdmin is not used
import currentTournament from '../store/current-tournament';

const router = useRouter();

// Tournaments data
const tournaments = ref([]);
const loading = ref(true);
const error = ref(null);

// Removed isAdmin computed property as it wasn't used in the template
// const isAdmin = computed(() => auth.state.isAuthenticated);

// Fetch tournaments
const fetchTournaments = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await api.getTournaments();
    tournaments.value = response.data;
  } catch (err) {
    console.error('Error loading tournaments:', err);
    error.value = 'Failed to load tournaments. Please try again later.';
  } finally {
    loading.value = false;
  }
};

// Format date for display (Month Day, Year)
const formatDate = (dateString) => {
  if (!dateString) return 'TBD';
  const date = new Date(dateString);
  // Adjust for potential timezone issues by parsing as UTC
  const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
  return utcDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    // year: 'numeric' // Optionally add year if needed
  });
};

// Format date range
const formatDateRange = (startDateString, endDateString) => {
  const start = formatDate(startDateString);
  const end = formatDate(endDateString);
  if (start === 'TBD') return 'Dates TBD';
  if (end === 'TBD' || start === end) return start;
  return `${start} - ${end}`;
}

// Get CSS class for status pill
const getStatusClass = (status) => {
    if (!status) return 'unknown';
    return status.toLowerCase().replace(' ', '-'); // e.g., 'In Progress' -> 'in-progress'
};

// Navigation function
const navigateToTournament = (tournamentId) => {
  const tournament = tournaments.value.find(t => t.id === tournamentId);
  if (tournament) {
    currentTournament.setTournament({
      id: tournament.id,
      name: tournament.name
    });
  }
  router.push({ name: 'TournamentHome', params: { id: tournamentId } });
};

// Removed unused navigation functions
// const navigateToEdit = (tournamentId) => { ... };
// const navigateToCreate = () => { ... };
// const navigateToTournamentAdmin = () => { ... };

onMounted(() => {
  fetchTournaments();
  document.title = 'Tournaments - Rocketpad'; // Update title
});
</script>

<style scoped>
.tournaments-view {
  /* Uses container padding defined in main layout */
  width: 100%;
}

.page-header {
  /* Similar to HomeView header */
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  text-align: left;
}

.page-header h1 {
  /* Use global h1 styles */
  margin-bottom: var(--space-xs);
}

.subtitle {
  /* Use global styles if defined, or refine here */
  font-size: 1.1rem;
  color: var(--color-text-light);
  margin-top: 0;
}

.content-container {
  /* Uses container width/margins from parent */
}

.tournaments-section {
  /* Inherits .card styles from template */
  /* Add specific overrides if needed */
}

.section-header {
  /* Shared style with HomeView */
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
  gap: var(--space-sm);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.section-header h2 {
  /* Use global h2/h3 styles */
  margin: 0;
  color: var(--color-text);
  font-size: 1.5rem; /* Adjust if needed */
}

.badge {
  /* Shared style with HomeView */
  background-color: var(--color-primary-light);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

/* Consistent loading/error/empty states */
.loading-state, .error-state, .empty-state {
  padding: var(--space-xl) var(--space-lg);
  text-align: center;
  background-color: var(--color-background-alt);
  border-radius: var(--radius-md);
  margin-top: var(--space-md);
  color: var(--color-text-light);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.loading-spinner {
  /* Shared style with HomeView */
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

.empty-state {
  font-style: normal;
}

.tournaments-grid {
  display: grid;
  /* Responsive columns */
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr));
  gap: var(--space-lg);
}

.tournament-card-item {
  background-color: var(--color-background-card); /* White background */
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
}

.tournament-card-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.tournament-header {
  padding: var(--space-md);
  background-color: var(--color-background-alt); /* Subtle header background */
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.tournament-header h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-accent);
  /* Truncate long names */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-pill {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
  border: 1px solid transparent;
}

/* Status Colors (Example) */
.status-pill.upcoming {
  background-color: rgba(96, 165, 250, 0.1); /* info color */
  color: #1d4ed8; /* darker info */
  border-color: rgba(96, 165, 250, 0.3);
}

.status-pill.active,
.status-pill.in-progress {
  background-color: rgba(52, 211, 153, 0.1); /* success color */
  color: #047857; /* darker success */
  border-color: rgba(52, 211, 153, 0.3);
}

.status-pill.completed {
  background-color: rgba(107, 114, 128, 0.1); /* neutral color */
  color: #374151; /* darker neutral */
  border-color: rgba(107, 114, 128, 0.3);
}

.status-pill.cancelled {
  background-color: rgba(244, 63, 94, 0.1); /* danger color */
  color: #be123c; /* darker danger */
  border-color: rgba(244, 63, 94, 0.3);
}

.status-pill.unknown {
    background-color: var(--color-background-alt);
    color: var(--color-text-lighter);
    border-color: var(--color-border);
}

.tournament-details {
  padding: var(--space-md);
  flex-grow: 1; /* Allows details to fill space */
  display: flex;
  flex-direction: column;
  gap: var(--space-md); /* Space between desc and metadata */
}

.tournament-description {
  color: var(--color-text-light);
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
  /* Limit to 3 lines */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.6 * 0.9rem * 3); /* Reserve space for 3 lines */
}

.tournament-metadata {
  margin: 0; /* Reset margin */
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--color-text-light);
  font-size: 0.85rem;
}

.metadata-item .icon {
  /* Basic icon styling */
  font-size: 1rem;
  line-height: 1;
}

.tournament-footer {
  padding: var(--space-sm) var(--space-md); /* Reduced padding */
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end; /* Align button right */
  background-color: var(--color-background-alt); /* Subtle footer background */
}

.view-btn {
  /* Uses .btn, .btn-sm, .btn-primary from global styles */
}

/* Remove redundant/unused styles */
/* .edit-btn, .admin-actions, .create-tournament-btn, .primary, .admin-btn, .header-actions */


@media (max-width: 768px) {
  .page-header {
    /* Keep flex layout, but allow wrap maybe? */
    flex-wrap: wrap;
    text-align: left;
  }

  .header-content {
    /* Take full width if actions wrap */
    width: 100%;
    text-align: left;
    margin-bottom: var(--space-md); /* Add space if actions wrap */
  }
}

@media (max-width: 480px) {
    .page-header h1 {
        font-size: 1.8rem;
    }
    .subtitle {
        font-size: 1rem;
    }
    .section-header h2 {
        font-size: 1.3rem;
    }
    .tournament-header h3 {
        font-size: 1.05rem;
    }
}
</style> 