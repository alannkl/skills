package httpx

import (
	"errors"
	"net/http"

	"fleetwise/fleetapi/internal/store"
)

func WriteError(w http.ResponseWriter, r *http.Request, err error) {
	var ve *ValidationError
	switch {
	case errors.Is(err, store.ErrNotFound):
		WriteJSON(w, http.StatusNotFound, map[string]string{"error": "not found"})
	case errors.As(err, &ve):
		WriteJSON(w, http.StatusUnprocessableEntity, map[string]any{"error": ve.Error(), "fields": ve.Fields})
	default:
		WriteJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal error"})
	}
}
