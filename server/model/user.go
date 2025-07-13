package model

import (
	"errors"
	"time"

	"github.com/DreamZhongJu/next-shop/dao"
	"gorm.io/gorm"
)

// LoginRequest 表示用户登录输入（可用于接收参数）
type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type SignRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Role     string `gorm:"column:role"`
}

// User 与数据库 users 表字段一一对应
type User struct {
	UserID    int       `gorm:"column:user_id;primaryKey;autoIncrement"` // 映射 user_id 字段
	Username  string    `gorm:"column:username"`
	Password  string    `gorm:"column:password"`
	Role      string    `gorm:"column:role"`
	CreatedAt time.Time `gorm:"column:created_at"` // 正确类型，GORM 自动处理
}

// Login 执行登录逻辑，返回用户信息或错误
func Login(username string, password string) (*User, error) {
	var user User

	// 查询 username 对应的记录
	err := dao.GetDB().Where("username = ?", username).First(&user).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("用户不存在")
		}
		return nil, err
	}

	// 验证密码（明文，实际项目需改为哈希比对）
	if user.Password != password {
		return nil, errors.New("密码错误")
	}

	return &user, nil
}

func Sign(username string, password string) (*User, error) {
	// 用户名重复校验
	var existing User
	if err := dao.GetDB().Where("username = ?", username).First(&existing).Error; err == nil {
		return nil, errors.New("用户名已存在")
	}

	user := User{
		Username: username,
		Password: password,
		Role:     "common", // 默认角色
	}

	// 插入数据库
	err := dao.GetDB().Create(&user).Error
	if err != nil {
		return nil, err
	}

	return &user, nil
}

func AllUserCount() (int64, error) {
	var count int64
	err := dao.GetDB().Table("users").Count(&count).Error
	return count, err
}
