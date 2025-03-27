package http

import (
	"backend/internal/requests"
	"backend/internal/usecases"
	"github.com/gin-gonic/gin"
	"net/http"
)

type newRequestController struct {
	useCase usecases.NewRequestUseCase
}

func NewNewRequestController(
	handler *gin.Engine,
	useCase usecases.NewRequestUseCase,
) {

	u := &newRequestController{
		useCase: useCase,
	}

	handler.POST("/support/request", u.HandleNewRequest)
}

func (u *newRequestController) HandleNewRequest(c *gin.Context) {
	var req requests.NewSupportRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		AddGinError(c, ErrWrongDataFormat)
		return
	}

	response, err := u.useCase.ProcessNewRequest(c, req)
	if err != nil {
		AddGinError(c, err)
		return
	}

	c.JSON(http.StatusOK, response)
}
