package middleware

import (
	"fmt"
	"strings"

	"github.com/DreamZhongJu/next-shop/utils"
	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		fmt.Println("Authorization Header:", authHeader)
		if authHeader == "" {
			c.AbortWithStatusJSON(401, gin.H{"msg": "请求未携带token"})
			return
		}

		token := strings.TrimPrefix(authHeader, "Bearer ")
		fmt.Println("Extracted Token:", token)

		// fmt.Println("收到的Token:", token)
		claims, err := utils.ParseToken(token)
		if err != nil {
			c.AbortWithStatusJSON(401, gin.H{"msg": "Token无效或已过期"})
			return
		}
		// fmt.Println("解析成功，user_id:", claims.UserID)

		// 保存用户信息到上下文
		c.Set("user_id", claims.UserID)
		c.Set("role", claims.Role)

		c.Next()

	}
}

func AdminMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(401, gin.H{"msg": "请求未携带token"})
			return
		}

		claims, err := utils.ParseToken(authHeader) // 直接传完整的 Authorization
		if err != nil {
			c.AbortWithStatusJSON(401, gin.H{"msg": "Token无效或已过期: " + err.Error()})
			return
		}

		if claims.Role != "admin" {
			c.AbortWithStatusJSON(403, gin.H{"msg": "无管理员权限"})
			return
		}

		c.Set("user_id", claims.UserID)
		c.Next()
	}
}
