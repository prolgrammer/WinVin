package repositories

import (
	"backend/internal/models"
	"context"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type SupportRepository struct {
	collection *mongo.Collection
}

func NewSupportRepository(db *mongo.Database) *SupportRepository {
	return &SupportRepository{
		collection: db.Collection("support_requests"),
	}
}

// Сохранение нового запроса
func (r *SupportRepository) SaveNewRequest(ctx context.Context, request models.SupportRequest) error {
	_, err := r.collection.InsertOne(ctx, request)
	return err
}

// Получение истории запросов клиента
func (r *SupportRepository) GetHistory(ctx context.Context, clientID string) ([]models.SupportRequest, error) {
	filter := bson.M{"client_id": clientID}
	cursor, err := r.collection.Find(ctx, filter)
	if err != nil {
		return nil, err
	}

	var history []models.SupportRequest
	if err = cursor.All(ctx, &history); err != nil {
		return nil, err
	}

	return history, nil
}

// Добавление сообщения в историю чата
func (r *SupportRepository) AddMessageToHistory(ctx context.Context, requestID string, message models.MessageHistory) error {
	filter := bson.M{"request_id": requestID}
	update := bson.M{"$push": bson.M{"history": message}}
	_, err := r.collection.UpdateOne(ctx, filter, update)
	return err
}

// Назначение оператора запросу
func (r *SupportRepository) AssignOperator(ctx context.Context, requestID string, operator string) error {
	filter := bson.M{"request_id": requestID}
	update := bson.M{"$set": bson.M{"operator": operator}}
	_, err := r.collection.UpdateOne(ctx, filter, update)
	return err
}
