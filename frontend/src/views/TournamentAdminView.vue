<template>
  <div class="tournament-admin-view">
    <header class="page-header">
      <h1>Tournament Management</h1>
      <div class="header-actions">
        <button class="btn create-btn" @click="navigateToCreate">
          <span class="btn-icon">+</span> Create Tournament
        </button>
        <button class="btn logout-btn" @click="logout">Logout</button>
      </div>
    </header>
    
    <div class="content-container">
      <section class="tournaments-section">
        <div class="section-header">
          <h2>Manage Tournaments</h2>
          <div class="badge" v-if="tournaments.length > 0">{{ tournaments.length }} Tournaments</div>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading tournaments...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button class="btn primary" @click="fetchTournaments">Retry</button>
        </div>
        
        <div v-else-if="tournaments.length === 0" class="empty-state">
          <p>No tournaments available. Create your first tournament to get started.</p>
          <button class="btn primary" @click="navigateToCreate">Create Tournament</button>
        </div>
        
        <div v-else class="tournaments-table-container">
          <table class="tournaments-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Dates</th>
                <th>Location</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tournament in tournaments" :key="tournament.id">
                <td>{{ tournament.name }}</td>
                <td>
                  <span class="status-pill" :class="tournament.status.toLowerCase()">
                    {{ tournament.status }}
                  </span>
                </td>
                <td>
                  {{ formatDateRange(tournament.start_date, tournament.end_date) }}
                </td>
                <td>{{ tournament.location || '-' }}</td>
                <td class="actions-cell">
                  <button class="btn action-btn view-btn" @click="navigateToTournament(tournament.id)" title="View Tournament">
                    <span class="btn-icon">👁️</span>
                  </button>
                  <button class="btn action-btn edit-btn" @click="navigateToEdit(tournament.id)" title="Edit Tournament">
                    <span class="btn-icon">✏️</span>
                  </button>
                  <button class="btn action-btn delete-btn" @click="confirmDelete(tournament)" title="Delete Tournament">
                    <span class="btn-icon">🗑️</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirm Deletion</h3>
        <p>Are you sure you want to delete the tournament "{{ tournamentToDelete.name }}"?</p>
        <p class="warning">This will permanently remove all associated data including teams, games, and brackets.</p>
        <div class="modal-actions">
          <button class="btn secondary" @click="cancelDelete">Cancel</button>
          <button class="btn danger" @click="deleteTournament" :disabled="deleting">
            {{ deleting ? 'Deleting...' : 'Delete Tournament' }}
          </button>
        </div>
      </div>
    </div>
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
const tournamentToDelete = ref({});
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
  if (!startDate && !endDate) return 'No dates set';
  
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };
  
  if (startDate && endDate) {
    return `${formatDate(startDate)} - ${formatDate(endDate)}`;
  } else if (startDate) {
    return `From ${formatDate(startDate)}`;
  } else {
    return `Until ${formatDate(endDate)}`;
  }
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
  tournamentToDelete.value = {};
};

const deleteTournament = async () => {
  deleting.value = true;
  
  try {
    await api.deleteTournament(tournamentToDelete.value.id);
    showDeleteModal.value = false;
    tournamentToDelete.value = {};
    
    // Refresh the tournaments list
    await fetchTournaments();
  } catch (err) {
    console.error('Error deleting tournament:', err);
    error.value = 'Failed to delete tournament. Please try again later.';
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
  document.title = 'Tournament Administration';
});
</script>

<style scoped>
.tournament-admin-view {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  margin: 0;
  color: var(--color-primary);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-text-primary);
}

.badge {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  text-align: center;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid var(--color-primary);
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.tournaments-table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tournaments-table {
  width: 100%;
  border-collapse: collapse;
}

.tournaments-table th,
.tournaments-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.tournaments-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.tournaments-table tr:last-child td {
  border-bottom: none;
}

.status-pill {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pill.active {
  background-color: #e6f7e6;
  color: #2e8b57;
}

.status-pill.completed {
  background-color: #e6e6e6;
  color: #666666;
}

.status-pill.upcoming {
  background-color: #e6f0ff;
  color: #3366cc;
}

.actions-cell {
  white-space: nowrap;
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.create-btn {
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.create-btn:hover {
  background-color: var(--color-primary-dark);
}

.logout-btn {
  background-color: #f0f0f0;
  color: #333;
}

.logout-btn:hover {
  background-color: #e0e0e0;
}

.action-btn {
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 1rem;
}

.view-btn {
  background-color: #f0f0f0;
  color: #333;
}

.edit-btn {
  background-color: #f0f0f0;
  color: #333;
}

.delete-btn {
  background-color: #ffebee;
  color: #d32f2f;
}

.view-btn:hover, .edit-btn:hover {
  background-color: #e0e0e0;
}

.delete-btn:hover {
  background-color: #ffcdd2;
}

.btn-icon {
  display: inline-block;
  font-size: 1rem;
}

.primary {
  background-color: var(--color-primary);
  color: white;
}

.primary:hover {
  background-color: var(--color-primary-dark);
}

.secondary {
  background-color: #f0f0f0;
  color: #333;
}

.secondary:hover {
  background-color: #e0e0e0;
}

.danger {
  background-color: #f44336;
  color: white;
}

.danger:hover:not(:disabled) {
  background-color: #d32f2f;
}

.danger:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin-top: 0;
  color: var(--color-text-primary);
}

.warning {
  color: #f44336;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .create-btn {
    flex: 1;
  }
  
  .tournaments-table {
    display: block;
    overflow-x: auto;
  }
  
  .modal-content {
    width: 95%;
    padding: 1.5rem;
  }
}
</style> 