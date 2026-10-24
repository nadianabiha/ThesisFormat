
class Finding {
  const Finding({
    required this.type,
    required this.title,
    required this.location,
    required this.detail,
  });

  final String type;
  final String title;
  final String location;
  final String detail;

  factory Finding.fromJson(Map<String, dynamic> json) {
    final rawStatus = (json['status'] ?? json['type'] ?? 'warning')
        .toString()
        .toLowerCase();

    final type = switch (rawStatus) {
      'failed' || 'error' => 'error',
      'passed' || 'success' => 'success',
      'pending' || 'warning' => 'warning',
      _ => 'warning',
    };

    return Finding(
      type: type,
      title: (json['title'] ??
              json['rule_key'] ??
              'Temuan pemeriksaan')
          .toString()
          .replaceAll('_', ' '),
      location: (json['location'] ?? '').toString(),
      detail: (json['detail'] ??
              json['message'] ??
              'Tidak ada detail tambahan.')
          .toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type,
        'title': title,
        'location': location,
        'detail': detail,
      };
}

class AuditResult {
  const AuditResult({
    required this.totalScore,
    required this.formatScore,
    required this.semanticScore,
    required this.findings,
  });

  final int totalScore;
  final int formatScore;
  final int semanticScore;
  final List<Finding> findings;

  static int _scoreFromFindings(List<dynamic> items) {
    var passed = 0;
    var failed = 0;

    for (final item in items) {
      if (item is! Map) continue;

      final status = (item['status'] ?? '').toString().toLowerCase();

      if (status == 'passed' || status == 'success') {
        passed++;
      } else if (status == 'failed' || status == 'error') {
        failed++;
      }
    }

    final checked = passed + failed;
    if (checked == 0) return 0;

    return ((passed / checked) * 100).round().clamp(0, 100);
  }

  factory AuditResult.fromBackend({
    required List<dynamic> jalurAFindings,
    required List<dynamic> jalurBFindings,
  }) {
    final all = <dynamic>[
      ...jalurAFindings,
      ...jalurBFindings,
    ];

    final formatScore = _scoreFromFindings(jalurAFindings);
    final semanticScore = _scoreFromFindings(jalurBFindings);

    final availableScores = <int>[
      if (jalurAFindings.isNotEmpty) formatScore,
      if (jalurBFindings.isNotEmpty) semanticScore,
    ];

    final totalScore = availableScores.isEmpty
        ? 0
        : (availableScores.reduce((a, b) => a + b) /
                availableScores.length)
            .round();

    return AuditResult(
      totalScore: totalScore,
      formatScore: formatScore,
      semanticScore: semanticScore,
      findings: all
          .whereType<Map>()
          .map((item) => Finding.fromJson(
                Map<String, dynamic>.from(item),
              ))
          .toList(),
    );
  }

  factory AuditResult.fromJson(Map<String, dynamic> json) {
    final rawFindings = json['findings'] as List? ?? const [];

    return AuditResult(
      totalScore: (json['total_score'] ??
              json['totalScore'] ??
              json['score'] ??
              0) is num
          ? ((json['total_score'] ??
                      json['totalScore'] ??
                      json['score'] ??
                      0) as num)
              .toInt()
          : 0,
      formatScore: (json['format_score'] ?? json['formatScore'] ?? 0) is num
          ? ((json['format_score'] ?? json['formatScore'] ?? 0) as num)
              .toInt()
          : 0,
      semanticScore:
          (json['semantic_score'] ?? json['semanticScore'] ?? 0) is num
              ? ((json['semantic_score'] ??
                      json['semanticScore'] ??
                      0) as num)
                  .toInt()
              : 0,
      findings: rawFindings
          .whereType<Map>()
          .map((item) => Finding.fromJson(
                Map<String, dynamic>.from(item),
              ))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'total_score': totalScore,
        'format_score': formatScore,
        'semantic_score': semanticScore,
        'findings': findings.map((item) => item.toJson()).toList(),
      };

  // Data contoh untuk kebutuhan UI saja.
  static const demo = AuditResult(
    totalScore: 86,
    formatScore: 92,
    semanticScore: 82,
    findings: demoFindings,
  );
}

// Data demo hanya untuk tampilan contoh,
// bukan untuk hasil pemeriksaan dokumen asli.
const demoFindings = <Finding>[
  Finding(
    type: 'error',
    title: 'Left margin is incorrect',
    location: 'Halaman 4',
    detail: '3.5 cm; it should be 4 cm',
  ),
  Finding(
    type: 'warning',
    title: 'Citation missing from the bibliography',
    location: 'BAB II, halaman 13',
    detail: 'Check the bibliography.',
  ),
  Finding(
    type: 'warning',
    title: 'Foreign term is not italicized',
    location: 'BAB III, halaman 25',
    detail: 'Italicize the foreign term.',
  ),
  Finding(
    type: 'success',
    title: 'Font size is correct',
    location: 'Entire document',
    detail: 'The font size follows the guidelines.',
  ),
];
