
import 'audit_result.dart';
import 'document_type.dart';

class DocumentModel {
  const DocumentModel({
    this.id,
    required this.fileName,
    required this.documentType,
    required this.uploadDate,
    this.status = 'completed',
    this.score = 0,
    this.findingsCount = 0,
    this.sizeBytes = 0,
    this.result,
  });

  final int? id;
  final String fileName;
  final String documentType;
  final String uploadDate;
  final String status;
  final int score;
  final int findingsCount;
  final int sizeBytes;
  final AuditResult? result;

  DocumentModel copyWith({
    String? documentType,
    int? score,
    int? findingsCount,
    AuditResult? result,
  }) => DocumentModel(
    id: id,
    fileName: fileName,
    documentType: documentType ?? this.documentType,
    uploadDate: uploadDate,
    status: status,
    score: score ?? this.score,
    findingsCount: findingsCount ?? this.findingsCount,
    sizeBytes: sizeBytes,
    result: result ?? this.result,
  );

  String get name => fileName;

  String get type => documentType;

  String get displayDocumentType => DocumentType.labelOf(documentType);

  String get date => uploadDate;

  int get findings => findingsCount;

  /// Pemeriksaan isi (AI) gagal: nilai yang tersimpan hanya nilai format,
  /// jadi dokumen belum punya nilai akhir.
  bool get isIncomplete =>
      status == 'completed' && result != null && !result!.hasSemanticScore;

  String get displayStatus {
    if (isIncomplete) return 'Incomplete';
    if (status == 'completed') {
      if (score >= 90) return 'Excellent';
      if (score >= 75) return 'Good';
      return 'Needs improvement';
    }

    if (status == 'processing') return 'Processing';
    if (status == 'failed') return 'Failed';

    return status;
  }

  factory DocumentModel.fromJson(Map<String, dynamic> json) {
    final rawId = json['id'] ?? json['document_id'];

    final rawResult = json['result'];

    return DocumentModel(
      id: rawId is num
          ? rawId.toInt()
          : int.tryParse(rawId?.toString() ?? ''),

      fileName: (
        json['file_name'] ??
        json['fileName'] ??
        json['title'] ??
        json['name'] ??
        ''
      ).toString(),

      documentType: (
        json['document_type'] ??
        json['documentType'] ??
        ''
      ).toString(),

      uploadDate: _formatDate(
        (
          json['upload_date'] ??
          json['uploadDate'] ??
          json['uploaded_at'] ??
          ''
        ).toString(),
      ),

      status: (json['status'] ?? 'processing').toString(),

      score: (json['score'] as num?)?.toInt()
          ?? (json['total_score'] as num?)?.toInt()
          ?? 0,

      findingsCount:
          (json['findings_count'] as num?)?.toInt() ?? 0,

      sizeBytes:
          (json['size_bytes'] as num?)?.toInt() ?? 0,

      result: rawResult is Map
          ? AuditResult.fromJson(Map<String, dynamic>.from(rawResult))
          : null,
    );
  }

  static String _formatDate(String raw) {
    final parsed = DateTime.tryParse(raw)?.toLocal();
    if (parsed == null) return raw;

    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];

    return '${months[parsed.month - 1]} ${parsed.day}, ${parsed.year}';
  }

  Map<String, dynamic> toJson() => {
        if (id != null) 'id': id,
        'file_name': fileName,
        'document_type': documentType,
        'upload_date': uploadDate,
        'status': status,
        'score': score,
        'findings_count': findingsCount,
        'size_bytes': sizeBytes,
        if (result != null) 'result': result!.toJson(),
      };

  // Data contoh untuk kebutuhan UI/demo.
  // Data ini bukan data asli dari database Django.
  static const samples = <DocumentModel>[
    DocumentModel(
      id: 1,
      fileName: 'Proposal_Thesis.docx',
      documentType: 'proposal',
      uploadDate: 'Oct 6, 2026',
      status: 'completed',
      score: 86,
      findingsCount: 5,
      result: AuditResult.demo,
    ),
    DocumentModel(
      id: 2,
      fileName: 'Thesis_Chapter1.docx',
      documentType: 'skripsi',
      uploadDate: 'Oct 2, 2026',
      status: 'completed',
      score: 72,
      findingsCount: 9,
      result: AuditResult(
        totalScore: 72,
        formatScore: 75,
        semanticScore: 69,
        findings: demoFindings,
      ),
    ),
    DocumentModel(
      id: 3,
      fileName: 'Proposal_Revised.pdf',
      documentType: 'proposal',
      uploadDate: 'Sep 28, 2026',
      status: 'completed',
      score: 91,
      findingsCount: 2,
      result: AuditResult(
        totalScore: 91,
        formatScore: 94,
        semanticScore: 88,
        findings: demoFindings,
      ),
    ),
  ];

  // Dipertahankan sementara agar bagian aplikasi lama
  // yang menggunakan DocumentModel.history tidak langsung rusak.
  static final history = <DocumentModel>[...samples];

  static void addToHistory(DocumentModel document) {
    history.insert(0, document);
  }
}

typedef ThesisDocument = DocumentModel;
