class ProductModel {
  int? id;
  String? name;
  String? description;
  double? price;
  int? stock;
  String? imageUrl;
  String? category;
  String? createdAt;
  String? updatedAt;

  ProductModel(
      {this.id,
        this.name,
        this.description,
        this.price,
        this.stock,
        this.imageUrl,
        this.category,
        this.createdAt,
        this.updatedAt});

  ProductModel.fromJson(Map<String, dynamic> json) {
    id = json['id'];
    name = json['name'];
    description = json['description'];
    price = json['price'];
    stock = json['stock'];
    imageUrl = json['image_url'];
    category = json['category'];
    createdAt = json['created_at'];
    updatedAt = json['updated_at'];
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = new Map<String, dynamic>();
    data['id'] = this.id;
    data['name'] = this.name;
    data['description'] = this.description;
    data['price'] = this.price;
    data['stock'] = this.stock;
    data['image_url'] = this.imageUrl;
    data['category'] = this.category;
    data['created_at'] = this.createdAt;
    data['updated_at'] = this.updatedAt;
    return data;
  }
}