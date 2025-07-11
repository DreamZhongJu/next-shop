package controllers

import (
	"strconv"

	"github.com/DreamZhongJu/next-shop/model"
	"github.com/gin-gonic/gin"
)

type UserSearch struct{}

func (s UserSearch) Search(c *gin.Context) {
	name := c.DefaultPostForm("name", "")
	products, err := model.SearchProduct(name)
	if err != nil {
		ReturnError(c, 402, "搜索失败："+err.Error())
	}
	ReturnSuccess(c, 0, "搜索成功", products, 0)
}

func (s UserSearch) SearchAll(c *gin.Context) {
	products, err := model.GetAllProducts()
	if err != nil {
		ReturnError(c, 402, "获取商品信息失败"+err.Error())
	}
	ReturnSuccess(c, 0, "获取商品信息成功", products, 0)
}

func (s UserSearch) GetProductDetail(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		ReturnError(c, 400, "商品ID格式错误")
		return
	}
	product, err := model.GetProductByID(id)
	if err != nil {
		ReturnError(c, 404, "商品不存在或已下架")
		return
	}
	ReturnSuccess(c, 0, "获取商品详情成功", product, 0)
}
