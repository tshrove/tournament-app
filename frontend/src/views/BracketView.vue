<template>
  <div class="bracket-view">
    <h1>Tournament Bracket JSON Editor</h1>

    <div class="bracket-editor-container">
      <div class="instructions">
        <h3>Bracket JSON Editor</h3>
        <p>
          Enter your bracket configuration as a JSON object. This will be stored
          with the current tournament.
        </p>
        <p>
          The bracket should follow a valid tournament bracket structure. JSON
          will be validated before saving.
        </p>
      </div>

      <div class="form-group">
        <label for="bracketJson">Bracket JSON:</label>
        <textarea
          id="bracketJson"
          v-model="bracketJson"
          class="json-editor"
          placeholder="Enter valid JSON bracket configuration here..."
          rows="15"
          @input="validateJson"
        ></textarea>
      </div>

      <div v-if="jsonError" class="error-message">
        <p>{{ jsonError }}</p>
      </div>

      <div class="button-group">
        <button
          class="btn btn-primary save-button"
          @click="saveBracketJson"
          :disabled="isInvalid || saving"
        >
          {{ saving ? "Saving..." : "Save Bracket" }}
        </button>
        <button class="btn btn-secondary sample-button" @click="loadSampleJson">
          Load Sample
        </button>
      </div>

      <div v-if="saveSuccess" class="success-message">
        <p>Bracket configuration successfully saved!</p>
      </div>

      <div v-if="saveError" class="error-message">
        <p>{{ saveError }}</p>
      </div>
    </div>

    <!-- Bracket Visualization Section -->
    <div
      class="bracket-visualization-container"
      v-if="parsedBracketData && !isInvalid"
    >
      <h2>Bracket Visualization</h2>
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
import { ref, onMounted, computed } from "vue";
import api from "../services/api";
import { useRoute } from "vue-router";
import TournamentBracket from "../components/TournamentBracket.vue";

const route = useRoute();
const bracketJson = ref("");
const jsonError = ref("");
const saveError = ref("");
const saveSuccess = ref(false);
const isInvalid = ref(true);
const saving = ref(false);

// Store parsed bracket data for visualization
const parsedBracketData = computed(() => {
  if (!bracketJson.value || isInvalid.value) return null;

  try {
    const json = JSON.parse(bracketJson.value);

    // Transform the data into the format expected by vue-tournament
    const transformedData = transformBracketDataForViz(json);
    return transformedData;
  } catch (err) {
    console.error("Error parsing JSON for visualization:", err);
    return null;
  }
});

const transformBracketDataForViz = (data) => {
  // If the data is already in the right format (array of rounds with matchs property),
  // return it as is
  if (Array.isArray(data.rounds) && data.rounds.length > 0 && data.rounds[0].matchs) {
    return data.rounds;
  }

  // Otherwise, try to transform it to the expected format for vue-tournament
  const transformed = [];

  // If we have a rounds object with keys like "round_1", "round_2", etc.
  if (data.rounds && typeof data.rounds === "object") {
    const roundKeys = Object.keys(data.rounds).sort();

    roundKeys.forEach((roundKey) => {
      const roundData = {
        matchs: []
      };

      data.rounds[roundKey].forEach(match => {
        roundData.matchs.push({
          id: match.matchId || match.id || `match_${Math.random().toString(36).substring(2, 9)}`,
          winner: match.winnerId || match.winner_id || null,
          team1: {
            id: match.team1Id || (match.team1 ? match.team1.id : null),
            name: match.team1Name || (match.team1 ? match.team1.name : "Team 1"),
            score: match.team1Score !== undefined ? match.team1Score : 
                   (match.team1 && match.team1.score !== undefined) ? match.team1.score : null
          },
          team2: {
            id: match.team2Id || (match.team2 ? match.team2.id : null),
            name: match.team2Name || (match.team2 ? match.team2.name : "Team 2"),
            score: match.team2Score !== undefined ? match.team2Score : 
                   (match.team2 && match.team2.score !== undefined) ? match.team2.score : null
          }
        });
      });

      transformed.push(roundData);
    });
  }

  return transformed;
};

const validateJson = () => {
  saveError.value = "";
  saveSuccess.value = false;

  if (!bracketJson.value.trim()) {
    jsonError.value = "JSON cannot be empty";
    isInvalid.value = true;
    return;
  }

  try {
    // Just make sure it's valid JSON, no further validation
    JSON.parse(bracketJson.value);
    jsonError.value = "";
    isInvalid.value = false;
  } catch (err) {
    jsonError.value = `Invalid JSON: ${err.message}`;
    isInvalid.value = true;
  }
};

const saveBracketJson = async () => {
  saving.value = true;
  saveError.value = "";
  saveSuccess.value = false;

  try {
    // Get tournament ID from route if available
    const tournamentId = route.params.tournamentId || route.query.tournament_id;

    // Attempt to parse again to ensure it's valid
    const bracketData = JSON.parse(bracketJson.value);
    console.log(bracketData);
    console.log(bracketJson.value);

    // Send the JSON string to be stored in the database
    await api.saveBracketJson({
      bracket_json: bracketJson.value,
      tournament_id: tournamentId,
    });

    saveSuccess.value = true;
  } catch (err) {
    console.error("Error saving bracket JSON:", err);
    saveError.value =
      err.response?.data?.error || "Failed to save bracket JSON";
  } finally {
    saving.value = false;
  }
};

const fetchBracketJson = async () => {
  try {
    const tournamentId = route.params.tournamentId || route.query.tournament_id;
    const params = tournamentId ? { tournament_id: tournamentId } : {};

    const response = await api.getBracket(params);

    // If there's existing data, format it as JSON string for the editor
    if (response.data && Object.keys(response.data).length > 0) {
      bracketJson.value = JSON.stringify(response.data, null, 2);
      validateJson();
    }
  } catch (err) {
    console.error("Error fetching bracket data:", err);
    saveError.value =
      err.response?.data?.error || "Failed to load existing bracket data";
  }
};

// Load a sample bracket in the vue-tournament format
const loadSampleJson = () => {
  // Create a sample bracket structure using vue-tournament format
  const sampleBracket = {
    rounds: [
      {
        matchs: [
          {
            id: "match1",
            team1: {
              id: "1",
              name: "Competitor 1",
              score: 2,
            },
            team2: {
              id: "2",
              name: "Competitor 2",
              score: 1,
            },
            winner: "1",
          },
          {
            id: "match2",
            team1: {
              id: "3",
              name: "Competitor 3",
              score: 0,
            },
            team2: {
              id: "4",
              name: "Competitor 4",
              score: 2,
            },
            winner: "4",
          },
          {
            id: "match3",
            team1: {
              id: "5",
              name: "Competitor 5",
              score: 2,
            },
            team2: {
              id: "6",
              name: "Competitor 6",
              score: 1,
            },
            winner: "5",
          },
          {
            id: "match4",
            team1: {
              id: "7",
              name: "Competitor 7",
              score: 0,
            },
            team2: {
              id: "8",
              name: "Competitor 8",
              score: 2,
            },
            winner: "8",
          },
        ],
      },
      {
        matchs: [
          {
            id: "match5",
            team1: {
              id: "1",
              name: "Competitor 1",
              score: 1,
            },
            team2: {
              id: "4",
              name: "Competitor 4",
              score: 2,
            },
            winner: "4",
          },
          {
            id: "match6",
            team1: {
              id: "5",
              name: "Competitor 5",
              score: 1,
            },
            team2: {
              id: "8",
              name: "Competitor 8",
              score: 2,
            },
            winner: "8",
          },
        ],
      },
      {
        matchs: [
          {
            id: "any_match_id",
            team1: {
              id: "4",
              name: "Competitor 4",
              score: 1,
            },
            team2: {
              id: "8",
              name: "Competitor 8",
              score: 3,
            },
            winner: "8",
          },
        ],
      },
    ],
  };

  // Set it as the current JSON
  bracketJson.value = JSON.stringify(sampleBracket, null, 2);
  validateJson();
};

// Event handlers for the bracket visualization
const teamClicked = (team) => {
  console.log("Team clicked:", team);
};

const matchClicked = (matchId) => {
  console.log("Match clicked:", matchId);
};

onMounted(() => {
  fetchBracketJson();
});
</script>

<style scoped>
.bracket-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h1,
h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
}

.bracket-editor-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.instructions {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.instructions h3 {
  margin-top: 0;
  color: #2c3e50;
}

.instructions p {
  color: #666;
  margin: 8px 0;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.json-editor {
  width: 100%;
  font-family: monospace;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
}

.json-editor:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.btn {
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3e8e41;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.save-button,
.sample-button {
  min-width: 120px;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #f8d7da;
  color: #721c24;
  border-radius: 4px;
  border-left: 4px solid #f5c6cb;
}

.success-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #d4edda;
  color: #155724;
  border-radius: 4px;
  border-left: 4px solid #c3e6cb;
}

/* Bracket visualization styles */
.bracket-visualization-container {
  margin-top: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow: auto;
}

.tournament-bracket-wrapper {
  overflow-x: auto;
  min-height: 500px;
  padding: 20px 0;
}
</style>
