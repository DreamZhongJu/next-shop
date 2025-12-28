import 'package:flutter/material.dart';
import 'package:flutter_jdshop/services/ApiService.dart';
import 'package:flutter_jdshop/services/StorageService.dart';

class UserPage extends StatefulWidget {
  const UserPage({super.key});

  @override
  State<UserPage> createState() => _UserPageState();
}

class _UserPageState extends State<UserPage> with AutomaticKeepAliveClientMixin {
  final ApiService _apiService = ApiService();
  final StorageService _storageService = StorageService();

  Map<String, dynamic> _userData = {};
  int _userCount = 0;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    setState(() {
      _loading = true;
    });

    final data = await _storageService.getUserData();
    try {
      final response = await _apiService.get<Map<String, dynamic>>(
        '/user/count',
        fromJson: (raw) => raw as Map<String, dynamic>,
      );
      if (response.code == 0) {
        _userCount = (response.data['count'] as num?)?.toInt() ?? 0;
      }
    } catch (e) {}

    if (mounted) {
      setState(() {
        _userData = data;
        _loading = false;
      });
    }
  }

  Widget _profileHeader() {
    final user = _userData['user'];
    final username = user is Map<String, dynamic>
        ? (user['username'] ?? '游客')
        : '游客';
    final displayName = username.toString();
    final initial = displayName.isNotEmpty
        ? displayName.substring(0, 1).toUpperCase()
        : 'U';
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade400, Colors.teal.shade300],
        ),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 28,
            backgroundColor: Colors.white,
            child: Text(
              initial,
              style: TextStyle(
                color: Colors.blue.shade600,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                displayName,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                '平台用户数：$_userCount',
                style: TextStyle(
                  color: Colors.white.withOpacity(0.9),
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _menuItem(IconData icon, String title) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.blueGrey.shade600),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(fontSize: 14),
            ),
          ),
          Icon(Icons.chevron_right, color: Colors.grey.shade400),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return _loading
        ? const Center(child: CircularProgressIndicator())
        : ListView(
            children: [
              _profileHeader(),
              const SizedBox(height: 16),
              _menuItem(Icons.receipt_long, '我的订单'),
              _menuItem(Icons.location_on_outlined, '收货地址'),
              _menuItem(Icons.favorite_border, '收藏夹'),
              _menuItem(Icons.support_agent, '客服与帮助'),
              _menuItem(Icons.settings_outlined, '设置'),
              const SizedBox(height: 24),
            ],
          );
  }

  @override
  bool get wantKeepAlive => true;
}
