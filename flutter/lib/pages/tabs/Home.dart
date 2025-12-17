import 'package:carousel_slider/carousel_slider.dart';
import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_jdshop/model/FocusModel.dart';
import 'package:flutter_jdshop/services/ScreenAdaper.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with AutomaticKeepAliveClientMixin {



  /// 轮播图数据，**永远不是 null**，初始就是空列表
  List<FocusModel> focusData = <FocusModel>[];

  /// 加载状态
  bool _isLoadingSwiper = false;

  /// 是否加载失败（可选）
  bool _loadError = false;

  @override
  void initState() {
    super.initState();
    _getFocusData();
  }

  /// 请求轮播图数据
  Future<void> _getFocusData() async {
    setState(() {
      _isLoadingSwiper = true;
      _loadError = false;
    });

    try {
      const api = 'https://jsonplaceholder.typicode.com/photos?_limit=10';
      final response = await Dio().get(api);

      final data = response.data;
      if (data is List) {
        final list = FocusModel.fromJsonList(data);
        setState(() {
          focusData = list; // 这里一定是一个 List<FocusModel>，不是 null
        });
      } else {
        debugPrint('接口返回的不是 List：$data');
        setState(() {
          _loadError = true;
        });
      }
    } catch (e) {
      debugPrint('获取轮播图数据失败: $e');
      setState(() {
        _loadError = true;
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingSwiper = false;
        });
      }
    }
  }

  // 轮播图
  Widget _swiperWidget() {
    // 1. 正在加载 & 还没数据
    if (_isLoadingSwiper && focusData.isEmpty) {
      return SizedBox(
        height: 150.h,
        child: const Center(child: CircularProgressIndicator()),
      );
    }

    // 2. 加载失败 & 没有数据 —— 给个提示/兜底图
    if (_loadError && focusData.isEmpty) {
      return SizedBox(
        height: 150.h,
        child: GestureDetector(
          onTap: _getFocusData, // 点一下重新加载
          child: const Center(
            child: Text('轮播图加载失败，点击重试'),
          ),
        ),
      );
    }

    // 3. 没出错，就是暂时还没拿到数据（极端情况）
    if (focusData.isEmpty) {
      return SizedBox(
        height: 150.h,
        child: Image.network(
          'https://picsum.photos/350/150',
          fit: BoxFit.cover,
          width: double.infinity,
        ),
      );
    }

    // 4. 有数据，正常轮播
    return AspectRatio(
      aspectRatio: 2 / 1, // 宽高比
      child: CarouselSlider.builder(
        itemCount: focusData.length,
        itemBuilder: (context, index, realIndex) {
          final item = focusData[index];
          return Image.network(
            item.url, // 接口返回的大图
            fit: BoxFit.cover,
            width: double.infinity,
          );
        },
        options: CarouselOptions(
          height: 150.h,
          viewportFraction: 1.0,
          autoPlay: true,
        ),
      ),
    );
  }

  Widget _titleWidget(String value) {
    return Container(
      height: 32.h,
      margin: const EdgeInsets.only(left: 10),
      padding: const EdgeInsets.only(left: 10),
      decoration: BoxDecoration(
        border: Border(
          left: BorderSide(
            color: Colors.red,
            width: 10.w,
          ),
        ),
      ),
      child: Text(
        value,
        style: const TextStyle(color: Colors.black54),
      ),
    );
  }

  // 热门商品
  Widget _hotProductListWidget() {
    return SizedBox(
      height: 160.h,
      width: double.infinity,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: 10,
        itemBuilder: (context, index) {
          return SizedBox(
            width: 140.w,
            child: Column(
              children: [
                Expanded(
                  child: Image.network(
                    'https://picsum.photos/64/64',
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(height: 4),
                Text('第$index条'),
              ],
            ),
          );
        },
      ),
    );
  }

  // 推荐商品
  Widget _recProductItemWidget() {
    final itemWidth = (ScreenAdapter.width(context) - 30) / 2;

    return Container(
      padding: const EdgeInsets.all(10),
      width: itemWidth,
      decoration: BoxDecoration(
        border: Border.all(
          color: Colors.black12,
          width: 1,
        ),
      ),
      child: Column(
        children: [
          SizedBox(
            width: double.infinity,
            child: Image.network(
              'https://picsum.photos/64/64',
              fit: BoxFit.cover,
            ),
          ),
          Padding(
            padding: EdgeInsets.only(top: 20.h),
            child: const Text(
              '这是标题这是标题这是标题这是标题',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(color: Colors.black54),
            ),
          ),
          Padding(
            padding: EdgeInsets.only(top: 20.h),
            child: Stack(
              children: const [
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    '123',
                    style: TextStyle(color: Colors.red, fontSize: 16),
                  ),
                ),
                Align(
                  alignment: Alignment.centerRight,
                  child: Text(
                    '180',
                    style: TextStyle(
                      color: Colors.black54,
                      fontSize: 14,
                      decoration: TextDecoration.lineThrough,
                    ),
                  ),
                )
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: <Widget>[
        _swiperWidget(),
        const SizedBox(height: 10),
        _titleWidget('猜你喜欢'),
        const SizedBox(height: 10),
        _hotProductListWidget(),
        const SizedBox(height: 10),
        _titleWidget('热门推荐'),
        Container(
          padding: const EdgeInsets.all(10),
          child: Wrap(
            runSpacing: 10,
            spacing: 10,
            children: [
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
              _recProductItemWidget(),
            ],
          ),
        ),
      ],
    );
  }

  @override
  bool get wantKeepAlive => true;
}
