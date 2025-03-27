package requests

type NewSupportRequest struct {
	ClientID string `json:"client_id" binding:"required"`
	Message  string `json:"message" binding:"required"`
	Channel  string `json:"channel" binding:"required"`
}

type StoredSupportRequest struct {
	RequestID string `json:"request_id"`
	ClientID  string `json:"client_id"`
	Message   string `json:"message"`
	Channel   string `json:"channel"`
	Status    string `json:"status"`
}

type ClientRequestHistory struct {
	RequestID string `json:"request_id"`
	Message   string `json:"message"`
	Status    string `json:"status"`
	Operator  string `json:"operator,omitempty"`
}
