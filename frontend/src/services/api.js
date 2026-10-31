/**
 * API Service for Backend Communication
 * Connects React Frontend to FastAPI Recommender Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function getAuthHeader() {
  const token = localStorage.getItem('cinematch_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      let errMsg = `Request failed (${res.status})`;
      try {
        const errData = await res.json();
        errMsg = errData.detail || errMsg;
      } catch (e) {
        // silent parse error
      }
      throw new Error(errMsg);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Authentication & Users
  auth: {
    login: (username_or_email, password) =>
      request('/users/login', {
        method: 'POST',
        body: JSON.stringify({ username_or_email, password }),
      }),
    register: (username, email, password) =>
      request('/users/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      }),
    getMe: () => request('/auth/me'),
  },

  // Movies & Search
  movies: {
    list: (params = {}) => {
      const q = new URLSearchParams();
      if (params.q) q.append('q', params.q);
      if (params.genre) q.append('genre', params.genre);
      if (params.page) q.append('page', params.page);
      if (params.limit) q.append('limit', params.limit || 20);
      return request(`/movies?${q.toString()}`);
    },
    popular: (params = {}) => {
      const q = new URLSearchParams();
      if (params.genre) q.append('genre', params.genre);
      if (params.page) q.append('page', params.page);
      if (params.limit) q.append('limit', params.limit || 20);
      return request(`/movies/popular?${q.toString()}`);
    },
    search: (params = {}) => {
      const q = new URLSearchParams();
      if (params.query || params.q) q.append('query', params.query || params.q);
      if (params.genre) q.append('genre', params.genre);
      if (params.page) q.append('page', params.page);
      if (params.limit) q.append('limit', params.limit || 20);
      return request(`/movies/search?${q.toString()}`);
    },
    get: (movieId) => request(`/movies/${movieId}`),
    similar: (movieId, limit = 8) => request(`/movies/${movieId}/similar?limit=${limit}`),
    genres: () => request('/movies/genres'),
  },

  // Recommendations (Cold-Start & Personalized Collaborative Filtering)
  recommendations: {
    getMine: (params = {}) => {
      const q = new URLSearchParams();
      if (params.genre) q.append('genre', params.genre);
      if (params.limit) q.append('limit', params.limit || 20);
      return request(`/recommendations/me?${q.toString()}`);
    },
    getColdStart: (params = {}) => {
      const q = new URLSearchParams();
      if (params.genre) q.append('genre', params.genre);
      if (params.limit) q.append('limit', params.limit || 20);
      return request(`/recommendations?${q.toString()}`);
    },
    getByUserId: (userId, params = {}) => {
      const q = new URLSearchParams();
      if (params.genre) q.append('genre', params.genre);
      if (params.limit) q.append('limit', params.limit || 20);
      return request(`/recommendations/${userId}?${q.toString()}`);
    },
    seedDemo: (taste_profile) =>
      request('/recommendations/demo-seed', {
        method: 'POST',
        body: JSON.stringify({ taste_profile }),
      }),
  },

  // Interactions (Ratings, Likes/Favorites, Watch History)
  interactions: {
    rate: (movie_id, rating, user_id = null) =>
      request('/interactions/rating', {
        method: 'POST',
        body: JSON.stringify({ movie_id, rating, ...(user_id ? { user_id } : {}) }),
      }),
    deleteRating: (movie_id) =>
      request(`/interactions/rate/${movie_id}`, {
        method: 'DELETE',
      }),
    getRatings: () => request('/interactions/ratings'),
    toggleFavorite: (movie_id, user_id = null) =>
      request('/interactions/like', {
        method: 'POST',
        body: JSON.stringify({ movie_id, ...(user_id ? { user_id } : {}) }),
      }),
    getFavorites: () => request('/interactions/favorites'),
    recordWatch: (movie_id, user_id = null) =>
      request('/interactions/watch', {
        method: 'POST',
        body: JSON.stringify({ movie_id, ...(user_id ? { user_id } : {}) }),
      }),
    getHistory: () => request('/interactions/history'),
    getUserHistory: (userId) => request(`/users/${userId}/history`),
    getSummary: () => request('/interactions/summary'),
  },
};
