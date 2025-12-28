class Config {
  static String domain = 'http://127.0.0.1:8080/api/v1';
  static String imageHost = domain.replaceAll('/api/v1', '');

  static String resolveImage(String? url) {
    if (url == null || url.isEmpty) {
      return '';
    }
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    if (url.startsWith('/')) {
      return '$imageHost$url';
    }
    return '$imageHost/$url';
  }
}
