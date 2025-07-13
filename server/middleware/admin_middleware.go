package middleware

import (
	"github.com/gin-gonic/gin"
)

func AdminMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement actual admin check logic
		// For now, just allow all requests
		c.Next()
	}
}
