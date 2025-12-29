# Next-Shop 电商平台

Next-Shop 是一个完整的电商项目，包含 Web 前端、Flutter 客户端与 Go 后端。支持用户登录、商品浏览、购物车、分类、商品详情、以及管理员后台管理功能。

## 亮点功能

- 用户系统：注册、登录、JWT 鉴权
- 商品与分类：商品列表、详情、搜索、分类浏览
- 购物车：添加、数量调整、删除、刷新同步
- 管理后台：用户角色管理、商品管理、新建商品
- 多端支持：Web 前端 + Flutter 客户端

## 技术栈

### Web 前端 (client/shop)
- Next.js 15
- React 19
- TypeScript
- TailwindCSS

### Flutter 客户端 (flutter)
- Flutter Web
- Dio 网络请求
- Hive 本地存储
- 统一图片地址解析与默认图兜底

### 后端 (server)
- Go + Gin
- MySQL + GORM
- JWT 鉴权
- Zap 日志

## 项目结构

```
next-shop/
├── client/
│   └── shop/                 # Web 前端
├── flutter/                  # Flutter 客户端
└── server/                   # Go 后端
```

## 快速启动

### Web 前端
```bash
cd client/shop
npm install
npm run dev
```

### Flutter 客户端
```bash
cd flutter
flutter pub get
flutter run -d chrome
```

### 后端
```bash
cd server
go mod download
go run main.go
```

## 管理后台说明

- 登录后若角色为 `admin`，用户页会出现“进入后台”
- 可管理用户角色、商品数据并新建商品
- 管理接口路径统一为 `/api/v1/admin/*`

## 运行要求

- Node.js 18+
- Go 1.23+
- MySQL 8.0+
- Flutter 3.38+

## License

MIT
