<template>
  <div class="tournaments-view">
    <header class="page-header">
      <div class="header-content">
        <h1>Baseball Tournaments</h1>
        <p class="subtitle">Select a tournament to view details</p>
      </div>
    </header>
    
    <div class="content-container">
      <section class="tournaments-section">
        <div class="section-header">
          <h2>Available Tournaments</h2>
          <div class="badge" v-if="tournaments.length > 0">{{ tournaments.length }} Tournaments</div>
        </div>
        
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading tournaments...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
        </div>
        
        <div v-else-if="tournaments.length === 0" class="empty-state">
          <p>No tournaments available.</p>
        </div>
        
        <div v-else class="tournaments-container">
          <div class="tournaments-grid">
            <div v-for="tournament in tournaments" :key="tournament.id" class="tournament-card" @click="navigateToTournament(tournament.id)">
              <div class="tournament-header">
                <h3>{{ tournament.name }}</h3>
                <span class="status-pill" :class="tournament.status.toLowerCase()">{{ tournament.status }}</span>
              </div>
              <div class="tournament-details">
                <p class="tournament-description">{{ tournament.description || 'No description available' }}</p>
                <div class="tournament-metadata">
                  <div v-if="tournament.location" class="metadata-item">
                    <i class="icon location"></i>
                    <span>{{ tournament.location }}</span>
                  </div>
                  <div v-if="tournament.start_date" class="metadata-item">
                    <i class="icon calendar"></i>
                    <span>{{ formatDate(tournament.start_date) }} {{ tournament.end_date ? `- ${formatDate(tournament.end_date)}` : '' }}</span>
                  </div>
                </div>
              </div>
              <div class="tournament-footer">
                <button class="btn view-btn">View Tournament</button>
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
import auth from '../store/auth';
import currentTournament from '../store/current-tournament';

const router = useRouter();

// Tournaments data
const tournaments = ref([]);
const loading = ref(true);
const error = ref(null);

// Computed property to check if user is admin
const isAdmin = computed(() => auth.state.isAuthenticated);

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

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'TBD';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  });
};

// Navigation functions
const navigateToTournament = (tournamentId) => {
  // Find the tournament by ID to get its data
  const tournament = tournaments.value.find(t => t.id === tournamentId);
  if (tournament) {
    // Set the current tournament in store
    currentTournament.setTournament({
      id: tournament.id,
      name: tournament.name
    });
  }
  
  router.push({ name: 'TournamentHome', params: { id: tournamentId } });
};

const navigateToEdit = (tournamentId) => {
  router.push({ name: 'ManageTournament', params: { id: tournamentId } });
};

const navigateToCreate = () => {
  router.push({ name: 'CreateTournament' });
};

// Add the function back to navigate to tournament admin login
const navigateToTournamentAdmin = () => {
  router.push({ name: 'TournamentAdminLogin' });
};

onMounted(() => {
  fetchTournaments();
  document.title = 'Tournaments - Baseball Tournament App';
});
</script>

<style scoped>
.tournaments-view {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  text-align: left;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-primary);
}

.subtitle {
  font-size: 1.2rem;
  color: var(--color-text-secondary);
  margin-bottom: 0;
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

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
}

.empty-state-actions {
  margin-top: 1rem;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.tournament-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.tournament-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.tournament-header {
  padding: 1.25rem;
  background-color: var(--color-primary-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tournament-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-primary);
}

.status-pill {
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

.tournament-details {
  padding: 1.25rem;
  flex-grow: 1;
}

.tournament-description {
  color: var(--color-text-primary);
  margin-top: 0;
  margin-bottom: 1rem;
  line-height: 1.5;
  /* Limit to 3 lines */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tournament-metadata {
  margin-top: 1rem;
}

.metadata-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  color: var(--color-text-secondary);
}

.metadata-item .icon {
  margin-right: 0.5rem;
  width: 16px;
  height: 16px;
  /* You can add actual icons later */
  display: inline-block;
  background-color: var(--color-text-secondary);
  opacity: 0.6;
  border-radius: 50%;
}

.tournament-footer {
  padding: 1rem;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
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

.view-btn {
  background-color: var(--color-primary);
  color: white;
}

.view-btn:hover {
  background-color: var(--color-primary-dark);
}

.edit-btn {
  background-color: #f0f0f0;
  color: #333;
}

.edit-btn:hover {
  background-color: #e0e0e0;
}

.admin-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
}

.create-tournament-btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.primary {
  background-color: var(--color-primary);
  color: white;
}

.primary:hover {
  background-color: var(--color-primary-dark);
}

.admin-btn {
  background-color: #f0f0f0;
  color: #555;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.admin-btn:hover {
  background-color: #e0e0e0;
}

.header-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    text-align: center;
  }
  
  .header-content {
    text-align: center;
    margin-bottom: 1rem;
  }
  
  .tournaments-grid {
    grid-template-columns: 1fr;
  }
  
  .tournament-card {
    max-width: 100%;
  }
}
</style> 