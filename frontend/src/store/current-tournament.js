// Current Tournament Store
import { reactive } from 'vue';

// Check if there is a stored selected tournament in localStorage
const getInitialState = () => {
  const storedTournament = localStorage.getItem('current_tournament');
  return storedTournament ? JSON.parse(storedTournament) : { 
    id: null,
    name: null,
    isSelected: false
  };
};

// Create a reactive state object
const state = reactive(getInitialState());

export default {
  // Expose the state
  state,
  
  // Set current tournament
  setTournament(tournamentData) {
    state.id = tournamentData.id;
    state.name = tournamentData.name;
    state.isSelected = true;
    localStorage.setItem('current_tournament', JSON.stringify(state));
  },
  
  // Clear current tournament
  clearTournament() {
    state.id = null;
    state.name = null;
    state.isSelected = false;
    localStorage.removeItem('current_tournament');
  },
  
  // Check if a tournament is selected
  hasSelectedTournament() {
    return state.isSelected && state.id !== null;
  }
}; 