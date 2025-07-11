package router

import (
	"github.com/DreamZhongJu/next-shop/controllers"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func Router() *gin.Engine {
	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://192.168.1.15:3000", "http://localhost:3000"}, // 允许本地开发环境
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	user := r.Group("/api/v1")
	{
		user.POST("/login", controllers.UserControllers{}.Login)
		user.POST("/sign", controllers.UserControllers{}.Sign)

		user.POST("/search", controllers.UserSearch{}.Search)
		user.GET("/search/all", controllers.UserSearch{}.SearchAll)
		user.GET("/search/detail/:id", controllers.UserSearch{}.GetProductDetail)
	}

	return r
}
