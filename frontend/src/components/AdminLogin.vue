<template>
  <div class="admin-login">
    <div class="login-card">
      <h2>Admin Login</h2>
      <p class="login-description">Please enter the admin password to access the administration area.</p>
      
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            class="form-control"
            placeholder="Enter admin password"
            required
            ref="passwordInput"
          >
        </div>
        
        <p v-if="auth.state.error" class="error-message">{{ auth.state.error }}</p>
        
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="isLoggingIn">
            {{ isLoggingIn ? 'Logging in...' : 'Login' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import auth from '../store/auth';

const router = useRouter();
const password = ref('');
const isLoggingIn = ref(false);
const passwordInput = ref(null);

// Focus the password input when component mounts
onMounted(() => {
  passwordInput.value.focus();
});

// Handle login form submission
const login = async () => {
  if (!password.value) return;
  
  isLoggingIn.value = true;
  
  try {
    // Try to authenticate with the provided password
    const success = await auth.login(password.value);
    
    if (success) {
      // If login was successful, redirect to the originally requested admin page
      router.push(router.currentRoute.value.query.redirect || '/admin');
    } else {
      // If login failed, clear the password field and focus it
      password.value = '';
      passwordInput.value.focus();
    }
  } catch (error) {
    console.error('Login error:', error);
  } finally {
    isLoggingIn.value = false;
  }
};
</script>

<style scoped>
.admin-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.login-card {
  background-color: var(--color-background-card);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  box-shadow: var(--shadow-md);
  width: 100%;
  max-width: 450px;
}

.login-card h2 {
  margin-top: 0;
  margin-bottom: var(--space-md);
  color: var(--color-accent);
  font-size: 1.5rem;
  position: relative;
  padding-bottom: var(--space-sm);
}

.login-card h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-secondary));
  border-radius: var(--radius-full);
}

.login-description {
  margin-bottom: var(--space-lg);
  color: var(--color-text-light);
}

.login-form {
  margin-top: var(--space-md);
}

.form-group {
  margin-bottom: var(--space-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-xs);
  font-weight: 500;
  color: var(--color-text);
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 1rem;
  transition: border-color var(--transition-fast);
}

.form-control:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.1);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--space-md);
  font-size: 0.9rem;
}

.form-actions {
  margin-top: var(--space-lg);
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-primary:disabled {
  background-color: var(--color-muted);
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .login-card {
    padding: var(--space-lg);
    margin: 0 var(--space-md);
  }
}
</style> 