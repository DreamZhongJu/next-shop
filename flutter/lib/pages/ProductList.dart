import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_jdshop/model/ProductModel.dart';
import 'package:flutter_jdshop/services/ScreenAdaper.dart';
import 'package:flutter_jdshop/widget/LoadingWidget.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../config/Config.dart';
import '../model/RequestModel.dart';

class ProductListPage extends StatefulWidget {
  Map arguments;
  ProductListPage({super.key, required this.arguments});

  @override
  State<ProductListPage> createState() => _ProductListPageState();
}

class _ProductListPageState extends State<ProductListPage> {
  //Scafford key
  final GlobalKey<ScaffoldState> _scaffoldkey = new GlobalKey<ScaffoldState>();

  //用于上拉分页
  ScrollController _scrollController = ScrollController();

  //分页
  int _page = 1;

  //数据
  List<ProductModel> _productList = [];
  /*
  sort 可选：default、price_asc、price_desc、stock_asc、stock_desc
  */
  //排序
  String _sort = "default";

  //设置信号值，解决重复问题
  bool flag = true;

  @override
  void initState() {
    super.initState();
    _getProductListData();

    //监听滚动条滚动事件
    _scrollController.addListener((){
      // _scrollController.position.pixels; //获取滚动条滚动高度
      // _scrollController.position.maxScrollExtent; //获取页面高度

      if(_scrollController.position.pixels>_scrollController.position.maxScrollExtent-20){
        if(this.flag) {
          _getProductListData();
        }
      }
    });
  }

  //获取商品列表的数据
  _getProductListData() async {

    setState(() {
      this.flag = false;
    });

    final api =
        '${Config.domain}/categories/level2/${widget.arguments["cid"]}/products?page=${this._page}&sort=${this._sort}';
    final res = await Dio().get(api);

    final resp = ApiResponse<List<ProductModel>>.fromJson(
      res.data as Map<String, dynamic>,
      (raw) => (raw as List)
          .map((e) => ProductModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

    if (resp.code != 0) {
      throw Exception(resp.msg);
    }
    setState(() {
      this._productList.addAll(resp.data);
      this._page++;
      this.flag = true;
    });
  }

  Widget _subHeaderWidget() {
    return Positioned(
      top: 0,
      height: 80.h,
      width: 750.w,
      child: Container(
        height: 80.h,
        width: 750.w,
        decoration: BoxDecoration(
          border: Border(
            bottom: BorderSide(
              width: 1,
              color: Color.fromRGBO(233, 233, 233, 0.9),
            ),
          ),
        ),
        child: Row(
          children: [
            Expanded(
              flex: 1,
              child: InkWell(
                child: Padding(
                  padding: EdgeInsetsGeometry.fromLTRB(0, 16.h, 0, 20.h),
                  child: Text(
                    "综合",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.red),
                  ),
                ),
                onTap: () {},
              ),
            ),
            Expanded(
              flex: 1,
              child: InkWell(
                child: Padding(
                  padding: EdgeInsetsGeometry.fromLTRB(0, 16.h, 0, 20.h),
                  child: Text(
                    "销量",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.red),
                  ),
                ),
                onTap: () {},
              ),
            ),
            Expanded(
              flex: 1,
              child: InkWell(
                child: Padding(
                  padding: EdgeInsetsGeometry.fromLTRB(0, 16.h, 0, 20.h),
                  child: Text(
                    "价格",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.red),
                  ),
                ),
                onTap: () {},
              ),
            ),
            Expanded(
              flex: 1,
              child: InkWell(
                child: Padding(
                  padding: EdgeInsetsGeometry.fromLTRB(0, 16.h, 0, 20.h),
                  child: Text(
                    "筛选",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.red),
                  ),
                ),
                onTap: () {
                  _scaffoldkey.currentState?.openEndDrawer();
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _productListWidget() {
    if (this._productList.length > 0) {
      return Container(
        padding: EdgeInsets.all(10),
        margin: EdgeInsets.only(top: 80.h),
        child: ListView.builder(
          controller: _scrollController,
          itemCount: this._productList.length,
          itemBuilder: (context, index) {
            return Column(
              children: [
                Row(
                  children: [
                    Container(
                      width: 180.w,
                      height: 180.h,
                      child: Image.network(
                        "https://picsum.photos/64/64",
                        fit: BoxFit.cover,
                      ),
                    ),
                    Expanded(
                      flex: 1,
                      child: Container(
                        height: 180.h,
                        margin: EdgeInsets.only(left: 10),
                        //color: Colors.red,
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "${this._productList[index].name}",
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            Row(
                              children: [
                                Text(
                                  "${_productList[index].price}",
                                  style: const TextStyle(color: Colors.red, fontSize: 16),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Text(
                                    "库存：${_productList[index].stock}",
                                    style: const TextStyle(color: Colors.blue, fontSize: 12),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    textAlign: TextAlign.right,
                                  ),
                                ),
                              ],
                            )
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                Divider(height: 20),
                (index==this._productList.length-1&&!this.flag)?Loadingwidget():Text("")
              ],
            );
          },
        ),
      );
    } else {
      //加载中
      return Loadingwidget();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ScreenAdapter.init(
      child: Scaffold(
        key: _scaffoldkey,
        appBar: AppBar(title: Text("商品列表"), actions: [Text("")]),
        endDrawer: Drawer(child: Container(child: Text("实现筛选功能"))),
        //body: Text("${widget.arguments}"),
        body: Stack(children: [_productListWidget(), _subHeaderWidget()]),
      ),
    );
  }
}
