package http

import "github.com/gin-gonic/gin"

func AddGinError(ctx *gin.Context, err error) {
	ctx.Errors = append(ctx.Errors, &gin.Error{
		Err:  err,
		Type: gin.ErrorTypePublic,
		Meta: nil,
	})
}
