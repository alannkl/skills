package http

import (
	"github.com/go-chi/chi/v5"

	"fleetwise/fleetapi/internal/auth"
	"fleetwise/fleetapi/internal/http/handlers"
)

func Routes(h *handlers.Handlers) chi.Router {
	r := chi.NewRouter()

	r.Get("/healthz", h.Health)

	r.Group(func(r chi.Router) {
		r.Use(auth.Middleware)
		r.Get("/vehicles", h.ListVehicles)
		r.Get("/vehicles/{id}", h.GetVehicle)

		r.Group(func(r chi.Router) {
			r.Use(auth.RequireRole("admin"))
			r.Delete("/vehicles/{id}", h.DeleteVehicle)
		})
	})

	return r
}
