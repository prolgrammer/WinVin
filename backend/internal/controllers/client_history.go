package http

import (
	"backend/internal/usecases"
	"github.com/gin-gonic/gin"
	"net/http"
)

type clientHistoryController struct {
	useCase usecases.ClientHistoryUseCase
}

func NewClientHistoryController(
	handler *gin.Engine,
	useCase usecases.ClientHistoryUseCase,
) {

	u := &clientHistoryController{
		useCase: useCase,
	}

	handler.GET("/support/history", u.GetClientHistory)
}

func (u *clientHistoryController) GetClientHistory(c *gin.Context) {
	clientID := "1"

	history, err := u.useCase.GetClientHistory(c, clientID)
	if err != nil {
		AddGinError(c, err)
		return
	}

	c.JSON(http.StatusOK, history)
}
