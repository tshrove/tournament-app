<template>
  <div class="public-bracket-view">
    <h1>Tournament Brackets</h1>
    <p v-if="tournamentId">Displaying brackets for Tournament ID: {{ tournamentId }}</p>
    <p v-else class="error-message">No Tournament ID specified.</p>

    <div v-if="loading" class="loading-indicator">Loading bracket information...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="bracketsList.length === 0" class="no-brackets">
      No brackets have been created for this tournament yet.
    </div>

    <div v-else class="bracket-selector-container card">
       <label for="bracketSelectPublic">Select Bracket to View:</label>
       <select id="bracketSelectPublic" v-model="selectedBracketId" @change="loadSelectedBracket">
         <option :value="null" disabled>-- Select a bracket --</option>
         <option v-for="bracket in bracketsList" :key="bracket.id" :value="bracket.id">
           {{ bracket.name }} (ID: {{ bracket.id }})
         </option>
       </select>
    </div>

    <div v-if="loadingBracketData" class="loading-indicator">Loading selected bracket data...</div>
    
    <!-- Bracket Visualization Section -->
    <div 
      class="bracket-visualization-container card" 
      v-if="selectedBracketData && !loadingBracketData"
    >
      <h2>{{ selectedBracketName }}</h2>
      <div class="tournament-bracket-wrapper">
        <TournamentBracket 
          :rounds="selectedBracketData" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';
import TournamentBracket from '../components/TournamentBracket.vue'; // Re-use our display component

const route = useRoute();
const loading = ref(true);
const loadingBracketData = ref(false);
const error = ref(null);
const bracketsList = ref([]);
const selectedBracketId = ref(null);
const selectedBracketData = ref(null); // Parsed & transformed data for the visualizer

const tournamentId = computed(() => {
  // Get ID from route params (make sure route is configured with props: true)
  const id = route.params.id || route.query.tournament_id;
  return id ? parseInt(id, 10) || id : null;
});

const selectedBracketName = computed(() => {
    const selected = bracketsList.value.find(b => b.id === selectedBracketId.value);
    return selected ? selected.name : 'Bracket Visualization';
});

// Fetch the list of available brackets for this tournament
const fetchBracketsList = async () => {
  if (!tournamentId.value) {
    error.value = "Tournament ID is missing.";
    loading.value = false;
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    const response = await api.getTournamentBrackets(tournamentId.value);
    bracketsList.value = response.data || [];
    // Automatically select the first bracket if available
    if (bracketsList.value.length > 0) {
        selectedBracketId.value = bracketsList.value[0].id;
        // loadSelectedBracket will be called by the watcher
    }
  } catch (err) {
    console.error("Error fetching brackets list:", err);
    error.value = "Failed to load bracket list for this tournament.";
    bracketsList.value = [];
  } finally {
    loading.value = false;
  }
};

// Load the JSON data for the selected bracket
const loadSelectedBracket = async () => {
  if (!selectedBracketId.value) {
    selectedBracketData.value = null;
    return;
  }
  loadingBracketData.value = true;
  selectedBracketData.value = null; // Clear previous data
  error.value = null; // Clear previous errors
  
  try {
    // Find the bracket data from the list (already fetched)
    const selectedBracket = bracketsList.value.find(b => b.id === selectedBracketId.value);
    if (selectedBracket && selectedBracket.bracket_json) {
        const parsedJson = JSON.parse(selectedBracket.bracket_json);
        selectedBracketData.value = transformToVueTournamentFormat(parsedJson);
        if (!selectedBracketData.value) {
             error.value = "Failed to parse or transform the selected bracket data.";
        }
    } else if (selectedBracket) {
         error.value = "Selected bracket is missing JSON data.";
         selectedBracketData.value = []; // Show empty bracket
    } else {
         error.value = `Bracket with ID ${selectedBracketId.value} not found in the list.`;
    }

    // --- Alternative: Fetch individually (if list doesn't contain JSON) ---
    // const response = await api.getBracketById(selectedBracketId.value);
    // const parsedJson = JSON.parse(response.data.bracket_json);
    // selectedBracketData.value = transformToVueTournamentFormat(parsedJson);
    // ---------------------------------------------------------------------

  } catch (err) {
    console.error("Error loading selected bracket data:", err);
    error.value = "Failed to load or parse the selected bracket data.";
    selectedBracketData.value = null;
  } finally {
    loadingBracketData.value = false;
  }
};

// Transformation function (Copied from BracketView - consider extracting to utils)
const transformToVueTournamentFormat = (data) => {
  if (!data || !data.rounds) {
    console.warn("Transform input data is missing 'rounds'");
    return null; // Return null on bad data
  }
  if (Array.isArray(data.rounds) && data.rounds.length > 0 && data.rounds[0].matchs) {
    return data.rounds; 
  }
  const transformed = [];
  if (typeof data.rounds === "object") {
    const roundKeys = Object.keys(data.rounds).sort();
    roundKeys.forEach((roundKey, roundIndex) => {
      const roundData = { matchs: [] };
      if (Array.isArray(data.rounds[roundKey])) {
         data.rounds[roundKey].forEach((match, matchIndex) => {
            const vueTournamentMatch = {
              id: match.matchId || match.id || `match_${roundIndex}_${matchIndex}`,
              winner: match.winnerId || match.winner || null,
              team1: {
                id: String(match.team1Id || (match.player1 ? match.player1.id : match.team1?.id || null)),
                name: match.team1Name || (match.player1 ? match.player1.name : match.team1?.name || "TBD"),
                score: match.team1Score !== undefined ? match.team1Score : (match.player1 ? match.player1.score : match.team1?.score)
              },
              team2: {
                id: String(match.team2Id || (match.player2 ? match.player2.id : match.team2?.id || null)),
                name: match.team2Name || (match.player2 ? match.player2.name : match.team2?.name || "TBD"),
                score: match.team2Score !== undefined ? match.team2Score : (match.player2 ? match.player2.score : match.team2?.score)
              },
            };
             roundData.matchs.push(vueTournamentMatch);
         });
      }
      transformed.push(roundData);
    });
  }
  return transformed;
};

// Watch for changes in selectedBracketId to load data
watch(selectedBracketId, (newId) => {
    if (newId) {
        loadSelectedBracket();
    }
});

// Fetch bracket list when component mounts
onMounted(() => {
  fetchBracketsList();
});

</script>

<style scoped>
.public-bracket-view {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

h1, h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
}

.card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.bracket-selector-container {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.bracket-selector-container label {
  font-weight: 600;
}

.bracket-selector-container select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
  min-width: 250px;
}

.bracket-visualization-container h2 {
    font-size: 1.4em;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.tournament-bracket-wrapper {
  overflow-x: auto;
  min-height: 400px;
  padding: 20px 0;
  background-color: #fdfdfd; /* Slightly off-white background */
  border: 1px solid #eee;
  border-radius: 5px;
}

.loading-indicator, .error-message, .no-brackets {
  text-align: center;
  padding: 40px 20px;
  margin: 20px 0;
  border-radius: 5px;
}

.loading-indicator {
  color: #666;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.no-brackets {
    background-color: #e9ecef;
    color: #495057;
}

</style> 