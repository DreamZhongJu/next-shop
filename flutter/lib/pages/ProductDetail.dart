import 'package:flutter/material.dart';
import 'package:flutter_jdshop/model/ProductModel.dart';
import 'package:flutter_jdshop/services/ApiService.dart';
import 'package:flutter_jdshop/services/AppState.dart';
import 'package:flutter_jdshop/widget/ProductCard.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:shimmer/shimmer.dart';
import 'package:provider/provider.dart';
import 'package:badges/badges.dart' as badges;

class ProductDetailPage extends StatefulWidget {
  final int productId;

  const ProductDetailPage({super.key, required this.productId});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  final ApiService _apiService = ApiService();
  ProductModel? _product;
  bool _isLoading = true;
  bool _loadError = false;
  int _selectedImageIndex = 0;
  int _quantity = 1;
  List<String> _imageUrls = [];

  @override
  void initState() {
    super.initState();
    _loadProductDetail();
  }

  Future<void> _loadProductDetail() async {
    setState(() {
      _isLoading = true;
      _loadError = false;
    });

    try {
      final response = await _apiService.get('/search/detail/${widget.productId}');
      
      if (response.code == 0 && response.data is Map<String, dynamic>) {
        final productData = response.data as Map<String, dynamic>;
        final product = ProductModel.fromJson(productData);
        
        setState(() {
          _product = product;
          _imageUrls = [
            product.imageUrl ?? 'https://picsum.photos/400/400',
            'https://picsum.photos/400/401',
            'https://picsum.photos/400/402',
            'https://picsum.photos/400/403',
          ];
          _isLoading = false;
        });
      } else {
        setState(() {
          _loadError = true;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('加载商品详情失败: $e');
      setState(() {
        _loadError = true;
        _isLoading = false;
      });
    }
  }

  Widget _buildImageGallery() {
    if (_isLoading) {
      return Shimmer.fromColors(
        baseColor: Colors.grey.shade300,
        highlightColor: Colors.grey.shade100,
        child: Container(
          height: 400,
          width: double.infinity,
          color: Colors.white,
        ),
      );
    }

    if (_loadError || _imageUrls.isEmpty) {
      return Container(
        height: 400,
        color: Colors.grey.shade100,
        child: const Center(
          child: Icon(
            Icons.image_not_supported_outlined,
            color: Colors.grey,
            size: 64,
          ),
        ),
      );
    }

    return Column(
      children: [
        Container(
          height: 400,
          width: double.infinity,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: CachedNetworkImage(
            imageUrl: _imageUrls[_selectedImageIndex],
            fit: BoxFit.contain,
            placeholder: (context, url) => Shimmer.fromColors(
              baseColor: Colors.grey.shade300,
              highlightColor: Colors.grey.shade100,
              child: Container(
                width: double.infinity,
                height: 400,
                color: Colors.white,
              ),
            ),
            errorWidget: (context, url, error) => Container(
              color: Colors.grey.shade200,
              child: const Center(
                child: Icon(
                  Icons.image_not_supported_outlined,
                  color: Colors.grey,
                  size: 48,
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 80,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _imageUrls.length,
            itemBuilder: (context, index) {
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedImageIndex = index;
                  });
                },
                child: Container(
                  width: 80,
                  height: 80,
                  margin: const EdgeInsets.only(right: 12),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: _selectedImageIndex == index
                          ? Colors.blue.shade500
                          : Colors.grey.shade300,
                      width: _selectedImageIndex == index ? 2 : 1,
                    ),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: CachedNetworkImage(
                      imageUrl: _imageUrls[index],
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        color: Colors.grey.shade200,
                      ),
                      errorWidget: (context, url, error) => Container(
                        color: Colors.grey.shade200,
                        child: const Icon(
                          Icons.image_not_supported_outlined,
                          color: Colors.grey,
                          size: 24,
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildProductInfo() {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Shimmer.fromColors(
              baseColor: Colors.grey.shade300,
              highlightColor: Colors.grey.shade100,
              child: Container(
                width: 200,
                height: 24,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            Shimmer.fromColors(
              baseColor: Colors.grey.shade300,
              highlightColor: Colors.grey.shade100,
              child: Container(
                width: 150,
                height: 20,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            Shimmer.fromColors(
              baseColor: Colors.grey.shade300,
              highlightColor: Colors.grey.shade100,
              child: Container(
                width: double.infinity,
                height: 60,
                color: Colors.white,
              ),
            ),
          ],
        ),
      );
    }

    if (_loadError || _product == null) {
      return const Padding(
        padding: EdgeInsets.all(16),
        child: Center(
          child: Text(
            '商品信息加载失败',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
        ),
      );
    }

    final product = _product!;
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            product.name ?? 'Unknown Product',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              badges.Badge(
                badgeStyle: badges.BadgeStyle(
                  badgeColor: Colors.blue.shade500,
                ),
                badgeContent: const Text(
                  '4.8',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                  ),
                ),
                child: const Icon(
                  Icons.star,
                  color: Colors.amber,
                  size: 20,
                ),
              ),
              const SizedBox(width: 4),
              const Text(
                '4.8 (128 reviews)',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 14,
                ),
              ),
              const Spacer(),
              Text(
                '库存: ${product.stock ?? 0}',
                style: const TextStyle(
                  color: Colors.green,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Text(
                '\$${product.price?.toStringAsFixed(2) ?? '0.00'}',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '\$${(product.price ?? 0) * 1.3}',
                style: const TextStyle(
                  fontSize: 18,
                  color: Colors.grey,
                  decoration: TextDecoration.lineThrough,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  '30% OFF',
                  style: TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Text(
            '商品描述',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            product.description ?? 'No description available',
            style: const TextStyle(
              fontSize: 16,
              color: Colors.grey,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            '规格参数',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          _buildSpecItem('品牌', 'JD Shop'),
          _buildSpecItem('型号', 'JD-${product.id}'),
          _buildSpecItem('分类', product.category ?? '未分类'),
          _buildSpecItem('重量', '1.2kg'),
          _buildSpecItem('尺寸', '30 × 20 × 10 cm'),
        ],
      ),
    );
  }

  Widget _buildSpecItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuantitySelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text(
            '数量',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
          Row(
            children: [
              IconButton(
                onPressed: _quantity > 1
                    ? () {
                        setState(() {
                          _quantity--;
                        });
                      }
                    : null,
                icon: const Icon(Icons.remove),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                    side: BorderSide(color: Colors.grey.shade300),
                  ),
                ),
              ),
              Container(
                width: 60,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Text(
                  _quantity.toString(),
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              IconButton(
                onPressed: () {
                  setState(() {
                    _quantity++;
                  });
                },
                icon: const Icon(Icons.add),
                style: IconButton.styleFrom(
                  backgroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                    side: BorderSide(color: Colors.grey.shade300),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          top: BorderSide(color: Colors.grey.shade200),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () {
                final appState = Provider.of<AppState>(context, listen: false);
                if (_product != null) {
                  appState.addToCart({
                    'product': _product!.toJson(),
                    'quantity': _quantity,
                    'price': _product!.price,
                  });
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('已添加到购物车'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                }
              },
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                side: BorderSide(color: Colors.blue.shade500),
              ),
              child: const Text(
                '加入购物车',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.blue,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton(
              onPressed: () {
                final appState = Provider.of<AppState>(context, listen: false);
                if (_product != null) {
                  appState.addToCart({
                    'product': _product!.toJson(),
                    'quantity': _quantity,
                    'price': _product!.price,
                  });
                  Navigator.pushNamed(context, '/cart');
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue.shade500,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                '立即购买',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('商品详情'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.favorite_border),
            onPressed: () {},
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  _buildImageGallery(),
                  _buildProductInfo(),
                  _buildQuantitySelector(),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
          _buildActionButtons(),
        ],
      ),
    );
  }
}
