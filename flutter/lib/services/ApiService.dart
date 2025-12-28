import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_jdshop/config/Config.dart';
import 'package:flutter_jdshop/model/RequestModel.dart';
import 'package:flutter_jdshop/services/StorageService.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storageService.getUserToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = token;
          }
          handler.next(options);
        },
      ),
    );
  }

  final Dio _dio = Dio(BaseOptions(
    baseUrl: Config.domain,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
    },
  ));
  final StorageService _storageService = StorageService();

  Future<ApiResponse<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
      );
      
      if (fromJson != null) {
        return ApiResponse<T>.fromJson(
          response.data as Map<String, dynamic>,
          fromJson,
        );
      }
      
      return ApiResponse<T>.fromJson(
        response.data as Map<String, dynamic>,
        (data) => data as T,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<ApiResponse<T>> post<T>(
    String path, {
    dynamic data,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
      );
      
      if (fromJson != null) {
        return ApiResponse<T>.fromJson(
          response.data as Map<String, dynamic>,
          fromJson,
        );
      }
      
      return ApiResponse<T>.fromJson(
        response.data as Map<String, dynamic>,
        (data) => data as T,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<ApiResponse<T>> put<T>(
    String path, {
    dynamic data,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
      );
      
      if (fromJson != null) {
        return ApiResponse<T>.fromJson(
          response.data as Map<String, dynamic>,
          fromJson,
        );
      }
      
      return ApiResponse<T>.fromJson(
        response.data as Map<String, dynamic>,
        (data) => data as T,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<ApiResponse<T>> delete<T>(
    String path, {
    dynamic data,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
      );
      
      if (fromJson != null) {
        return ApiResponse<T>.fromJson(
          response.data as Map<String, dynamic>,
          fromJson,
        );
      }
      
      return ApiResponse<T>.fromJson(
        response.data as Map<String, dynamic>,
        (data) => data as T,
      );
    } catch (e) {
      rethrow;
    }
  }
}
