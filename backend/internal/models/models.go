package models

import "time"

// История общения с клиентом
type MessageHistory struct {
	Timestamp time.Time `json:"timestamp" bson:"timestamp"`
	Message   string    `json:"message" bson:"message"`
	From      string    `json:"from" bson:"from"`
}

// Структура запроса в техподдержку
type SupportRequest struct {
	RequestID string           `json:"request_id" bson:"request_id"`
	ClientID  string           `json:"client_id" bson:"client_id"`
	Text      string           `json:"text" bson:"text"`
	Topic     string           `json:"topic" bson:"topic"`
	Priority  string           `json:"priority" bson:"priority"`
	Operator  string           `json:"operator,omitempty" bson:"operator,omitempty"`
	History   []MessageHistory `json:"history" bson:"history"`
}
