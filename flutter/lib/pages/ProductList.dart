import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_jdshop/services/ScreenAdaper.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class ProductListPage extends StatefulWidget {
  Map arguments;
  ProductListPage({super.key, required this.arguments});

  @override
  State<ProductListPage> createState() => _ProductListPageState();
}

class _ProductListPageState extends State<ProductListPage> {
  final GlobalKey<ScaffoldState> _scaffoldkey = new GlobalKey<ScaffoldState>();

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
                onTap: () {
                },
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
    return Container(
      padding: EdgeInsets.all(10),
      margin: EdgeInsets.only(top: 80.h),
      child: ListView.builder(
        itemCount: 10,
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
                            "商品名字",
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            "999",
                            style: TextStyle(color: Colors.red, fontSize: 16),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              Divider(height: 20),
            ],
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScreenAdapter.init(
      child: Scaffold(
        key: _scaffoldkey,
        appBar: AppBar(title: Text("商品列表"),actions: [Text("")],),
        endDrawer: Drawer(
          child: Container(
            child: Text("实现筛选功能"),
          ),
        ),
        //body: Text("${widget.arguments}"),
        body: Stack(children: [_productListWidget(), _subHeaderWidget()]),
      ),
    );
  }
}
