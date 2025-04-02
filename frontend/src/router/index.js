import { createRouter, createWebHistory } from 'vue-router'
// Import view components
import HomeView from '../views/HomeView.vue'
import RankingsView from '../views/RankingsView.vue'
import TeamManagementView from '../views/TeamManagementView.vue'
import BracketView from '../views/BracketView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import ManageScheduleView from '../views/ManageScheduleView.vue'
import AdminView from '../views/AdminView.vue'
import GameScoringView from '../views/GameScoringView.vue'
import TournamentSettingsView from '../views/TournamentSettingsView.vue'

const routes = [
  // Public routes
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { isPublic: true }
  },
  
  // Admin dashboard route
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { isAdmin: true }
  },
  
  // Admin functionality routes
  {
    path: '/rankings',
    name: 'Rankings',
    component: RankingsView,
    meta: { isAdmin: true }
  },
  {
    path: '/manage-teams',
    name: 'TeamManagement',
    component: TeamManagementView,
    meta: { isAdmin: true }
  },
  {
    path: '/bracket',
    name: 'Bracket',
    component: BracketView,
    meta: { isAdmin: true }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: ScheduleView,
    meta: { isAdmin: true }
  },
  {
    path: '/manage-schedule',
    name: 'ManageSchedule',
    component: ManageScheduleView,
    meta: { isAdmin: true }
  },
  {
    path: '/game-scoring',
    name: 'GameScoring',
    component: GameScoringView,
    meta: { isAdmin: true }
  },
  {
    path: '/tournament-settings',
    name: 'TournamentSettings',
    component: TournamentSettingsView,
    meta: { isAdmin: true }
  }
  // Add a placeholder route for now
  // {
  //   path: '/',
  //   name: 'Home',
  //   component: { template: '<div>Placeholder Home Page</div>' } // Temporary component
  // }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 