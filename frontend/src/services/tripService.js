import apiClient from "./apiClient";

export const tripService = {
  /* ---- Trips CRUD ---- */
  getTrips: (params = {}) =>
    apiClient.get("/trips", { params }).then((r) => r.data),

  createTrip: (payload) =>
    apiClient.post("/trips", payload).then((r) => r.data),

  getTrip: (id) =>
    apiClient.get(`/trips/${id}`).then((r) => r.data),

  getPublicTrip: (id) =>
    apiClient.get(`/trips/public/${id}`).then((r) => r.data),

  updateTrip: (id, payload) =>
    apiClient.put(`/trips/${id}`, payload).then((r) => r.data),

  deleteTrip: (id) =>
    apiClient.delete(`/trips/${id}`).then((r) => r.data),

  duplicateTrip: (id) =>
    apiClient.post(`/trips/${id}/duplicate`).then((r) => r.data),

  /* ---- Stops ---- */
  addStop: (tripId, payload) =>
    apiClient.post(`/trips/${tripId}/stops`, payload).then((r) => r.data),

  updateStop: (tripId, stopId, payload) =>
    apiClient.put(`/trips/${tripId}/stops/${stopId}`, payload).then((r) => r.data),

  deleteStop: (tripId, stopId) =>
    apiClient.delete(`/trips/${tripId}/stops/${stopId}`).then((r) => r.data),

  reorderStops: (tripId, items) =>
    apiClient.put(`/trips/${tripId}/stops/reorder`, items).then((r) => r.data),

  /* ---- Budget ---- */
  getTripBudget: (id) =>
    apiClient.get(`/trips/${id}/budget`).then((r) => r.data),

  updateTripBudget: (id, payload) =>
    apiClient.put(`/trips/${id}/budget`, payload).then((r) => r.data),

  /* ---- Expenses ---- */
  getExpenses: (tripId) =>
    apiClient.get(`/trips/${tripId}/expenses`).then((r) => r.data),

  addExpense: (tripId, payload) =>
    apiClient.post(`/trips/${tripId}/expenses`, payload).then((r) => r.data),

  updateExpense: (expenseId, payload) =>
    apiClient.put(`/expenses/${expenseId}`, payload).then((r) => r.data),

  deleteExpense: (expenseId) =>
    apiClient.delete(`/expenses/${expenseId}`).then((r) => r.data),

  /* ---- Itinerary items (schedule activities to stops) ---- */
  getItinerary: (tripId) =>
    apiClient.get(`/trips/${tripId}/itinerary`).then((r) => r.data),

  addItineraryItem: (stopId, payload) =>
    apiClient.post(`/stops/${stopId}/items`, payload).then((r) => r.data),

  generateAIItinerary: (tripId, payload) =>
    apiClient.post(`/trips/${tripId}/generate-itinerary`, payload).then((r) => r.data),

  updateItineraryItem: (itemId, payload) =>
    apiClient.put(`/itinerary-items/${itemId}`, payload).then((r) => r.data),

  deleteItineraryItem: (itemId) =>
    apiClient.delete(`/itinerary-items/${itemId}`).then((r) => r.data),

  getConflicts: (tripId) =>
    apiClient.get(`/trips/${tripId}/conflicts`).then((r) => r.data),

  /* ---- Map Route ---- */
  getMapRoute: (tripId) =>
    apiClient.get(`/trips/${tripId}/map-route`).then((r) => r.data),

  /* ---- Sharing ---- */
  generateShareLink: (tripId, payload = {}) =>
    apiClient.post(`/trips/${tripId}/share`, payload).then((r) => r.data),

  getSharedTrip: (token) =>
    apiClient.get(`/shared/${token}`).then((r) => r.data),

  copySharedTrip: (token) =>
    apiClient.post(`/shared/${token}/copy`).then((r) => r.data),

  /* ---- Collaborators ---- */
  getCollaborators: (tripId) =>
    apiClient.get(`/trips/${tripId}/collaborators`).then((r) => r.data),

  addCollaborator: (tripId, payload) =>
    apiClient.post(`/trips/${tripId}/collaborators`, payload).then((r) => r.data),

  removeCollaborator: (tripId, userId) =>
    apiClient.delete(`/trips/${tripId}/collaborators/${userId}`).then((r) => r.data),

  /* ---- Stays ---- */
  getTripStays: (tripId) =>
    apiClient.get(`/trips/${tripId}/stays`).then((r) => r.data),

  selectStay: (tripId, payload) =>
    apiClient.post(`/trips/${tripId}/stays`, payload).then((r) => r.data),

  /* ---- Budget Optimization ---- */
  recalculateBudget: (tripId) =>
    apiClient.post(`/trips/${tripId}/budget/recalculate`).then((r) => r.data),

  optimizeBudget: (tripId) =>
    apiClient.post(`/trips/${tripId}/budget/optimize`).then((r) => r.data),

  applyOptimization: (tripId, recId) =>
    apiClient.post(`/trips/${tripId}/budget/optimize/${recId}/apply`).then((r) => r.data),

  /* ---- Indian Multi-Modal Transit & Routes ---- */
  getTripTransit: (tripId) =>
    apiClient.get(`/trips/${tripId}/transit`).then((r) => r.data),

  selectTransitOption: (tripId, legId, selectedOptionId) =>
    apiClient.patch(`/trips/${tripId}/transit/${legId}`, { selected_option_id: selectedOptionId }).then((r) => r.data),

  /* ---- Live DuckDuckGo Food & Stays Recommendations ---- */
  getLiveFood: (city, budgetTier = 'mid') =>
    apiClient.get('/places/live-food', { params: { city, budget_tier: budgetTier } }).then((r) => r.data),

  getLiveStays: (city, budgetTier = 'mid') =>
    apiClient.get('/places/live-stays', { params: { city, budget_tier: budgetTier } }).then((r) => r.data),
};

