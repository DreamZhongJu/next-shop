# Next-Shop 电商平台

一个基于Next.js和Go的全栈电商平台项目，提供完整的电商功能包括用户认证、商品管理、购物车和订单处理等。

## 功能特性

- **用户系统**：注册、登录、JWT认证
- **商品管理**：商品展示、分类、搜索
- **购物车系统**：添加商品、修改数量、结算
- **后台管理**：商品管理、用户管理
- **实时聊天**：集成OpenAI的客服聊天功能
- **响应式设计**：适配各种设备屏幕

## 技术栈

### 前端 (client/shop)
- **框架**: Next.js 15.3.5 (with Turbopack)
- **UI库**: React 19
- **样式**: TailwindCSS
- **状态管理**: React Context
- **构建工具**: TypeScript 5
- **其他**:
  - React Icons 5.5.0
  - OpenAI SDK 5.8.3 (用于聊天功能)

### 后端 (server)
- **语言**: Go 1.23.2
- **Web框架**: Gin
- **数据库**: MySQL + GORM
- **认证**: JWT
- **日志**: Zap
- **其他**:
  - CORS中间件
  - 数据验证器

## 安装与运行

### 先决条件
- Node.js 18+ (前端)
- Go 1.23+ (后端)
- MySQL 8.0+

### 前端开发
```bash
cd client/shop
npm install
npm run dev
```

### 后端开发
```bash
cd server
go mod download
go run main.go
```

### 生产构建
```bash
# 前端
cd client/shop
npm run build
npm run start

# 后端
cd server
go build
./next-shop
```

## 项目结构

```
next-shop/
├── client/
│   └── shop/                  # 前端项目
│       ├── src/
│       │   ├── app/           # Next.js应用路由
│       │   ├── components/    # React组件
│       │   ├── lib/           # API客户端
│       │   └── styles/        # 全局样式
│       └── ...                # 其他Next.js配置文件
└── server/                    # 后端项目
    ├── controllers/           # 业务逻辑
    ├── middleware/            # 中间件
    ├── model/                 # 数据模型
    ├── router/                # 路由定义
    └── ...                    # 其他Go模块文件
```

## 开发指南

1. **前端开发**:
   - 组件放在`client/shop/src/components`
   - 页面路由使用Next.js 13+的App Router
   - API请求使用`client/shop/src/lib/api`中的客户端

2. **后端开发**:
   - 新API需在`server/router/router.go`注册
   - 业务逻辑放在`server/controllers`
   - 数据库模型在`server/model`

3. **环境变量**:
   - 前端: 创建`.env.local`文件
   - 后端: 配置`server/config`中的相关文件

## 贡献

欢迎提交Pull Request。请确保:
1. 代码风格一致
2. 包含必要的测试
3. 更新相关文档

## 许可证

MIT License
