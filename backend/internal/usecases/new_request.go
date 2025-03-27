package usecases

import (
	"backend/internal/requests"
	"context"
	"github.com/google/uuid"
)

type NewRequestUseCase struct {
	repo  repositories.SupportRepository
	kafka kafka.Producer
}

func NewNewRequestUseCase(repo repositories.SupportRepository, kafka kafka.Producer) *NewRequestUseCase {
	return &NewRequestUseCase{
		repo:  repo,
		kafka: kafka,
	}
}

func (u *NewRequestUseCase) ProcessNewRequest(ctx context.Context, req requests.NewSupportRequest) (map[string]interface{}, error) {
	// Генерируем request_id
	requestID := uuid.New().String()

	// Создаем объект запроса с ID
	newReq := requests.StoredSupportRequest{
		RequestID: requestID,
		ClientID:  req.ClientID,
		Message:   req.Message,
		Channel:   req.Channel,
		Status:    "new",
	}

	// Сохраняем в БД
	err := u.repo.SaveNewRequest(ctx, newReq)
	if err != nil {
		return map[string]interface{}{
			"status":  "error",
			"message": "Database error",
		}, err
	}

	// Отправляем в Kafka
	err = u.kafka.Produce("raw_requests", newReq)
	if err != nil {
		return map[string]interface{}{
			"status":  "error",
			"message": "Kafka error",
		}, err
	}

	return map[string]interface{}{
		"status":     "success",
		"message":    "Request received and sent to processing",
		"request_id": requestID,
	}, nil
}
