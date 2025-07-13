package router

import (
	"github.com/DreamZhongJu/next-shop/controllers"
	"github.com/DreamZhongJu/next-shop/middleware" // 新增中间件导入
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func Router() *gin.Engine {
	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://192.168.1.15:3000", "http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// 添加日志和恢复中间件
	r.Use(middleware.GinLogger(), middleware.GinRecovery(true))

	user := r.Group("/api/v1")
	{
		user.POST("/login", controllers.UserControllers{}.Login)
		user.POST("/sign", controllers.UserControllers{}.Sign)

		user.POST("/search", controllers.UserSearch{}.Search)
		user.GET("/search/all", controllers.UserSearch{}.SearchAll)
		user.GET("/search/detail/:id", controllers.UserSearch{}.GetProductDetail)

		// 嵌套购物车
		cart := user.Group("/cart")
		cart.Use(middleware.AuthMiddleware())
		{
			cart.POST("/add", controllers.CartController{}.Add)
			cart.PUT("/update", controllers.CartController{}.Update)
			cart.POST("/delete", controllers.CartController{}.Delete)
			cart.GET("/list/:user_id", controllers.CartController{}.List)
		}

		user.GET("/user/count", controllers.UserControllers{}.Count)

		// TODO: 增加商品图片上传功能
		// - 后端支持文件上传接口，可选本地存储或云存储
		// - 前端表单支持图片上传与预览效果
		// - 数据库记录图片 URL 字段

		// TODO: 添加单元测试与接口测试
		// - 后端：使用 Go Test 对控制器与模型方法进行测试
		// - 前端：使用 Jest 或 Playwright 测试页面组件与用户交互流程

		// TODO: 接入全局状态管理
		// - 使用 Zustand 或 Redux Toolkit 管理登录状态与购物车状态
		// - 提高组件间状态同步效率，避免 prop drilling

		// TODO: 项目部署与优化
		// - 使用 Docker 制作前后端镜像
		// - 使用 Nginx 配置反向代理与静态资源服务
		// - 配置 CI/CD 流水线，例如 GitHub Actions

		// 管理员用户管理
		admin := user.Group("/admin")
		admin.Use(middleware.AdminMiddleware()) // 需要添加管理员中间件
		{
			admin.GET("/users", (&controllers.AdminUserController{}).GetUsers)
			admin.PUT("/users/:id", (&controllers.AdminUserController{}).UpdateUser)
			admin.DELETE("/users/:id", (&controllers.AdminUserController{}).DeleteUser)
			// Dashboard endpoint
			user.GET("/admin/dashboard", controllers.DashboardController{}.GetDashboardData)
		}

		// // 嵌套收藏
		// favorite := user.Group("/favorite")
		// {
		// 	favorite.POST("/add", controllers.FavoriteController{}.Add)
		// 	favorite.DELETE("/remove", controllers.FavoriteController{}.Remove)
		// 	favorite.GET("/list/:user_id", controllers.FavoriteController{}.List)
		// }
	}

	return r
}
