class CateItemModel {
  final int id;
  final String name;
  final DateTime createdAt;
  final DateTime updatedAt;

  CateItemModel({
    required this.id,
    required this.name,
    required this.createdAt,
    required this.updatedAt,
  });

  factory CateItemModel.fromJson(Map<String, dynamic> json) {
    return CateItemModel(
      id: (json['id'] as num).toInt(),
      name: (json['name'] ?? '') as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'created_at': createdAt.toUtc().toIso8601String(),
      'updated_at': updatedAt.toUtc().toIso8601String(),
    };
  }
}


class CateLevel2ItemModel {
  final int id;
  final String name;
  final int level1Id;
  final String createdAt;
  final String updatedAt;

  const CateLevel2ItemModel({
    required this.id,
    required this.name,
    required this.level1Id,
    required this.createdAt,
    required this.updatedAt,
  });

  factory CateLevel2ItemModel.fromJson(Map<String, dynamic> json) {
    return CateLevel2ItemModel(
      id: json['id'] as int,
      name: json['name'] as String,
      level1Id: json['level1_id'] as int,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'level1_id': level1Id,
    'created_at': createdAt,
    'updated_at': updatedAt,
  };
}
