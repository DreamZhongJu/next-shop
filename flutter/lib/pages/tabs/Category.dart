import 'dart:math';

import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_jdshop/config/Config.dart';
import 'package:flutter_jdshop/model/FocusModel.dart';
import 'package:flutter_jdshop/services/ScreenAdaper.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

import '../../model/CateModle.dart';
import '../../model/RequestModel.dart';

class CategoryPage extends StatefulWidget {
  const CategoryPage({super.key});

  @override
  State<CategoryPage> createState() => _CategoryPageState();
}

class _CategoryPageState extends State<CategoryPage> with AutomaticKeepAliveClientMixin {

  int _selectIndex = 0;

  @override
  void initState() {
    super.initState();
    _getLeftCateData();
  }

  List<CateItemModel> _leftCateList = [];
  bool _loading = false;
  _getLeftCateData() async {
    setState(() => _loading = true);

    try {
      final api = '${Config.domain}/categories';
      final res = await Dio().get(api);

      final resp = ApiResponse<List<CateItemModel>>.fromJson(
        res.data as Map<String, dynamic>,
            (raw) => (raw as List)
            .map((e) => CateItemModel.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

      if (resp.code != 0) {
        throw Exception(resp.msg);
      }

      setState(() {
        _leftCateList = resp.data;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      debugPrint('get categories error: $e');
    }
    //print(_leftCateList[0].name);
    _getRightCateData(_leftCateList[0].id);
  }

  List<CateLevel2ItemModel> _rightCateList = [];
  _getRightCateData(pid) async {
    setState(() => _loading = true);

    try {
      final api = '${Config.domain}/categories/${pid}/level2';
      final res = await Dio().get(api);

      final resp = ApiResponse<List<CateLevel2ItemModel>>.fromJson(
        res.data as Map<String, dynamic>,
            (raw) => (raw as List)
            .map((e) => CateLevel2ItemModel.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

      if (resp.code != 0) {
        throw Exception(resp.msg);
      }

      setState(() {
        _rightCateList = resp.data;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      debugPrint('get categories error: $e');
    }
    //print(_rightCateList[0].name);
  }

  Widget _leftCateWidget(leftWidth){

    return Container(
      padding: EdgeInsets.all(10.w),
      width: leftWidth,
      child: ListView.builder(
        itemCount: _leftCateList.length,
        itemBuilder: (context,index){
          return Column(
            children: [
              InkWell(
                onTap: (){
                  setState(() {
                    _selectIndex = index;
                    this._getRightCateData(_selectIndex+1);
                  });
                },
                child: Container(
                  child: Text(_leftCateList[index].name),
                  width: double.infinity,
                  padding: EdgeInsets.only(top: 24.h),
                  height: 84.h,
                  color: _selectIndex==index?Color.fromRGBO(240, 246, 246, 0.9):Colors.white,
                ),
              ),
              Divider(height: 1.h,)
            ],
          );
        },
      ),
      height: double.infinity,
    );
  }

  Widget _rightCateWidget(rightItemWidth,rightItemHeight){
    if(this._rightCateList.length>0){
      return
        Expanded(
          flex: 1,
          child: Container(
              height: double.infinity,
              color: Color.fromRGBO(240, 246, 246, 0.9),
              child: GridView.builder(
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    childAspectRatio: rightItemWidth/rightItemHeight,
                    crossAxisSpacing: 10
                ),
                itemCount: _rightCateList.length,
                itemBuilder: (context,index){
                  return InkWell(
                    onTap: (){
                      Navigator.pushNamed(context, '/productList',arguments: {
                        "cid":this._rightCateList[index].id
                      });
                    },
                    child: Container(
                      child: Column(
                        children: [
                          AspectRatio(
                            aspectRatio: 1/1,
                            child: Image.network("https://picsum.photos/64/64",fit: BoxFit.cover,),
                          ),
                          Container(
                            height: 32.h,
                            child: Text(_rightCateList[index].name),
                          )
                        ],
                      ),
                    ),
                  );
                },
              )
          ),
        );
    }

    return Expanded(
      flex: 1,
      child: Container(
        padding: EdgeInsets.all(10),
          height: double.infinity,
          color: Color.fromRGBO(240, 246, 246, 0.9),
        child: Text("加载中"),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    var leftWidth = ScreenAdapter.width(context)/4;
    var rightItemWidth = (ScreenAdapter.width(context) - leftWidth-20-20)/3;
    var rightItemHeight = rightItemWidth+20.h+32.h;

    return ScreenAdapter.init(
        child: Row(
      children: [
        _leftCateWidget(leftWidth),
        _rightCateWidget(rightItemWidth, rightItemHeight)
      ],
    ));
  }

  @override
  bool get wantKeepAlive => true;
}

