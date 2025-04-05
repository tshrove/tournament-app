<script setup>
import { ref, provide, computed } from 'vue';
import { useRoute } from 'vue-router';
import ToastNotification from './components/ToastNotification.vue'; // Import the component
import auth from './store/auth';
import currentTournament from './store/current-tournament';

// Notification State
const notification = ref({
  visible: false,
  message: '',
  type: 'success' // success, error, info
});

// Get current route
const route = useRoute();

// Computed property to check if we're on the tournaments list page
const isOnTournamentsList = computed(() => route.name === 'Tournaments');

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
          <h1>🚀 Rocketpad</h1>
        </div>
        
        <!-- Mobile menu toggle -->
        <button class="mobile-menu-toggle" @click="toggleMobileMenu" aria-label="Toggle menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
        
        <nav class="main-nav" :class="{ 'mobile-open': mobileMenuOpen }">
          <router-link to="/" class="nav-link" @click="mobileMenuOpen = false">Home</router-link>
          <!-- Admin button only appears when a tournament is selected and not on tournaments list -->
          <router-link 
            v-if="currentTournament.hasSelectedTournament() && !isOnTournamentsList" 
            to="/admin" 
            class="nav-link admin-link" 
            @click="mobileMenuOpen = false"
          >
            <span class="admin-icon">⚙️</span> Admin
          </router-link>
          <!-- Tournament Admin button only appears on the tournaments list page -->
          <router-link 
            v-if="isOnTournamentsList" 
            to="/tournament-admin" 
            class="nav-link admin-link" 
            @click="mobileMenuOpen = false"
          >
            <span class="admin-icon">🏆</span> Tournament Admin
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
          <p>&copy; {{ new Date().getFullYear() }} Rocketpad</p>
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
  padding: 0; /* Remove padding, handle in container */
  border-bottom: 1px solid var(--color-border); /* Add subtle border */
  transition: box-shadow var(--transition-normal), background-color var(--transition-normal);
}

/* Remove header hover effect */
/* .app-header:hover { */
/*  box-shadow: var(--shadow-md); */
/* } */

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm) var(--space-lg); /* Consistent padding */
  min-height: 60px; /* Ensure minimum header height */
}

.logo h1 {
  margin: 0;
  font-size: 1.6rem; /* Slightly adjusted size */
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%); /* Adjusted gradient */
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  font-weight: 800; /* Match h1 weight from global styles */
  letter-spacing: -0.03em; /* Slightly tighter */
}

.main-nav {
  display: flex;
  align-items: center; /* Align items vertically */
  gap: var(--space-sm); /* Reduced gap slightly */
}

.nav-link {
  position: relative;
  color: var(--color-text-light);
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  text-decoration: none;
  transition: color var(--transition-fast), background-color var(--transition-fast);
  border-radius: var(--radius-sm);
  border: none; /* Ensure no default border */
  background-color: transparent; /* Ensure transparent background */
  cursor: pointer; /* Ensure pointer cursor for buttons */
  font-family: inherit; /* Inherit font */
  font-size: 0.95rem; /* Slightly smaller nav links */
}

/* Remove underline effect */
/* .nav-link::after { */
/*  content: ''; */
/*  position: absolute; */
/*  width: 0; */
/*  height: 3px; */
/*  bottom: -3px; */
/*  left: 0; */
/*  background: linear-gradient(to right, var(--color-primary), var(--color-secondary)); */
/*  transition: width var(--transition-normal); */
/*  border-radius: var(--radius-full); */
/* } */

.nav-link:hover {
  color: var(--color-primary-dark);
  background-color: var(--color-background-alt); /* Subtle background on hover */
  text-decoration: none;
}

/* Remove hover underline width */
/* .nav-link:hover::after { */
/*  width: 100%; */
/* } */

.nav-link.router-link-active {
  color: var(--color-primary-dark);
  font-weight: 600;
  background-color: rgba(90, 103, 216, 0.1); /* Use primary color with alpha */
}

/* Remove active underline width */
/* .nav-link.router-link-active::after { */
/*  width: 100%; */
/* } */

.admin-link,
.logout-button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md); /* Consistent padding */
  border-radius: var(--radius-md);
  font-size: 0.9rem;
}

.admin-link {
  background-color: rgba(90, 103, 216, 0.1);
  color: var(--color-primary-dark);
}

.admin-link:hover {
  background-color: rgba(90, 103, 216, 0.2);
  color: var(--color-primary-dark);
}

.admin-icon {
  font-size: 1rem;
}

.logout-button {
  background-color: rgba(244, 63, 94, 0.1);
  color: var(--color-danger);
}

.logout-button:hover {
  background-color: rgba(244, 63, 94, 0.2);
  color: var(--color-danger);
}

.logout-icon {
  font-size: 1rem;
}

/* Mobile menu toggle - Enhanced animation */
.mobile-menu-toggle {
  display: none;
  background: transparent;
  border: none;
  width: 24px; /* Slightly smaller */
  height: 24px;
  position: relative;
  cursor: pointer;
  padding: 0;
  z-index: var(--z-modal); /* Ensure it's above nav */
}

.mobile-menu-toggle span {
  display: block;
  position: absolute;
  height: 2px; /* Thinner lines */
  width: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  opacity: 1;
  left: 0;
  transform-origin: center center;
  transition: transform var(--transition-normal), top var(--transition-normal), opacity var(--transition-normal);
}

.mobile-menu-toggle span:nth-child(1) {
  top: 4px;
}

.mobile-menu-toggle span:nth-child(2) {
  top: 11px; /* Centered */
}

.mobile-menu-toggle span:nth-child(3) {
  top: 18px;
}

.mobile-open .mobile-menu-toggle span:nth-child(1) {
  transform: rotate(45deg);
  top: 11px;
}

.mobile-open .mobile-menu-toggle span:nth-child(2) {
  opacity: 0;
  transform: translateX(-10px);
}

.mobile-open .mobile-menu-toggle span:nth-child(3) {
  transform: rotate(-45deg);
  top: 11px;
}

/* Main Content Area (minor tweaks if needed) */
.main-content {
  flex-grow: 1;
  padding: var(--space-xl) 0;
  width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
}

.main-content .container {
  max-width: 1280px; /* Use consistent max-width */
  margin: 0 auto;
  box-sizing: border-box;
  padding-left: var(--space-lg);
  padding-right: var(--space-lg);
  width: 100%;
}

/* Footer Styling - Simplified */
.app-footer {
  margin-top: auto;
  padding: var(--space-lg) 0;
  background-color: var(--color-background-alt); /* Use alt background */
  color: var(--color-text-light);
  font-size: 0.875rem;
  border-top: 1px solid var(--color-border);
}

.footer-content {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping */
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md); /* Add gap for spacing */
}

.footer-content p {
  margin: 0;
  flex-shrink: 0; /* Prevent copyright from shrinking too much */
}

.sponsor-badge {
  display: flex;
  align-items: center; /* Align items horizontally */
  gap: var(--space-sm);
  background: none; /* Remove background */
  padding: 0;
  border-radius: 0;
  text-align: left;
  border: none; /* Remove border */
  order: 3; /* Move to end on wrap */
  flex-basis: 100%; /* Take full width when wrapped */
  justify-content: center; /* Center when wrapped */
}

.sponsor-badge span {
  font-size: 0.8rem;
  opacity: 1;
  color: var(--color-text-lighter); /* Use lighter text */
}

.sponsor-name {
  font-weight: 500;
  font-size: 0.85rem !important;
  opacity: 1 !important;
  background: none;
  background-clip: unset;
  -webkit-background-clip: unset;
  color: var(--color-primary); /* Use primary color */
  text-decoration: none;
  transition: color var(--transition-fast);
}

.sponsor-name:hover {
  color: var(--color-primary-dark); /* Darken on hover */
  text-decoration: underline;
}

.footer-links {
  display: flex;
  gap: var(--space-md);
  order: 2; /* Default order */
}

.footer-link {
  color: var(--color-text-light);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-link:hover {
  color: var(--color-primary);
  text-decoration: underline;
}

/* Responsive Adjustments for App.vue */
@media (max-width: 768px) {
  .header-container {
    padding: var(--space-sm) var(--space-md); /* Adjust padding */
  }

  .mobile-menu-toggle {
    display: block;
  }

  .main-nav {
    position: fixed;
    top: 0;
    right: -100%; /* Start off-screen */
    height: 100vh;
    width: 280px; /* Fixed width */
    max-width: 80%;
    background-color: var(--color-background-card); /* Use card background */
    flex-direction: column;
    align-items: flex-start; /* Align items left */
    padding: 80px var(--space-lg) var(--space-lg);
    box-shadow: var(--shadow-lg);
    transition: transform var(--transition-normal); /* Use transform for transition */
    transform: translateX(100%); /* Off-screen state */
    z-index: calc(var(--z-modal) - 10); /* Below toggle */
    border-left: 1px solid var(--color-border);
  }

  .main-nav.mobile-open {
    transform: translateX(0); /* Slide in */
    right: auto; /* Reset right */
  }

  .nav-link {
    font-size: 1.1rem;
    padding: var(--space-md) 0; /* Adjust padding */
    width: 100%;
    border-radius: 0;
    color: var(--color-text);
  }
  
  .nav-link:hover {
      background-color: var(--color-background-alt);
  }
  
  .nav-link.router-link-active {
      color: var(--color-primary-dark);
      background-color: transparent; /* Remove background for active in mobile */
      font-weight: 700;
  }
  
  .admin-link,
  .logout-button {
      width: 100%;
      background-color: transparent;
      padding: var(--space-md) 0;
      border-radius: 0;
      font-size: 1.1rem;
  }
  
  .admin-link {
      color: var(--color-primary);
  }
  .admin-link:hover {
      color: var(--color-primary-dark);
      background-color: var(--color-background-alt);
  }
  
  .logout-button {
      color: var(--color-danger);
  }
  .logout-button:hover {
      color: #c81e1e;
      background-color: var(--color-background-alt);
  }


  .main-content {
    padding: var(--space-lg) 0; /* Adjust padding */
  }

  .main-content .container {
    padding-left: var(--space-md);
    padding-right: var(--space-md);
    max-width: 100%;
  }

  .footer-content {
    flex-direction: column;
    gap: var(--space-lg); /* Increased gap */
    text-align: center;
  }

  .sponsor-badge {
    order: 3; /* Keep at end */
    flex-basis: auto; /* Reset basis */
    justify-content: center;
    margin-top: var(--space-sm); /* Add some margin */
  }
  
  .footer-links {
      order: 2;
      margin-top: var(--space-sm);
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: var(--space-md) 0; /* Further adjust padding */
  }

  .main-content .container {
    padding-left: var(--space-sm);
    padding-right: var(--space-sm);
  }

  .footer-links {
    flex-direction: column;
    gap: var(--space-xs);
  }
  
  .logo h1 {
    font-size: 1.4rem;
  }
}
</style>
