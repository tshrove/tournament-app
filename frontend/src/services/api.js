import axios from 'axios';

// Read the base URL from environment variables
// VITE_API_BASE_URL will be set during the Docker build process or locally via a .env file
// When set to '/', it uses relative URLs which work both in Docker and in browser
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'; // Fallback for local dev

console.log(`API Base URL: ${API_BASE_URL}`); // Log the URL being used

// Set axios defaults
// CORS headers should be set by the server, not the client
axios.defaults.withCredentials = false;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false
});

// Add request interceptor to handle requests
apiClient.interceptors.request.use(
  config => {
    // You can modify request config here if needed
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default {
  // Tournament management endpoints
  getTournaments() {
    return apiClient.get('/api/tournaments');
  },
  getTournament(tournamentId) {
    return apiClient.get(`/api/tournaments/${tournamentId}`);
  },
  createTournament(tournamentData) {
    return apiClient.post('/api/tournaments', tournamentData);
  },
  updateTournament(tournamentId, tournamentData) {
    return apiClient.put(`/api/tournaments/${tournamentId}`, tournamentData);
  },
  deleteTournament(tournamentId) {
    return apiClient.delete(`/api/tournaments/${tournamentId}`);
  },

  // Team endpoints with optional tournament filtering
  getRankings(params) {
    return apiClient.get('/rankings', { params });
  },
  addTeam(teamData) {
    return apiClient.post('/api/teams', teamData);
  },
  addGame(gameData) {
    return apiClient.post('/games', gameData);
  },
  getTeams(params) {
    return apiClient.get('/api/teams', { params });
  },
  getBracket(params) {
    return apiClient.get('/brackets', { params });
  },
  updateBracketMatch(matchId, scoreData) {
    return apiClient.patch(`/brackets/match/${matchId}`, scoreData);
  },
  generateBracket(tournamentId) {
    return apiClient.post('/brackets/generate', { tournament_id: tournamentId });
  },
  clearBracket(tournamentId) {
    return apiClient.post('/brackets/clear', { tournament_id: tournamentId });
  },
  deleteTeam(teamId) {
    return apiClient.delete(`/api/teams/${teamId}`);
  },
  // Schedule API methods
  getSchedule(params) {
    return apiClient.get('/api/schedule', { params });
  },
  getGameById(gameId) {
    return apiClient.get(`/api/schedule/${gameId}`);
  },
  createScheduledGame(gameData) {
    return apiClient.post('/api/schedule', gameData);
  },
  updateScheduledGame(gameId, gameData) {
    return apiClient.put(`/api/schedule/${gameId}`, gameData);
  },
  deleteScheduledGame(gameId) {
    return apiClient.delete(`/api/schedule/${gameId}`);
  },
  // Game scoring method
  updateGameScore(gameData) {
    return apiClient.put(`/api/schedule/${gameData.id}/score`, {
      team1_score: gameData.team1_score,
      team2_score: gameData.team2_score,
      status: gameData.status
    });
  },
  // Tournament settings methods
  getSettings(params) {
    return apiClient.get('/api/settings', { params });
  },
  updateSettings(settingsData) {
    return apiClient.put('/api/settings', settingsData);
  },
  resetTournament(tournamentId) {
    return apiClient.post('/api/reset', { tournament_id: tournamentId });
  }
}; 