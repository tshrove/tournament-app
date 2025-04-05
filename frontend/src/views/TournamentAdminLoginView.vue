<template>
  <div class="tournament-admin-login-view">
    <div class="login-container">
      <div class="login-card">
        <h1>Tournament Management</h1>
        <p>Enter the tournament administrator password to continue.</p>
        
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="password">Administrator Password</label>
            <input 
              type="password" 
              id="password" 
              v-model="password" 
              required
              placeholder="Enter administrator password"
              autocomplete="current-password"
            />
          </div>
          
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        
        <div class="back-link">
          <a @click="goBack">Back to tournaments</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import tournamentAdminAuth from '../store/tournament-admin-auth';

const router = useRouter();
const password = ref('');
const error = ref('');
const loading = ref(false);

// Hard-coded password for tournament administration
const TOURNAMENT_ADMIN_PASSWORD = "T$hro^E!!!!!!0619";

const login = () => {
  loading.value = true;
  error.value = '';
  
  // Check if password matches the hard-coded admin password
  if (password.value === TOURNAMENT_ADMIN_PASSWORD) {
    // Set authentication in the store
    tournamentAdminAuth.login();
    
    // Redirect to the tournament management page or to the intended destination
    const redirectPath = router.currentRoute.value.query.redirect || '/tournament-admin';
    router.push(redirectPath);
  } else {
    error.value = 'Incorrect administrator password';
    loading.value = false;
  }
};

const goBack = () => {
  router.push('/');
};
</script>

<style scoped>
.tournament-admin-login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 1rem;
}

.login-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

h1 {
  color: var(--color-primary);
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.75rem;
  text-align: center;
}

p {
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
  text-align: center;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.error-message {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.back-link {
  margin-top: 1.5rem;
  text-align: center;
}

.back-link a {
  color: var(--color-primary);
  text-decoration: none;
  cursor: pointer;
}

.back-link a:hover {
  text-decoration: underline;
}
</style> 