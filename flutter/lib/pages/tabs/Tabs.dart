import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_jdshop/pages/tabs/Cart.dart';
import 'package:flutter_jdshop/pages/tabs/Category.dart';
import 'package:flutter_jdshop/pages/tabs/User.dart';
import 'package:flutter_jdshop/pages/tabs/Home.dart';

class Tabs extends StatefulWidget {
  const Tabs({super.key});

  @override
  State<Tabs> createState() => _TabsState();
}

class _TabsState extends State<Tabs> {
  int _currentIndex = 1;
  var _pageController;
  List<Widget> _pageList = [
    HomePage(),
    CategoryPage(),
    CartPage(),
    UserPage(),
  ];

  @override
  void initState() {
    _pageController = new PageController(initialPage: _currentIndex);
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("jsshop"),
      ),
      body: PageView(
        controller: _pageController,
        children: this._pageList,
        onPageChanged: (index){
          _currentIndex = index;
        },
      ),
      bottomNavigationBar: BottomNavigationBar(
        fixedColor: Colors.red,
      currentIndex: this._currentIndex,
      onTap: (index){
          setState(() {
            this._currentIndex=index;
            _pageController.jumpToPage(_currentIndex);
          });
      },
          type: BottomNavigationBarType.fixed,
      items: [
        BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: "首页"
        ),
        BottomNavigationBarItem(
            icon: Icon(Icons.category),
            label: "分类"
        ),
        BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: "购物车"
        ),
        BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: "我的"
        )
      ]),
    );
  }
}
