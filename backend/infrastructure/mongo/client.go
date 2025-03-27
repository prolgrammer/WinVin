package mongo

import (
	"backend/internal/config"
	"context"
	"errors"
	"fmt"
	mongoDriver "go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
	"time"
)

type Client struct {
	Database *mongoDriver.Database
	client   *mongoDriver.Client
	cfg      config.Mongo
}

var (
	ErrNoChange = errors.New("no changes applied")
)

func NewClient(cfg config.Mongo) (*Client, error) {
	client := &Client{
		cfg: cfg,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	clientOptions := options.Client().ApplyURI("mongodb://localhost:27017")
	mongoClient, err := mongoDriver.Connect(ctx, clientOptions)
	if err != nil {
		return nil, fmt.Errorf("failed to create mongo client: %w", err)
	}

	err = mongoClient.Ping(ctx, readpref.Primary())
	if err != nil {
		return nil, fmt.Errorf("failed to ping mongo client: %w", err)
	}

	client.client = mongoClient
	client.Database = mongoClient.Database(cfg.Database)

	fmt.Printf("Successfully connected to MongoDB at %s\n", client.cfg.Host)
	return client, nil
}
