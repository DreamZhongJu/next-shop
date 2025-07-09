package main

import (
	"github.com/DreamZhongJu/next-shop/router"
)

func main() {
	r := router.Router()

	r.Run(":8080")
}
