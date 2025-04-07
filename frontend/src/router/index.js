import { createRouter, createWebHistory } from 'vue-router'
// Import view components
import HomeView from '../views/HomeView.vue'
import TeamManagementView from '../views/TeamManagementView.vue'
import BracketView from '../views/BracketView.vue'
import PublicBracketView from '../views/PublicBracketView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import ManageScheduleView from '../views/ManageScheduleView.vue'
import AdminView from '../views/AdminView.vue'
import GameScoringView from '../views/GameScoringView.vue'
import TournamentSettingsView from '../views/TournamentSettingsView.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import TournamentsView from '../views/TournamentsView.vue'
import ManageTournamentView from '../views/ManageTournamentView.vue'
import TournamentAdminView from '../views/TournamentAdminView.vue'
import TournamentAdminLoginView from '../views/TournamentAdminLoginView.vue'
import auth from '../store/auth'
import tournamentAdminAuth from '../store/tournament-admin-auth'

const routes = [
  // Public routes
  {
    path: '/',
    name: 'Tournaments',
    component: TournamentsView,
    meta: { isPublic: true }
  },

  // Single tournament view (previously the home view)
  {
    path: '/tournament/:id',
    name: 'TournamentHome',
    component: HomeView,
    meta: { isPublic: true },
    props: true
  },
  
  // Tournament management routes
  {
    path: '/tournament-admin-login',
    name: 'TournamentAdminLogin',
    component: TournamentAdminLoginView,
    meta: { isPublic: true }
  },
  {
    path: '/tournament-admin',
    name: 'TournamentAdmin',
    component: TournamentAdminView,
    meta: { isTournamentAdmin: true }
  },
  {
    path: '/tournament/create',
    name: 'CreateTournament',
    component: ManageTournamentView,
    meta: { isTournamentAdmin: true }
  },
  {
    path: '/tournament/:id/edit',
    name: 'ManageTournament',
    component: ManageTournamentView,
    meta: { isTournamentAdmin: true },
    props: true
  },
  
  // Tournament-specific admin login
  {
    path: '/admin-login',
    name: 'AdminLogin',
    component: AdminLoginView,
    meta: { isPublic: true }
  },
  
  // Tournament-specific admin dashboard
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { isAdmin: true }
  },
  
  // Admin functionality routes - tournament specific
  {
    path: '/tournament/:id/manage-teams',
    name: 'TeamManagement',
    component: TeamManagementView,
    meta: { isAdmin: true },
    props: true
  },
  {
    path: '/tournament/:id/bracket',
    name: 'Bracket',
    component: BracketView,
    meta: { isAdmin: true },
    props: true
  },
  {
    path: '/tournament/:id/schedule',
    name: 'Schedule',
    component: ScheduleView,
    meta: { isAdmin: true },
    props: true
  },
  {
    path: '/tournament/:id/manage-schedule',
    name: 'ManageSchedule',
    component: ManageScheduleView,
    meta: { isAdmin: true },
    props: true
  },
  {
    path: '/tournament/:id/game-scoring',
    name: 'GameScoring',
    component: GameScoringView,
    meta: { isAdmin: true },
    props: true
  },
  {
    path: '/tournament/:id/settings',
    name: 'TournamentSettings',
    component: TournamentSettingsView,
    meta: { isAdmin: true },
    props: true
  },
  {
    path: '/tournament/:id/brackets',
    name: 'PublicBrackets',
    component: PublicBracketView,
    meta: { isPublic: true },
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Check for routes requiring tournament admin access
  if (to.matched.some(record => record.meta.isTournamentAdmin)) {
    // If not authenticated as tournament admin, redirect to tournament admin login
    if (!tournamentAdminAuth.state.isAuthenticated) {
      next({
        path: '/tournament-admin-login',
        query: { redirect: to.fullPath }
      });
    } else {
      // User is authenticated as tournament admin, allow access
      next();
    }
  } 
  // Check for routes requiring regular admin access (tournament-specific)
  else if (to.matched.some(record => record.meta.isAdmin)) {
    // If not authenticated, redirect to login page with return URL
    if (!auth.state.isAuthenticated) {
      next({
        path: '/admin-login',
        query: { redirect: to.fullPath }
      });
    } else {
      // User is authenticated, allow access
      next();
    }
  } else {
    // Public route, allow access
    next();
  }
});

export default router 