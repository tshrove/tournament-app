<template>
  <div class="modal-backdrop" v-if="show" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Select Team</h3>
        <button class="close-button" @click="closeModal">&times;</button>
      </div>
      
      <!-- Debug info -->
      <div v-if="debug" class="debug-info">
        <div>Tournament ID: {{ tournamentId || 'None' }}</div>
        <div>Player position: {{ playerPosition || 'None' }}</div>
        <div>Teams loaded: {{ teams.length }}</div>
      </div>
      
      <div class="modal-body">
        <div v-if="loading" class="loading-indicator">
          Loading teams...
        </div>
        <div v-else-if="error" class="error-message">
          {{ error }}
        </div>
        <div v-else-if="teams.length === 0" class="no-teams">
          No teams available for this tournament.
        </div>
        <div v-else class="team-list">
          <div 
            v-for="team in teams" 
            :key="team.id" 
            class="team-item"
            @click="selectTeam(team)"
            :class="{ 'selected': selectedTeamId === team.id }"
          >
            {{ team.name }}
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button 
          class="btn btn-secondary" 
          @click="closeModal"
        >
          Cancel
        </button>
        <button 
          class="btn btn-primary" 
          @click="confirmSelection"
          :disabled="!selectedTeamId"
        >
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import api from '../services/api';

export default {
  name: 'TeamSelectionModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    tournamentId: {
      type: [String, Number],
      default: null
    },
    playerPosition: {
      type: String,
      default: null
    },
    matchData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close', 'team-selected'],
  setup(props, { emit }) {
    const teams = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const selectedTeamId = ref(null);
    const debug = ref(true); // Enable debugging output

    const fetchTeams = async () => {
      loading.value = true;
      error.value = null;
      
      if (!props.tournamentId) {
        console.log("No tournament ID provided to team selection modal - loading all teams");
        try {
          // If no tournament ID is provided, try to load all teams
          const response = await api.getTeams();
          console.log("All teams response:", response);
          
          if (response && response.data) {
            teams.value = response.data;
            console.log(`Loaded ${teams.value.length} teams (all tournaments)`);
          } else {
            error.value = "No teams data received from the server";
          }
        } catch (err) {
          console.error('Error fetching all teams:', err);
          error.value = err.response?.data?.error || 'Failed to load teams. Please try again.';
        } finally {
          loading.value = false;
        }
        return;
      }
      
      console.log("Fetching teams for tournament ID:", props.tournamentId);
      
      try {
        const params = { tournament_id: props.tournamentId };
        const response = await api.getTeams(params);
        console.log("Teams API response:", response);
        
        if (response && response.data) {
          teams.value = response.data;
          console.log("Loaded teams:", teams.value.length);
          
          // Pre-select the current team if it exists
          if (props.playerPosition === 'player1' && props.matchData.player1?.id) {
            selectedTeamId.value = props.matchData.player1.id;
          } else if (props.playerPosition === 'player2' && props.matchData.player2?.id) {
            selectedTeamId.value = props.matchData.player2.id;
          }
        } else {
          error.value = "No teams data received from the server";
        }
      } catch (err) {
        console.error('Error fetching teams:', err);
        error.value = err.response?.data?.error || 'Failed to load teams. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const selectTeam = (team) => {
      selectedTeamId.value = team.id;
    };

    const confirmSelection = () => {
      if (!selectedTeamId.value) return;
      
      const selectedTeam = teams.value.find(team => team.id == selectedTeamId.value);
      if (selectedTeam) {
        emit('team-selected', {
          team: selectedTeam,
          playerPosition: props.playerPosition,
          matchData: props.matchData
        });
      }
      closeModal();
    };

    const closeModal = () => {
      emit('close');
    };

    // Watch for changes to show prop
    watch(() => props.show, (newValue) => {
      if (newValue) {
        // Reset selection and fetch teams when modal opens
        selectedTeamId.value = null;
        fetchTeams();
      }
    });

    // Initial fetch if modal is shown
    onMounted(() => {
      if (props.show) {
        fetchTeams();
      }
    });

    return {
      teams,
      loading,
      error,
      selectedTeamId,
      selectTeam,
      confirmSelection,
      closeModal,
      debug
    };
  }
};
</script>

<style scoped>
.modal-backdrop {
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
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: 60vh;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.team-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.team-item {
  padding: 12px 15px;
  border-radius: 4px;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.team-item:hover {
  background-color: #f1f8e9;
  transform: translateX(2px);
}

.team-item.selected {
  background-color: #e8f5e9;
  border-left: 4px solid #4caf50;
  color: #2e7d32;
  font-weight: 600;
}

.loading-indicator, .error-message, .no-teams {
  padding: 20px;
  text-align: center;
}

.error-message {
  color: #d32f2f;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3e8e41;
}

.btn-secondary {
  background-color: #f1f1f1;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Add debug info styling */
.debug-info {
  background-color: #f8f9fa;
  padding: 10px;
  margin: 10px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  color: #666;
}
</style> 