import 'audit_result.dart';

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

  String get name => fileName;
  String get type => documentType;
  String get displayDocumentType {
    switch (documentType.toLowerCase()) {
      case 'skripsi':
      case 'thesis': return 'Thesis';
      case 'proposal': return 'Proposal';
      case 'karya_tulis_ilmiah':
      case 'research paper': return 'Research Paper';
      case 'laporan_penelitian':
      case 'research report': return 'Research Report';
      default: return documentType;
    }
  }
  String get date => uploadDate;
  int get findings => findingsCount;
  String get displayStatus => status == 'completed' ? (score >= 90 ? 'Excellent' : score >= 75 ? 'Good' : 'Needs improvement') : status == 'processing' ? 'Processing' : status == 'failed' ? 'Failed' : status;

  factory DocumentModel.fromJson(Map<String, dynamic> json) => DocumentModel(
    id: (json['id'] as num?)?.toInt() ?? (json['document_id'] as num?)?.toInt(),
    fileName: (json['file_name'] ?? json['fileName'] ?? '') as String,
    documentType: (json['document_type'] ?? json['documentType'] ?? '') as String,
    uploadDate: (json['upload_date'] ?? json['uploadDate'] ?? '') as String,
    status: (json['status'] ?? 'processing') as String,
    score: (json['score'] as num?)?.toInt() ?? (json['total_score'] as num?)?.toInt() ?? 0,
    findingsCount: (json['findings_count'] as num?)?.toInt() ?? 0,
    sizeBytes: (json['size_bytes'] as num?)?.toInt() ?? 0,
    result: json['result'] is Map<String, dynamic>
        ? AuditResult.fromJson(json['result'] as Map<String, dynamic>)
        : null,
  );

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

  static const samples = <DocumentModel>[
    DocumentModel(id: 1, fileName: 'Proposal_Thesis.docx', documentType: 'proposal', uploadDate: 'Oct 6, 2026', status: 'completed', score: 86, findingsCount: 5, result: AuditResult.demo),
    DocumentModel(id: 2, fileName: 'Thesis_Chapter1.docx', documentType: 'skripsi', uploadDate: 'Oct 2, 2026', status: 'completed', score: 72, findingsCount: 9, result: AuditResult(totalScore: 72, formatScore: 75, semanticScore: 69, findings: demoFindings)),
    DocumentModel(id: 3, fileName: 'Proposal_Revised.pdf', documentType: 'proposal', uploadDate: 'Sep 28, 2026', status: 'completed', score: 91, findingsCount: 2, result: AuditResult(totalScore: 91, formatScore: 94, semanticScore: 88, findings: demoFindings)),
  ];

  static final history = <DocumentModel>[...samples];
  static void addToHistory(DocumentModel document) => history.insert(0, document);
}

typedef ThesisDocument = DocumentModel;
