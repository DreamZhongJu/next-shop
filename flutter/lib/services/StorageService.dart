import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  static const String _productBox = 'products';
  static const String _categoryBox = 'categories';
  static const String _userBox = 'user';
  static const String _cartBox = 'cart';

  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;

    await Hive.initFlutter();
    
    await Hive.openBox(_productBox);
    await Hive.openBox(_categoryBox);
    await Hive.openBox(_userBox);
    await Hive.openBox(_cartBox);
    
    _initialized = true;
  }

  Future<void> saveProducts(List<dynamic> products) async {
    await init();
    final box = Hive.box(_productBox);
    await box.put('products', products);
    await box.put('last_updated', DateTime.now().millisecondsSinceEpoch);
  }

  Future<List<dynamic>> getProducts() async {
    await init();
    final box = Hive.box(_productBox);
    final products = box.get('products', defaultValue: []);
    return List<dynamic>.from(products);
  }

  Future<bool> shouldRefreshProducts({int cacheDurationHours = 1}) async {
    await init();
    final box = Hive.box(_productBox);
    final lastUpdated = box.get('last_updated', defaultValue: 0);
    if (lastUpdated == 0) return true;
    
    final now = DateTime.now().millisecondsSinceEpoch;
    final hoursSinceUpdate = (now - lastUpdated) / (1000 * 60 * 60);
    return hoursSinceUpdate > cacheDurationHours;
  }

  Future<void> saveCategories(List<dynamic> categories) async {
    await init();
    final box = Hive.box(_categoryBox);
    await box.put('categories', categories);
    await box.put('categories_last_updated', DateTime.now().millisecondsSinceEpoch);
  }

  Future<List<dynamic>> getCategories() async {
    await init();
    final box = Hive.box(_categoryBox);
    final categories = box.get('categories', defaultValue: []);
    return List<dynamic>.from(categories);
  }

  Future<bool> shouldRefreshCategories({int cacheDurationHours = 6}) async {
    await init();
    final box = Hive.box(_categoryBox);
    final lastUpdated = box.get('categories_last_updated', defaultValue: 0);
    if (lastUpdated == 0) return true;

    final now = DateTime.now().millisecondsSinceEpoch;
    final hoursSinceUpdate = (now - lastUpdated) / (1000 * 60 * 60);
    return hoursSinceUpdate > cacheDurationHours;
  }

  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await init();
    final box = Hive.box(_userBox);
    await box.put('user_data', userData);
    final token = userData['token'] ?? userData['Token'];
    if (token != null) {
      await box.put('user_token', token.toString());
    }
  }

  Future<Map<String, dynamic>> getUserData() async {
    await init();
    final box = Hive.box(_userBox);
    final userData = box.get('user_data', defaultValue: {});
    return Map<String, dynamic>.from(userData);
  }

  Future<String?> getUserToken() async {
    await init();
    final box = Hive.box(_userBox);
    return box.get('user_token');
  }

  Future<void> clearUserData() async {
    await init();
    final box = Hive.box(_userBox);
    await box.clear();
  }

  Future<void> saveCartItems(List<dynamic> cartItems) async {
    await init();
    final box = Hive.box(_cartBox);
    await box.put('cart_items', cartItems);
  }

  Future<List<dynamic>> getCartItems() async {
    await init();
    final box = Hive.box(_cartBox);
    final cartItems = box.get('cart_items', defaultValue: []);
    return List<dynamic>.from(cartItems);
  }

  Future<void> clearAllCache() async {
    await init();
    await Hive.box(_productBox).clear();
    await Hive.box(_categoryBox).clear();
    await Hive.box(_cartBox).clear();
  }

  Future<void> close() async {
    if (_initialized) {
      await Hive.close();
      _initialized = false;
    }
  }
}
