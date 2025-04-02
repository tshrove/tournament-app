import { reactive, readonly } from 'vue';
import api from '../services/api';

// Static password fallback for admin access
const STATIC_PASSWORD = "T$hro^E!!!!!!0619";

// Create a reactive state
const state = reactive({
  isAuthenticated: false,
  customPassword: '',
  error: null
});

// Read authentication from localStorage on initialization
try {
  const storedAuth = localStorage.getItem('adminAuthenticated');
  if (storedAuth === 'true') {
    state.isAuthenticated = true;
  }
} catch (e) {
  console.error('Error accessing localStorage:', e);
}

// Authentication actions
const actions = {
  // Validate admin password
  async login(password) {
    try {
      // If the password matches the static password, authenticate
      if (password === STATIC_PASSWORD) {
        state.isAuthenticated = true;
        state.error = null;
        
        // Store authentication in localStorage for persistence
        try {
          localStorage.setItem('adminAuthenticated', 'true');
        } catch (e) {
          console.error('Error writing to localStorage:', e);
        }
        
        return true;
      }
      
      // Check if there's a custom password set
      const response = await api.getSettings();
      const settings = response.data;
      
      // If custom password exists and matches, authenticate
      if (settings.adminPassword && password === settings.adminPassword) {
        state.isAuthenticated = true;
        state.error = null;
        
        // Store authentication in localStorage for persistence
        try {
          localStorage.setItem('adminAuthenticated', 'true');
        } catch (e) {
          console.error('Error writing to localStorage:', e);
        }
        
        return true;
      }
      
      // If we get here, the password was invalid
      state.error = 'Invalid password';
      return false;
    } catch (error) {
      console.error('Login error:', error);
      state.error = 'An error occurred during login';
      return false;
    }
  },
  
  // Logout and clear authentication
  logout() {
    state.isAuthenticated = false;
    
    // Clear authentication from localStorage
    try {
      localStorage.removeItem('adminAuthenticated');
    } catch (e) {
      console.error('Error removing from localStorage:', e);
    }
  },
  
  // Clear any error messages
  clearError() {
    state.error = null;
  }
};

// Export readonly state and actions
export default {
  state: readonly(state),
  ...actions
}; 