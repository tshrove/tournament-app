// Tournament Admin Authentication Store
import { reactive } from 'vue';

// Check if the user is authenticated from localStorage
const getInitialState = () => {
  const storedAuth = localStorage.getItem('tournament_admin_auth');
  return storedAuth ? JSON.parse(storedAuth) : { isAuthenticated: false };
};

// Create a reactive state object
const state = reactive(getInitialState());

export default {
  // Expose the state
  state,
  
  // Login function - set authentication to true
  login() {
    state.isAuthenticated = true;
    localStorage.setItem('tournament_admin_auth', JSON.stringify(state));
  },
  
  // Logout function - clear authentication
  logout() {
    state.isAuthenticated = false;
    localStorage.removeItem('tournament_admin_auth');
  },
  
  // Check if the user is authenticated
  isAuthenticated() {
    return state.isAuthenticated;
  }
}; 