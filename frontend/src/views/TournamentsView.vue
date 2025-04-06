<template>
  <div class="tournaments-view">
    <header class="page-header">
      <div class="header-content">
        <h1>Available Divisions</h1>
        <p class="subtitle">Select a division to view its dashboard</p>
      </div>
      <!-- Optional: Add actions like Create Tournament if needed -->
      <!-- <div class="header-actions"> -->
      <!--   <button class="btn btn-primary">Create Tournament</button> -->
      <!-- </div> -->
    </header>

    <!-- Search and filters section -->
    <div class="filters-container card">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search tournaments..." 
          class="search-input"
          @input="applyFilters"
        />
        <span class="search-icon">🔍</span>
      </div>
      
      <div class="status-filters">
        <span class="filter-label">Filter by status:</span>
        <div class="filter-buttons">
          <button 
            @click="toggleStatusFilter('all')" 
            :class="['filter-btn', { active: selectedStatuses.includes('all') }]"
          >
            All
          </button>
          <button 
            @click="toggleStatusFilter('upcoming')" 
            :class="['filter-btn', { active: selectedStatuses.includes('upcoming') }]"
          >
            Upcoming
          </button>
          <button 
            @click="toggleStatusFilter('active')" 
            :class="['filter-btn', { active: selectedStatuses.includes('active') }]"
          >
            Active
          </button>
          <button 
            @click="toggleStatusFilter('completed')" 
            :class="['filter-btn', { active: selectedStatuses.includes('completed') }]"
          >
            Completed
          </button>
          <button 
            @click="toggleStatusFilter('cancelled')" 
            :class="['filter-btn', { active: selectedStatuses.includes('cancelled') }]"
          >
            Cancelled
          </button>
        </div>
      </div>
    </div>

    <div class="content-container">
      <!-- Apply .card styling directly -->
      <section class="card tournaments-section">
        <div class="section-header">
          <h2>Division List</h2>
          <div class="badge" v-if="filteredTournaments.length > 0">{{ filteredTournaments.length }} Found</div>
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
        
        <div v-else-if="filteredTournaments.length === 0" class="empty-state">
          <p>No tournaments match your search criteria.</p>
          <button class="btn btn-sm btn-outline" @click="resetFilters">Reset Filters</button>
        </div>

        <div v-else class="tournaments-container">
          <!-- List view instead of grid -->
          <div class="tournaments-list">
            <div 
              v-for="tournament in filteredTournaments" 
              :key="tournament.id" 
              class="tournament-list-item" 
              @click="navigateToTournament(tournament.id)"
            >
              <div class="tournament-list-main">
                <div class="tournament-name-and-status">
                  <h3>{{ tournament.name }}</h3>
                  <span class="status-pill" :class="getStatusClass(tournament.status)">{{ tournament.status }}</span>
                </div>
                <p class="tournament-description">{{ tournament.description || 'No description provided.' }}</p>
              </div>
              
              <div class="tournament-list-metadata">
                <div v-if="tournament.location" class="metadata-item">
                  <span class="icon location">📍</span>
                  <span>{{ tournament.location }}</span>
                </div>
                <div v-if="tournament.start_date" class="metadata-item">
                  <span class="icon calendar">📅</span>
                  <span>{{ formatDateRange(tournament.start_date, tournament.end_date) }}</span>
                </div>
              </div>
              
              <div class="tournament-list-actions">
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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
// import auth from '../store/auth'; // Removed if isAdmin is not used
import currentTournament from '../store/current-tournament';

const router = useRouter();

// Tournaments data
const tournaments = ref([]);
const loading = ref(true);
const error = ref(null);

// Search and filter state
const searchQuery = ref('');
const selectedStatuses = ref(['all']); // Default to 'all'

// Filtered tournaments based on search query and selected statuses
const filteredTournaments = computed(() => {
  if (selectedStatuses.value.includes('all') && !searchQuery.value.trim()) {
    return tournaments.value;
  }
  
  return tournaments.value.filter(tournament => {
    // Status filtering
    const statusMatch = selectedStatuses.value.includes('all') || 
      selectedStatuses.value.includes(tournament.status?.toLowerCase().replace(' ', '-'));
    
    // Text search
    const searchTerms = searchQuery.value.toLowerCase().trim();
    const textMatch = !searchTerms || 
      tournament.name?.toLowerCase().includes(searchTerms) || 
      tournament.description?.toLowerCase().includes(searchTerms) || 
      tournament.location?.toLowerCase().includes(searchTerms);
    
    return statusMatch && textMatch;
  });
});

// Filter functions
const toggleStatusFilter = (status) => {
  if (status === 'all') {
    // If 'all' is clicked, reset to only 'all'
    selectedStatuses.value = ['all'];
  } else {
    // Remove 'all' if it's present
    if (selectedStatuses.value.includes('all')) {
      selectedStatuses.value = selectedStatuses.value.filter(s => s !== 'all');
    }
    
    // Toggle the selected status
    if (selectedStatuses.value.includes(status)) {
      // If it's the last filter, revert to 'all'
      if (selectedStatuses.value.length === 1) {
        selectedStatuses.value = ['all'];
      } else {
        // Otherwise remove the status
        selectedStatuses.value = selectedStatuses.value.filter(s => s !== status);
      }
    } else {
      // Add the status
      selectedStatuses.value.push(status);
    }
  }
};

const applyFilters = () => {
  // This function can be expanded if we need more complex filter logic
  // Currently filtering is handled by the computed property
};

const resetFilters = () => {
  searchQuery.value = '';
  selectedStatuses.value = ['all'];
};

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
  margin-bottom: var(--space-md);
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

/* Search and filters styling */
.filters-container {
  margin-bottom: var(--space-lg);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.search-box {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  padding-left: calc(var(--space-md) * 2 + 18px); /* Space for the icon */
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  background-color: var(--color-background-alt);
  color: var(--color-text);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(90, 103, 216, 0.1);
}

.search-icon {
  position: absolute;
  left: var(--space-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-light);
  font-size: 1rem;
  pointer-events: none;
}

.status-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  align-items: center;
}

.filter-label {
  color: var(--color-text-light);
  font-weight: 500;
  font-size: 0.9rem;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.filter-btn {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-border);
  background-color: var(--color-background-alt);
  color: var(--color-text-light);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn:hover {
  background-color: var(--color-background);
  border-color: var(--color-primary-light);
}

.filter-btn.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
}

/* List view styles */
.tournaments-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.tournament-list-item {
  display: flex;
  flex-wrap: wrap;
  padding: var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-background-card);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
}

.tournament-list-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.tournament-list-main {
  flex: 1 1 50%;
  min-width: 300px;
  padding-right: var(--space-md);
}

.tournament-name-and-status {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
  flex-wrap: wrap;
}

.tournament-name-and-status h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-accent);
}

.tournament-list-metadata {
  flex: 1 1 25%;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-left: 1px solid var(--color-border);
  border-right: 1px solid var(--color-border);
}

.tournament-list-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--space-md);
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

.tournament-description {
  color: var(--color-text-light);
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
  /* Limit to 2 lines */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
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

.view-btn {
  /* Uses .btn, .btn-sm, .btn-primary from global styles */
  white-space: nowrap;
}

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
  
  .tournament-list-item {
    flex-direction: column;
  }
  
  .tournament-list-main {
    width: 100%;
    padding-right: 0;
    margin-bottom: var(--space-md);
  }
  
  .tournament-list-metadata {
    width: 100%;
    border-left: none;
    border-right: none;
    border-top: 1px solid var(--color-border);
    border-bottom: 1px solid var(--color-border);
    padding: var(--space-md) 0;
    margin-bottom: var(--space-md);
  }
  
  .tournament-list-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .status-filters {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-buttons {
    width: 100%;
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
    .tournament-name-and-status h3 {
        font-size: 1.05rem;
    }
    .filter-buttons {
        gap: var(--space-xs);
    }
    .filter-btn {
        font-size: 0.8rem;
        padding: var(--space-xxs) var(--space-xs);
    }
}
</style> 