<template>
  <div class="tournament-admin-view">
    <header class="page-header">
      <h1>Tournament Administration</h1>
      <div class="header-actions">
        <button class="btn btn-primary create-btn" @click="navigateToCreate">
          <span class="btn-icon">➕</span> Create Tournament
        </button>
        <button class="btn btn-outline logout-btn" @click="logout">Logout</button>
      </div>
    </header>
    
    <div class="content-container">
      <section class="card tournaments-section">
        <div class="section-header">
          <h2>Manage Tournaments</h2>
          <div class="badge" v-if="tournaments.length > 0">{{ tournaments.length }} Found</div>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading tournaments...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="fetchTournaments">Retry</button>
        </div>
        
        <div v-else-if="tournaments.length === 0" class="empty-state">
          <p>No tournaments created yet. Get started by creating one!</p>
          <button class="btn btn-primary" @click="navigateToCreate">
            <span class="btn-icon">➕</span> Create First Tournament
          </button>
        </div>
        
        <div v-else class="table-wrapper tournaments-table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Dates</th>
                <th>Location</th>
                <th class="actions-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tournament in tournaments" :key="tournament.id">
                <td class="tournament-name-cell">{{ tournament.name }}</td>
                <td>
                  <span class="status-pill" :class="getStatusClass(tournament.status)">
                    {{ tournament.status }}
                  </span>
                </td>
                <td class="date-cell">
                  {{ formatDateRange(tournament.start_date, tournament.end_date) }}
                </td>
                <td>{{ tournament.location || '-' }}</td>
                <td class="actions-cell">
                  <button class="btn btn-sm btn-outline action-btn view-btn" @click="navigateToTournament(tournament.id)" title="View Details">
                    <span class="btn-icon">👁️</span> <span class="sr-only">View</span>
                  </button>
                  <button class="btn btn-sm btn-outline action-btn edit-btn" @click="navigateToEdit(tournament.id)" title="Edit Settings">
                    <span class="btn-icon">✏️</span> <span class="sr-only">Edit</span>
                  </button>
                  <button class="btn btn-sm btn-danger-outline action-btn delete-btn" @click="confirmDelete(tournament)" title="Delete Tournament">
                    <span class="btn-icon">🗑️</span> <span class="sr-only">Delete</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <transition name="fade">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
        <div class="modal-content card">
          <div class="modal-header">
            <h3>Confirm Deletion</h3>
            <button class="modal-close-btn" @click="cancelDelete" aria-label="Close modal">&times;</button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to permanently delete the tournament:</p>
            <p class="tournament-name-emphasis">"{{ tournamentToDelete?.name }}"?</p>
            <p class="warning-text">
              <span class="warning-icon">⚠️</span>
              This action cannot be undone. All associated data (teams, games, schedule, bracket, results) will be permanently removed.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button class="btn btn-danger" @click="deleteTournament" :disabled="deleting">
              <span v-if="deleting" class="spinner"></span>
              {{ deleting ? 'Deleting...' : 'Confirm Delete' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';
import tournamentAdminAuth from '../store/tournament-admin-auth';

const router = useRouter();

// Tournaments data
const tournaments = ref([]);
const loading = ref(true);
const error = ref(null);

// Delete modal state
const showDeleteModal = ref(false);
const tournamentToDelete = ref(null);
const deleting = ref(false);

// Fetch all tournaments
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

// Format date range for display
const formatDateRange = (startDate, endDate) => {
  if (!startDate && !endDate) return '-';
  
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const utcDate = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
    return utcDate.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };
  
  const startFormatted = formatDate(startDate);
  const endFormatted = formatDate(endDate);
  
  if (startFormatted && endFormatted) {
    return `${startFormatted} - ${endFormatted}`;
  } else if (startFormatted) {
    return `Starts ${startFormatted}`;
  } else if (endFormatted) {
    return `Ends ${endFormatted}`;
  }
  return '-';
};

// Get CSS class for status pill
const getStatusClass = (status) => {
  if (!status) return 'unknown';
  return status.toLowerCase().replace(' ', '-');
};

// Navigation functions
const navigateToCreate = () => {
  router.push({ name: 'CreateTournament' });
};

const navigateToEdit = (tournamentId) => {
  router.push({ name: 'ManageTournament', params: { id: tournamentId } });
};

const navigateToTournament = (tournamentId) => {
  router.push({ name: 'TournamentHome', params: { id: tournamentId } });
};

// Delete functions
const confirmDelete = (tournament) => {
  tournamentToDelete.value = tournament;
  showDeleteModal.value = true;
};

const cancelDelete = () => {
  showDeleteModal.value = false;
  setTimeout(() => {
    tournamentToDelete.value = null;
  }, 300);
};

const deleteTournament = async () => {
  if (!tournamentToDelete.value) return;
  deleting.value = true;
  
  try {
    await api.deleteTournament(tournamentToDelete.value.id);
    showDeleteModal.value = false;
    
    tournaments.value = tournaments.value.filter(t => t.id !== tournamentToDelete.value.id);
    tournamentToDelete.value = null;
    
  } catch (err) {
    console.error('Error deleting tournament:', err);
    error.value = 'Failed to delete tournament. Please try again later.';
    showDeleteModal.value = false;
    tournamentToDelete.value = null;
  } finally {
    deleting.value = false;
  }
};

// Logout function
const logout = () => {
  tournamentAdminAuth.logout();
  router.push('/tournament-admin-login');
};

onMounted(() => {
  fetchTournaments();
  document.title = 'Tournament Admin - Rocketpad';
});
</script>

<style scoped>
.tournament-admin-view {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border);
}

.page-header h1 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-md);
}

.create-btn .btn-icon,
.empty-state .btn .btn-icon {
  margin-right: var(--space-xs);
}

.logout-btn {
}

.content-container {
}

.tournaments-section {
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
  gap: var(--space-sm);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.section-header h2 {
  margin: 0;
  color: var(--color-text);
  font-size: 1.5rem;
}

.badge {
  background-color: var(--color-primary-light);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

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

.empty-state p {
  margin-bottom: var(--space-md);
}

.tournaments-table-container {
}

table {
}

th {
  white-space: nowrap;
}

.actions-header {
  text-align: right;
}

td {
  vertical-align: middle;
}

.tournament-name-cell {
  font-weight: 600;
  color: var(--color-text);
}

.date-cell {
  white-space: nowrap;
  font-size: 0.9rem;
  color: var(--color-text-light);
}

.status-pill {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
  border: 1px solid transparent;
  line-height: 1.5;
}

.status-pill.upcoming {
  background-color: rgba(96, 165, 250, 0.1);
  color: #1d4ed8;
  border-color: rgba(96, 165, 250, 0.3);
}
.status-pill.active,
.status-pill.in-progress {
  background-color: rgba(52, 211, 153, 0.1);
  color: #047857;
  border-color: rgba(52, 211, 153, 0.3);
}
.status-pill.completed {
  background-color: rgba(107, 114, 128, 0.1);
  color: #374151;
  border-color: rgba(107, 114, 128, 0.3);
}
.status-pill.cancelled {
  background-color: rgba(244, 63, 94, 0.1);
  color: #be123c;
  border-color: rgba(244, 63, 94, 0.3);
}
.status-pill.unknown {
  background-color: var(--color-background-alt);
  color: var(--color-text-lighter);
  border-color: var(--color-border);
}

.actions-cell {
  white-space: nowrap;
  display: flex;
  justify-content: flex-end;
  gap: var(--space-xs);
}

.action-btn {
  padding: 0.4rem;
  line-height: 1;
}

.action-btn .btn-icon {
  font-size: 1rem;
  vertical-align: middle;
}

.btn-danger-outline {
  background-color: transparent;
  border: 1px solid var(--color-danger);
  color: var(--color-danger);
}
.btn-danger-outline:hover {
  background-color: rgba(244, 63, 94, 0.1);
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
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
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-md);
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .create-btn {
    flex-grow: 1;
  }
  
  .modal-content {
    max-width: 95%;
  }
}
</style> 