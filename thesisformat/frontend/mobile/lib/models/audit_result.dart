class Finding {
  const Finding({
    required this.type,
    required this.title,
    required this.location,
    required this.detail,
    this.severity = '',
    this.chapter = '',
  });

  final String type;
  final String title;
  final String location;
  final String detail;

  /// Bab tempat temuan, mis. "BAB I PENDAHULUAN", "Halaman sampul", atau
  /// "Seluruh dokumen". Kosong untuk hasil lama sebelum fitur per bab.
  final String chapter;

  /// Tingkat kesalahan temuan AI yang gagal: ringan / sedang / berat.
  /// Kosong untuk temuan format atau temuan yang lulus.
  final String severity;

  factory Finding.fromJson(Map<String, dynamic> json) {
    final rawStatus = (json['status'] ??
            json['result'] ??
            json['type'] ??
            'warning')
        .toString()
        .trim()
        .toLowerCase();

    final type = switch (rawStatus) {
      'failed' || 'fail' || 'error' || 'gagal' => 'error',
      'passed' || 'pass' || 'success' || 'berhasil' || 'lulus' =>
        'success',
      'pending' || 'warning' => 'warning',
      _ => 'warning',
    };

    final title = (json['title'] ??
            json['rule_key'] ??
            json['rule_name'] ??
            json['name'] ??
            json['issue'] ??
            'Temuan pemeriksaan')
        .toString()
        .replaceAll('_', ' ');

    final location = (json['location'] ??
            json['page'] ??
            json['section'] ??
            '')
        .toString();

    final detail = (json['detail'] ??
            json['message'] ??
            json['description'] ??
            json['reason'] ??
            json['issue'] ??
            'Tidak ada detail tambahan.')
        .toString();

    return Finding(
      type: type,
      title: title,
      location: location,
      detail: detail,
      severity: (json['severity'] ?? '').toString().trim().toLowerCase(),
      chapter: (json['chapter'] ?? '').toString().trim(),
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type,
        'title': title,
        'location': location,
        'detail': detail,
        'severity': severity,
        'chapter': chapter,
      };
}

class AuditResult {
  const AuditResult({
    required this.totalScore,
    required this.formatScore,
    required this.semanticScore,
    required this.findings,
    this.hasFormatScore = false,
    this.hasSemanticScore = false,
  });

  final int totalScore;
  final int formatScore;
  final int semanticScore;
  final List<Finding> findings;

  // Menandakan apakah skor memiliki dasar perhitungan yang tersedia.
  final bool hasFormatScore;
  final bool hasSemanticScore;

  factory AuditResult.fromJson(Map<String, dynamic> json) {
    final rawFindings = json['findings'];

    return AuditResult(
      totalScore: (json['total_score'] as num?)?.toInt() ?? 0,
      formatScore: (json['format_score'] as num?)?.toInt() ?? 0,
      semanticScore: (json['semantic_score'] as num?)?.toInt() ?? 0,
      hasFormatScore: json['has_format_score'] == true,
      hasSemanticScore: json['has_semantic_score'] == true,
      findings: rawFindings is List
          ? rawFindings
              .whereType<Map>()
              .map(
                (item) => Finding.fromJson(
                  Map<String, dynamic>.from(item),
                ),
              )
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() => {
        'total_score': totalScore,
        'format_score': formatScore,
        'semantic_score': semanticScore,
        'has_format_score': hasFormatScore,
        'has_semantic_score': hasSemanticScore,
        'findings': findings.map((item) => item.toJson()).toList(),
      };

  static const demo = AuditResult(
    totalScore: 86,
    formatScore: 92,
    semanticScore: 82,
    findings: demoFindings,
    hasFormatScore: true,
    hasSemanticScore: true,
  );
}

const demoFindings = <Finding>[
  Finding(
    type: 'success',
    title: 'Format dokumen',
    location: 'Dokumen',
    detail: 'Format dokumen memenuhi pemeriksaan.',
  ),
];