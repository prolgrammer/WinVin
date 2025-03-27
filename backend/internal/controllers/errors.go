package http

import "errors"

var (
	ErrAuthenticated   = errors.New("authentication is required for this action")
	ErrWrongDataFormat = errors.New("wrong data format")
)
