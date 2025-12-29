import 'package:flutter/material.dart';
import 'package:flutter_jdshop/model/ProductModel.dart';
import 'package:flutter_jdshop/config/Config.dart';
import 'package:flutter_jdshop/services/ApiService.dart';
import 'package:flutter_jdshop/services/StorageService.dart';

class CartPage extends StatefulWidget {
  const CartPage({super.key});

  @override
  State<CartPage> createState() => _CartPageState();
}

class _CartItemView {
  final int productId;
  int quantity;
  ProductModel? product;

  _CartItemView({
    required this.productId,
    required this.quantity,
    this.product,
  });
}

class _CartPageState extends State<CartPage> with AutomaticKeepAliveClientMixin {
  final ApiService _apiService = ApiService();
  final StorageService _storageService = StorageService();
  final Map<int, ProductModel> _productCache = {};

  List<_CartItemView> _items = [];
  bool _isLoading = false;
  bool _isGuest = false;
  int? _userId;

  @override
  void initState() {
    super.initState();
    _loadCart();
  }

  Future<void> _loadCart() async {
    setState(() {
      _isLoading = true;
      _isGuest = false;
    });

    final cached = await _storageService.getCartItems();
    if (cached.isNotEmpty) {
      final parsed = cached
          .map((e) => e as Map<String, dynamic>)
          .map((item) => _CartItemView(
                productId: (item['product_id'] as num?)?.toInt() ?? 0,
                quantity: (item['quantity'] as num?)?.toInt() ?? 1,
              ))
          .toList();
      setState(() {
        _items = parsed;
      });
      await _loadProductDetails(parsed);
    }

    final userData = await _storageService.getUserData();
    final token = await _storageService.getUserToken();
    final user = userData['user'];
    _userId = user is Map<String, dynamic> ? user['user_id'] : null;

    if (token == null || _userId == null) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _isGuest = true;
        });
      }
      return;
    }

    try {
      final response = await _apiService.get<List<dynamic>>(
        '/cart/list/$_userId',
        fromJson: (raw) => raw as List,
      );

      if (response.code != 0) {
        throw Exception(response.msg);
      }

      await _storageService.saveCartItems(response.data);
      final parsed = response.data
          .map((e) => e as Map<String, dynamic>)
          .map((item) => _CartItemView(
                productId: (item['product_id'] as num?)?.toInt() ?? 0,
                quantity: (item['quantity'] as num?)?.toInt() ?? 1,
              ))
          .toList();

      if (mounted) {
        setState(() {
          _items = parsed;
        });
      }
      await _loadProductDetails(parsed);
    } catch (_) {
      if (mounted) {
        setState(() {
          _isGuest = false;
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadProductDetails(List<_CartItemView> items) async {
    final ids = items.map((e) => e.productId).toSet();
    final missing = ids.where((id) => !_productCache.containsKey(id)).toList();
    if (missing.isNotEmpty) {
      final results = await Future.wait(
        missing.map(
          (id) async {
            try {
              return await _apiService.get<ProductModel>(
                '/search/detail/$id',
                fromJson: (raw) => ProductModel.fromJson(raw),
              );
            } catch (_) {
              return null;
            }
          },
        ),
      );

      for (final result in results) {
        if (result != null && result.code == 0 && result.data.id != null) {
          _productCache[result.data.id!] = result.data;
        }
      }
    }

    if (mounted) {
      setState(() {
        _items = items
            .map((item) => _CartItemView(
                  productId: item.productId,
                  quantity: item.quantity,
                  product: _productCache[item.productId],
                ))
            .toList();
      });
    }
  }

  Future<void> _updateQuantity(_CartItemView item, int newQuantity) async {
    if (newQuantity < 1) return;
    setState(() {
      item.quantity = newQuantity;
    });
    await _storageService.saveCartItems(_items.map((e) {
      return {
        'product_id': e.productId,
        'quantity': e.quantity,
      };
    }).toList());

    if (_userId != null) {
      try {
        await _apiService.put(
          '/cart/update',
          data: {
            'uid': _userId.toString(),
            'pid': item.productId.toString(),
            'quantity': newQuantity.toString(),
          },
        );
      } catch (_) {}
    }
  }

  Future<void> _removeItem(_CartItemView item) async {
    setState(() {
      _items.removeWhere((e) => e.productId == item.productId);
    });
    await _storageService.saveCartItems(_items.map((e) {
      return {
        'product_id': e.productId,
        'quantity': e.quantity,
      };
    }).toList());

    if (_userId != null) {
      try {
        await _apiService.post(
          '/cart/delete',
          data: {
            'uid': _userId.toString(),
            'pid': item.productId.toString(),
          },
        );
      } catch (_) {}
    }
  }

  double get _totalPrice {
    double total = 0;
    for (final item in _items) {
      final price = item.product?.price ?? 0;
      total += price * item.quantity;
    }
    return total;
  }

  Widget _emptyState(String title, String subtitle) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.shopping_cart_outlined,
              size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 12),
          Text(
            title,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 6),
          Text(
            subtitle,
            style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadCart,
            child: const Text('Refresh cart'),
          ),
        ],
      ),
    );
  }

  Widget _quantityControls(_CartItemView item) {
    return Row(
      children: [
        IconButton(
          onPressed: () => _updateQuantity(item, item.quantity - 1),
          icon: const Icon(Icons.remove),
          splashRadius: 18,
        ),
        Text(
          item.quantity.toString(),
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        IconButton(
          onPressed: () => _updateQuantity(item, item.quantity + 1),
          icon: const Icon(Icons.add),
          splashRadius: 18,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    if (_isLoading && _items.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_isGuest) {
      return _emptyState('Please login', 'Sign in to sync your cart');
    }

    if (_items.isEmpty) {
      return _emptyState('Cart is empty', 'Pick something you like');
    }

    return Column(
      children: [
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: _items.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final item = _items[index];
              final product = item.product;
              return Dismissible(
                key: ValueKey(item.productId),
                direction: DismissDirection.endToStart,
                onDismissed: (_) => _removeItem(item),
                background: Container(
                  alignment: Alignment.centerRight,
                  padding: const EdgeInsets.only(right: 20),
                  color: Colors.red.shade400,
                  child: const Icon(Icons.delete, color: Colors.white),
                ),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: SizedBox(
                          width: 72,
                          height: 72,
                          child: Image.network(
                            Config.resolveImage(product?.imageUrl) == ''
                                ? 'https://picsum.photos/seed/cart${item.productId}/200'
                                : Config.resolveImage(product?.imageUrl),
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Image.asset(
                                Config.defaultProductAsset,
                                fit: BoxFit.cover,
                              );
                            },
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              product?.name ?? 'Loading product',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Stock: ${product?.stock ?? 0}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade600,
                              ),
                            ),
                            const SizedBox(height: 6),
                            _quantityControls(item),
                          ],
                        ),
                      ),
                      Text(
                        'CNY ${(product?.price ?? 0).toStringAsFixed(2)}',
                        style: const TextStyle(
                          color: Colors.red,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, -4),
              ),
            ],
          ),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  'Total: CNY ${_totalPrice.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              ElevatedButton(
                onPressed: () {},
                child: const Text('Checkout'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  bool get wantKeepAlive => true;
}
