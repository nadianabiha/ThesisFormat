import 'package:flutter/foundation.dart';

/// Memberi tahu layar lain bahwa daftar dokumen berubah
/// (mis. setelah upload berhasil), agar Home dan Riwayat
/// memuat ulang data tanpa perlu refresh manual.
class DocumentEvents extends ChangeNotifier {
  DocumentEvents._();

  static final DocumentEvents instance = DocumentEvents._();

  void documentsChanged() => notifyListeners();
}
