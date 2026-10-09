import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../services/auth_service.dart';

/// Mock client for the frontend. No HTTP requests are made yet.
class ApiService {
  const ApiService();

  // TODO: Integrasikan endpoint login Django dari Person 1.
  Future<Map<String, dynamic>> login({required String email, required String password}) async {
    final user = AuthService.instance.login(email: email, password: password);
    return {
      'access': 'dummy-access-token',
      'refresh': 'dummy-refresh-token',
      'user': user.toJson(),
    };
  }

  // TODO: Hubungkan ke endpoint register backend.
  Future<Map<String, dynamic>> register({required String name, required String email, required String password}) async {
    return AuthService.instance.register(name: name, email: email, password: password).toJson();
  }

  // TODO: Kirim MultipartFile ke endpoint upload Django Person 1.
  Future<DocumentModel> uploadDocument({required String path, required String documentType}) async => DocumentModel(
    fileName: path.split(RegExp(r'[/\\]')).last,
    documentType: documentType,
    uploadDate: DateTime.now().toIso8601String(),
    status: 'processing',
  );

  // TODO: Ganti mock ini dengan GET /documents/{id}/result/.
  Future<AuditResult> getDocumentResult(int documentId) async => AuditResult.demo;

  // TODO: Ganti dummy list dengan GET history dari REST API.
  Future<List<DocumentModel>> getDocumentHistory() async => DocumentModel.history;

  // TODO: Hubungkan ke GET /profile/ milik backend Person 1.
  Future<Map<String, dynamic>> getProfile() async =>
      AuthService.instance.currentUser?.toJson() ?? <String, dynamic>{};
}
