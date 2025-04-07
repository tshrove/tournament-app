<template>
  <div class="bracket-view">
    <h1>Tournament Bracket JSON Editor</h1>

    <!-- Add tournament ID indicator for debugging -->
    <div class="tournament-indicator" v-if="tournamentId">
      Tournament ID: {{ tournamentId }}
    </div>
    <div class="tournament-indicator warning" v-else>
      No Tournament ID detected - Bracket management disabled.
    </div>

    <!-- Bracket Management Section -->
    <div class="bracket-management card" v-if="tournamentId">
      <h2>Manage Brackets</h2>
      <div v-if="loadingBrackets" class="loading-indicator">Loading brackets...</div>
      <div v-else-if="managementError" class="error-message">{{ managementError }}</div>
      <div v-else class="controls-grid">
        <!-- Bracket Selection -->
        <div class="control-group select-group">
          <label for="bracketSelect">Select Bracket:</label>
          <select id="bracketSelect" v-model="selectedBracketId" @change="onBracketSelectChange">
            <option :value="null" disabled>-- Select a bracket --</option>
            <option v-for="bracket in storedBrackets" :key="bracket.id" :value="bracket.id">
              {{ bracket.name }} (ID: {{ bracket.id }})
            </option>
          </select>
          <button 
            class="btn btn-danger delete-button" 
            @click="confirmDeleteBracket" 
            :disabled="!selectedBracketId || deletingBracket"
            title="Delete selected bracket"
          >
            <span v-if="deletingBracket">Deleting...</span>
            <span v-else>🗑️ Delete</span>
          </button>
        </div>

        <!-- Create New Bracket -->
        <div class="control-group create-group">
          <label for="newBracketName">New Bracket Name:</label>
          <input type="text" id="newBracketName" v-model="newBracketName" placeholder="e.g., Main Event, Consolation">
          <button 
            class="btn btn-primary" 
            @click="createNewBracket" 
            :disabled="!newBracketName || creatingBracket"
          >
            {{ creatingBracket ? 'Creating...' : '＋ Create New' }}
          </button>
        </div>
      </div>
    </div>

    <div class="bracket-editor-container" v-if="tournamentId">
      <div class="instructions">
        <h3>Bracket JSON Editor{{ selectedBracket ? ` for: ${selectedBracket.name}` : '' }}</h3>
        <p>Edit the JSON for the selected bracket below. Click "Update Bracket" to save changes.</p>
      </div>

      <div class="form-group">
        <label for="bracketJson">Bracket JSON:</label>
        <textarea
          id="bracketJson"
          v-model="bracketJson"
          class="json-editor"
          placeholder="Select or create a bracket to load/edit JSON..."
          rows="15"
          :disabled="!selectedBracketId"
          @input="validateJson"
        ></textarea>
      </div>

      <div v-if="jsonError && selectedBracketId" class="error-message">
        <p>{{ jsonError }}</p>
      </div>

      <div class="button-group">
        <button
          class="btn btn-primary save-button" 
          @click="saveBracketChanges" 
          :disabled="!selectedBracketId || isInvalid || saving"
          title="Save changes to the selected bracket"
        >
          {{ saving ? "Updating..." : "💾 Update Bracket" }}
        </button>
        <button 
            class="btn btn-secondary sample-button" 
            @click="loadSampleJson"
            title="Load vue-tournament sample JSON into the editor (will overwrite current content)"
         >
           🔄 Load Sample
         </button>
      </div>

      <div v-if="saveSuccess" class="success-message">
        <p>{{ successMessage || 'Bracket saved successfully!' }}</p>
      </div>

      <div v-if="saveError" class="error-message">
        <p>{{ saveError }}</p>
      </div>
    </div>

    <!-- Bracket Visualization Section -->
    <div
      class="bracket-visualization-container"
      v-if="parsedBracketData && !isInvalid && selectedBracketId"
    >
      <h2>Bracket Visualization{{ selectedBracket ? ` for: ${selectedBracket.name}` : '' }}</h2>
      <div class="tournament-bracket-wrapper">
        <TournamentBracket
          :rounds="parsedBracketData"
          @onMatchClick="matchClicked"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import api from "../services/api";
import { useRoute } from "vue-router";
import TournamentBracket from "../components/TournamentBracket.vue";

const route = useRoute();
const bracketJson = ref("");
const jsonError = ref("");
const saveError = ref("");
const saveSuccess = ref(false);
const successMessage = ref("");
const isInvalid = ref(true);
const saving = ref(false);
const loadingBrackets = ref(false);
const creatingBracket = ref(false);
const deletingBracket = ref(false);
const managementError = ref("");

// Bracket Management State
const storedBrackets = ref([]);
const selectedBracketId = ref(null);
const newBracketName = ref("");

const tournamentId = computed(() => {
  const id = route.params.id || route.query.tournament_id;
  return id ? parseInt(id, 10) || id : null;
});

const selectedBracket = computed(() => {
  return storedBrackets.value.find(b => b.id === selectedBracketId.value) || null;
});

// Computed property to parse and transform data
const parsedBracketData = computed(() => {
  if (!bracketJson.value || isInvalid.value) return null;
  try {
    const json = JSON.parse(bracketJson.value);
    return transformToVueTournamentFormat(json);
  } catch (err) {
    // jsonError.value = `Error parsing JSON for visualization: ${err.message}`; // Set error in validateJson
    return null;
  }
});

// Transformation function (ensure it handles potential empty input gracefully)
const transformToVueTournamentFormat = (data) => {
  if (!data || !data.rounds) {
    console.warn("Transform input data is missing 'rounds'");
    return [];
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

// Load sample data in the vue-tournament format
const loadSampleJson = () => {
  console.log("loadSampleJson triggered"); // Log 1
  const sampleBracket = {
    rounds: [
      // Quarter
      {
        matchs: [
          { id: "match1", winner: "1", team1: { id: "1", name: "Competitor 1", score: 2 }, team2: { id: "2", name: "Competitor 2", score: 1 } },
          { id: "match2", winner: "4", team1: { id: "3", name: "Competitor 3", score: 0 }, team2: { id: "4", name: "Competitor 4", score: 2 } },
          { id: "match3", winner: "5", team1: { id: "5", name: "Competitor 5", score: 2 }, team2: { id: "6", name: "Competitor 6", score: 1 } },
          { id: "match4", winner: "8", team1: { id: "7", name: "Competitor 7", score: 0 }, team2: { id: "8", name: "Competitor 8", score: 2 } },
        ],
      },
      // Semi
      {
        matchs: [
          { id: "match5", winner: "4", team1: { id: "1", name: "Competitor 1", score: 1 }, team2: { id: "4", name: "Competitor 4", score: 2 } },
          { id: "match6", winner: "8", team1: { id: "5", name: "Competitor 5", score: 1 }, team2: { id: "8", name: "Competitor 8", score: 2 } },
        ],
      },
      // Final
      {
        matchs: [
          { id: "any_match_id", winner: "8", team1: { id: "4", name: "Competitor 4", score: 1 }, team2: { id: "8", name: "Competitor 8", score: 3 } },
        ],
      },
    ]
  };
  console.log("Sample bracket object:", sampleBracket); // Log 2
  const jsonString = JSON.stringify(sampleBracket, null, 2);
  console.log("Stringified sample JSON:", jsonString); // Log 3
  bracketJson.value = jsonString;
  console.log("bracketJson.value after assignment:", bracketJson.value); // Log 4
  validateJson();
};

const validateJson = () => {
  console.log("validateJson triggered. Current value:", bracketJson.value.substring(0, 100) + "..."); // Log 5
  saveError.value = "";
  if (!bracketJson.value.trim()) {
    if (selectedBracketId.value) {
        console.log("validateJson: Empty JSON for existing bracket - invalid"); // Log 5a
        jsonError.value = "JSON cannot be empty for an existing bracket";
        isInvalid.value = true;
        return;
    } else {
        console.log("validateJson: Empty JSON, no bracket selected - invalid but no error message"); // Log 5b
        jsonError.value = "";
        isInvalid.value = true; // Cannot save empty / new without content
        return;
    }
  }
  try {
    JSON.parse(bracketJson.value);
    console.log("validateJson: JSON parsed successfully - valid"); // Log 5c
    jsonError.value = "";
    isInvalid.value = false;
  } catch (err) {
    console.log("validateJson: JSON parse error - invalid", err.message); // Log 5d
    jsonError.value = `Invalid JSON: ${err.message}`;
    isInvalid.value = true;
  }
};

// --- Bracket Management Functions ---

const fetchBrackets = async () => {
  if (!tournamentId.value) {
    managementError.value = "No tournament selected.";
    return;
  }
  loadingBrackets.value = true;
  managementError.value = "";
  try {
    const response = await api.getTournamentBrackets(tournamentId.value);
    storedBrackets.value = response.data || [];
    if (storedBrackets.value.length > 0 && !selectedBracketId.value) {
      // Optionally select the first bracket by default
      // selectedBracketId.value = storedBrackets.value[0].id;
      // loadBracket(selectedBracketId.value);
      // For now, require explicit selection
      bracketJson.value = "";
      validateJson();
    } else if (selectedBracketId.value) {
        // Reload current if it still exists
        const exists = storedBrackets.value.some(b => b.id === selectedBracketId.value);
        if (!exists) {
            selectedBracketId.value = null;
            bracketJson.value = "";
        }
    } else {
        bracketJson.value = "";
    }
    
  } catch (err) {
    console.error("Error fetching brackets:", err);
    managementError.value = "Failed to load brackets.";
    storedBrackets.value = [];
  } finally {
    loadingBrackets.value = false;
  }
};

const loadBracket = async (bracketId) => {
  if (!bracketId) {
    bracketJson.value = "";
    selectedBracketId.value = null;
    validateJson();
    return;
  }
  // Find in already fetched list first
  const existing = storedBrackets.value.find(b => b.id === bracketId);
  if (existing) {
      bracketJson.value = existing.bracket_json;
      selectedBracketId.value = bracketId; // Ensure state is consistent
      validateJson();
      clearNotifications();
      return;
  }
  // If not found (shouldn't happen if fetchBrackets worked), maybe fetch individually?
  // For simplicity, assume it's always in the fetched list after selection.
  console.warn("Selected bracket ID not found in stored list, clearing editor.")
  bracketJson.value = "";
  selectedBracketId.value = null;
  validateJson();
};

const onBracketSelectChange = () => {
    loadBracket(selectedBracketId.value);
};

const createNewBracket = async () => {
  if (!tournamentId.value || !newBracketName.value) return;
  
  creatingBracket.value = true;
  managementError.value = "";
  clearNotifications();
  
  // Use current editor content or a default empty bracket structure
  let initialJson = bracketJson.value;
  if (!initialJson || isInvalid.value) {
      initialJson = JSON.stringify({ rounds: [] }, null, 2); // Default empty structure
  }
  
  try {
    // Validate the JSON before creating
    JSON.parse(initialJson);
  } catch (err) {
      managementError.value = `Cannot create bracket with invalid JSON: ${err.message}`;
      creatingBracket.value = false;
      return;
  }

  try {
    const response = await api.createBracket(tournamentId.value, newBracketName.value, initialJson);
    storedBrackets.value.push(response.data);
    // Select the newly created bracket
    selectedBracketId.value = response.data.id;
    bracketJson.value = initialJson; // Load the JSON used for creation
    validateJson();
    newBracketName.value = ""; // Clear the input
    showSuccess("Bracket created successfully!");
  } catch (err) {
    console.error("Error creating bracket:", err);
    managementError.value = err.response?.data?.error || "Failed to create bracket.";
  } finally {
    creatingBracket.value = false;
  }
};

// Renamed from saveBracketJson
const saveBracketChanges = async () => {
  if (!selectedBracketId.value || isInvalid.value) return;

  saving.value = true;
  clearNotifications();

  try {
    const currentBracket = storedBrackets.value.find(b => b.id === selectedBracketId.value);
    // Pass undefined for name if we don't want to update it (or add a name edit field)
    await api.updateBracket(selectedBracketId.value, currentBracket?.name, bracketJson.value);
    
    // Update the stored bracket JSON in the local list
    const index = storedBrackets.value.findIndex(b => b.id === selectedBracketId.value);
    if (index !== -1) {
        storedBrackets.value[index].bracket_json = bracketJson.value;
        storedBrackets.value[index].name = currentBracket?.name; // Ensure name stays consistent locally
    }
    showSuccess("Bracket updated successfully!");
  } catch (err) {
    console.error("Error updating bracket:", err);
    saveError.value = err.response?.data?.error || "Failed to update bracket.";
  } finally {
    saving.value = false;
  }
};

const confirmDeleteBracket = () => {
    if (!selectedBracket.value) return;
    if (window.confirm(`Are you sure you want to delete the bracket "${selectedBracket.value.name}"? This cannot be undone.`)) {
        deleteSelectedBracket();
    }
};

const deleteSelectedBracket = async () => {
  if (!selectedBracketId.value) return;
  
deletingBracket.value = true;
  managementError.value = "";
  clearNotifications();

  try {
    await api.deleteBracket(selectedBracketId.value);
    // Remove from local list
    storedBrackets.value = storedBrackets.value.filter(b => b.id !== selectedBracketId.value);
    // Clear selection and editor
    selectedBracketId.value = null;
    bracketJson.value = "";
    validateJson();
    showSuccess("Bracket deleted successfully!");
  } catch (err) {
    console.error("Error deleting bracket:", err);
    managementError.value = err.response?.data?.error || "Failed to delete bracket.";
  } finally {
    deletingBracket.value = false;
  }
};

// --- Utility Functions ---
const clearNotifications = () => {
    saveError.value = "";
    saveSuccess.value = false;
    successMessage.value = "";
    managementError.value = "";
};

const showSuccess = (message) => {
    clearNotifications();
    saveSuccess.value = true;
    successMessage.value = message;
    setTimeout(() => { saveSuccess.value = false; successMessage.value = ""; }, 3000);
};

// --- Event Handlers & Lifecycle ---

const matchClicked = (matchId) => {
  console.log("Match clicked (vue-tournament):", matchId);
  // Future: Handle match click (e.g., scoring)
};

// Watch for tournament ID changes to refetch brackets
watch(tournamentId, (newId, oldId) => {
  if (newId !== oldId) {
    selectedBracketId.value = null; // Reset selection when tournament changes
    storedBrackets.value = [];
    bracketJson.value = "";
    fetchBrackets();
  }
});

onMounted(() => {
  fetchBrackets(); // Fetch brackets for the current tournament on load
});
</script>

<style scoped>
.card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 20px;
}

.bracket-management h2 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
  color: #2c3e50;
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  align-items: end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-weight: 600;
  color: #333;
  margin-bottom: 0;
}

.select-group {
    flex-direction: row;
    align-items: center;
    gap: 10px;
}
.select-group label {
    flex-shrink: 0;
}

.select-group select {
    flex-grow: 1;
    padding: 8px 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
}

.create-group input[type="text"] {
    padding: 8px 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
}

.create-group button {
    margin-top: 5px; /* Align button better */
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 15px; /* Ensure there's a gap */
  margin-top: 20px; /* Add margin above the buttons */
  margin-bottom: 20px;
}

.delete-button {
    padding: 6px 10px;
    background-color: #f44336;
    color: white;
    font-size: 0.9em;
    line-height: 1;
    flex-shrink: 0;
}
.delete-button:hover:not(:disabled) {
    background-color: #d32f2f;
}

.loading-indicator {
    text-align: center;
    padding: 15px;
    color: #666;
}

/* Adjustments for bracket editor */
.bracket-editor-container .instructions h3 {
    font-size: 1.2em;
    margin-bottom: 5px;
}
.bracket-editor-container .instructions p {
    margin-top: 0;
    font-size: 0.95em;
}

/* ... rest of existing styles ... */

.click-info {
  text-align: center;
  color: #666;
  margin-bottom: 15px;
  font-style: italic;
}

/* Removed :deep styles specific to vue-tournament-bracket */
</style>
