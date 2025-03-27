package usecases

import (
	"context"
)

type ClientHistoryUseCase struct {
	repo repositories.SupportRepository
}

func NewClientHistoryUseCase(repo repositories.SupportRepository) *ClientHistoryUseCase {
	return &ClientHistoryUseCase{repo: repo}
}

func (u *ClientHistoryUseCase) GetClientHistory(ctx context.Context, clientID string) (map[string]interface{}, error) {
	history, err := u.repo.GetHistory(ctx, clientID)
	if err != nil {
		return map[string]interface{}{
			"status":  "error",
			"message": "Database error",
		}, err
	}

	return map[string]interface{}{
		"status":    "success",
		"client_id": clientID,
		"history":   history,
	}, nil
}
