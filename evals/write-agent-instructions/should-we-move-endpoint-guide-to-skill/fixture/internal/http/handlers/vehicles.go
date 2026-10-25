package handlers

import (
	"net/http"

	"github.com/go-chi/chi/v5"

	"fleetwise/fleetapi/internal/httpx"
)

func (h *Handlers) GetVehicle(w http.ResponseWriter, r *http.Request) {
	v, err := h.Store.GetVehicle(r.Context(), chi.URLParam(r, "id"))
	if err != nil {
		httpx.WriteError(w, r, err)
		return
	}
	httpx.WriteJSON(w, http.StatusOK, v)
}

func (h *Handlers) ListVehicles(w http.ResponseWriter, r *http.Request) {
	page, err := httpx.ParsePage(r)
	if err != nil {
		httpx.WriteError(w, r, err)
		return
	}
	vs, err := h.Store.ListVehicles(r.Context(), page.Limit, page.Offset)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	httpx.WriteJSON(w, http.StatusOK, httpx.NewPage(vs, page))
}

func (h *Handlers) DeleteVehicle(w http.ResponseWriter, r *http.Request) {
	if err := h.Store.DeleteVehicle(r.Context(), chi.URLParam(r, "id")); err != nil {
		httpx.WriteError(w, r, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
