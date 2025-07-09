package controllers

import (
	"github.com/DreamZhongJu/next-shop/model"
	"github.com/gin-gonic/gin"
)

type UserControllers struct{}

func (u UserControllers) Login(c *gin.Context) {
	username := c.PostForm("username")
	password := c.PostForm("password")

	if username == "" || password == "" {
		ReturnError(c, 400, "用户名或密码不能为空")
		return
	}

	data, err := model.Login(username, password)
	if err != nil || data == nil {
		ReturnError(c, 400, err.Error())
		return
	}

	ReturnSuccess(c, 0, "登陆成功", data, 1)
}

func (u UserControllers) Sign(c *gin.Context) {
	username := c.DefaultPostForm("username", "")
	password := c.DefaultPostForm("password", "")
	data, err := model.Sign(username, password)
	if err != nil || data == nil {
		ReturnError(c, 402, err.Error())
	}
	ReturnSuccess(c, 0, "注册成功", data, 1)
}
