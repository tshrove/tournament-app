<script setup>
import { ref, provide } from 'vue';
import ToastNotification from './components/ToastNotification.vue'; // Import the component
import auth from './store/auth';

// Notification State
const notification = ref({
  visible: false,
  message: '',
  type: 'success' // success, error, info
});

// Function to show notification
const showNotification = (message, type = 'success', duration = 4000) => {
  notification.value = {
    visible: true,
    message,
    type,
    duration // Pass duration if needed by Toast component logic
  };
  // No need for timeout here if Toast handles its own closing
};

// Function to hide notification (called by Toast @close event)
const hideNotification = () => {
  notification.value.visible = false;
};

// Provide the showNotification function to child components
provide('showNotification', showNotification);

// Mobile menu toggle
const mobileMenuOpen = ref(false);
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

// Handle logout
const handleLogout = () => {
  auth.logout();
  showNotification('You have been logged out', 'info');
  mobileMenuOpen.value = false;
};
</script>

<template>
  <div id="app-container">
    <header class="app-header">
      <div class="container header-container">
        <div class="logo">
          <h1>🚀 Launchpad</h1>
        </div>
        
        <!-- Mobile menu toggle -->
        <button class="mobile-menu-toggle" @click="toggleMobileMenu" aria-label="Toggle menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
        
        <nav class="main-nav" :class="{ 'mobile-open': mobileMenuOpen }">
          <router-link to="/" class="nav-link" @click="mobileMenuOpen = false">Home</router-link>
          <router-link to="/admin" class="nav-link admin-link" @click="mobileMenuOpen = false">
            <span class="admin-icon">⚙️</span> Admin
          </router-link>
          <button v-if="auth.state.isAuthenticated" @click="handleLogout" class="nav-link logout-button">
            <span class="logout-icon">🔒</span> Logout
          </button>
        </nav>
      </div>
    </header>
    
    <main class="main-content">
      <div class="container">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <div class="footer-content">
          <p>&copy; {{ new Date().getFullYear() }} Launchpad</p>
          <div class="sponsor-badge">
            <span>Developed & Sponsored by</span>
            <a href="https://www.facebook.com/profile.php?id=61561326677708" target="_blank" rel="noopener noreferrer" class="sponsor-name">🚀 Rocket City Rockets</a>
          </div>
          <div class="footer-links">
            <a href="#" class="footer-link">Privacy Policy</a>
            <a href="#" class="footer-link">Terms of Use</a>
            <a href="#" class="footer-link">Contact</a>
          </div>
        </div>
      </div>
    </footer>
    
    <!-- Toast Notification Area -->
    <transition name="fade">
      <ToastNotification 
        v-if="notification.visible"
        :message="notification.message"
        :type="notification.type"
        @close="hideNotification"
      />
    </transition>
  </div>
</template>

<style>
/* Import Inter font for consistent typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base App Layout */
#app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background);
  overflow-x: hidden; /* Prevent horizontal overflow at the container level */
  max-width: 100vw; /* Ensure container doesn't exceed viewport width */
}

/* Header Styling */
.app-header {
  background-color: var(--color-background-card);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: var(--z-dropdown);
  padding: 0.7rem 0;
  transition: box-shadow var(--transition-normal), background-color var(--transition-normal);
}

.app-header:hover {
  box-shadow: var(--shadow-md);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem var(--space-md);
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.main-nav {
  display: flex;
  gap: var(--space-md);
}

.nav-link {
  position: relative;
  color: var(--color-text);
  font-weight: 500;
  padding: var(--space-xs) var(--space-sm);
  text-decoration: none;
  transition: color var(--transition-fast);
  border-radius: var(--radius-sm);
}

.nav-link::after {
  content: '';
  position: absolute;
  width: 0;
  height: 3px;
  bottom: -3px;
  left: 0;
  background: linear-gradient(to right, var(--color-primary), var(--color-secondary));
  transition: width var(--transition-normal);
  border-radius: var(--radius-full);
}

.nav-link:hover {
  color: var(--color-primary);
  text-decoration: none;
}

.nav-link:hover::after {
  width: 100%;
}

.nav-link.router-link-active {
  color: var(--color-primary);
  font-weight: 600;
}

.nav-link.router-link-active::after {
  width: 100%;
}

.admin-link {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  background-color: rgba(67, 97, 238, 0.1);
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--radius-full);
}

.admin-link:hover {
  background-color: rgba(67, 97, 238, 0.2);
}

.admin-icon {
  font-size: 0.9rem;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  background-color: rgba(226, 76, 76, 0.1);
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--radius-full);
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

.logout-button:hover {
  background-color: rgba(226, 76, 76, 0.2);
}

.logout-icon {
  font-size: 0.9rem;
}

/* Mobile menu toggle */
.mobile-menu-toggle {
  display: none;
  background: transparent;
  border: none;
  width: 30px;
  height: 24px;
  position: relative;
  cursor: pointer;
  padding: 0;
  z-index: 100;
}

.mobile-menu-toggle span {
  display: block;
  position: absolute;
  height: 3px;
  width: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  opacity: 1;
  left: 0;
  transform: rotate(0deg);
  transition: all var(--transition-fast);
}

.mobile-menu-toggle span:nth-child(1) {
  top: 0px;
}

.mobile-menu-toggle span:nth-child(2) {
  top: 10px;
}

.mobile-menu-toggle span:nth-child(3) {
  top: 20px;
}

/* Main Content Area */
.main-content {
  flex-grow: 1;
  padding: var(--space-xl) 0;
  width: 100%;
  overflow-x: hidden; /* Prevent horizontal overflow */
  box-sizing: border-box; /* Ensure padding is included in width */
  display: flex;
  justify-content: center; /* Center content horizontally */
}

.main-content .container {
  max-width: 100%; /* Ensure content doesn't exceed container width */
  margin: 0 auto; /* Center the container */
  box-sizing: border-box; /* Ensure padding is included in width */
  padding-left: var(--space-lg);
  padding-right: var(--space-lg); /* Explicit right padding to match left */
  width: 100%;
}

/* Footer Styling */
.app-footer {
  margin-top: auto;
  padding: var(--space-lg) 0;
  background-color: var(--color-accent);
  color: white;
  font-size: 0.875rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-content p {
  margin: 0;
}

.sponsor-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  text-align: center;
  border: 1px solid rgba(255,255,255,0.1);
}

.sponsor-badge span {
  font-size: 0.75rem;
  opacity: 0.8;
}

.sponsor-name {
  font-weight: 600;
  font-size: 0.9rem !important;
  opacity: 1 !important;
  background: linear-gradient(135deg, #ffffff, #f0f0f0);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.sponsor-name:hover {
  opacity: 0.9 !important;
  text-decoration: none;
}

.footer-links {
  display: flex;
  gap: var(--space-md);
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-link:hover {
  color: white;
  text-decoration: none;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .header-container {
    padding: var(--space-sm);
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .main-nav {
    position: fixed;
    top: 0;
    right: -100%;
    height: 100vh;
    width: 70%;
    max-width: 300px;
    background-color: white;
    flex-direction: column;
    padding: 80px var(--space-lg) var(--space-lg);
    box-shadow: var(--shadow-lg);
    transition: right var(--transition-normal);
    z-index: 90;
  }
  
  .main-nav.mobile-open {
    right: 0;
  }
  
  .nav-link {
    font-size: 1.1rem;
    padding: var(--space-md);
    width: 100%;
  }
  
  .main-content {
    padding: var(--space-md) 0;
  }
  
  .main-content .container {
    padding-left: var(--space-md);
    padding-right: var(--space-md); /* Explicit right padding to match left */
    max-width: 100%;
  }
  
  .footer-content {
    flex-direction: column;
    gap: var(--space-md);
    text-align: center;
  }
  
  .sponsor-badge {
    margin: var(--space-sm) 0;
    order: -1;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: var(--space-sm) 0;
  }
  
  .main-content .container {
    padding-left: var(--space-sm);
    padding-right: var(--space-sm); /* Explicit right padding to match left */
  }
  
  .footer-links {
    flex-direction: column;
    gap: var(--space-sm);
  }
}
</style>
