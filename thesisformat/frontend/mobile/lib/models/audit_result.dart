class Finding {
  const Finding({required this.type, required this.title, required this.location, required this.detail});

  final String type;
  final String title;
  final String location;
  final String detail;

  factory Finding.fromJson(Map<String, dynamic> json) => Finding(
    type: (json['type'] ?? 'warning') as String,
    title: (json['title'] ?? '') as String,
    location: (json['location'] ?? '') as String,
    detail: (json['detail'] ?? '') as String,
  );

  Map<String, dynamic> toJson() => {
    'type': type,
    'title': title,
    'location': location,
    'detail': detail,
  };
}

const demoFindings = <Finding>[
  Finding(type: 'error', title: 'Left margin is incorrect', location: 'Halaman 4', detail: '3.5 cm; it should be 4 cm'),
  Finding(type: 'warning', title: 'Citation missing from the bibliography', location: 'BAB II, halaman 13', detail: 'Check the bibliography.'),
  Finding(type: 'warning', title: 'Foreign term is not italicized', location: 'BAB III, halaman 25', detail: 'Italicize the foreign term.'),
  Finding(type: 'success', title: 'Font size is correct', location: 'Entire document', detail: 'The font size follows the guidelines.'),
];

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

  factory AuditResult.fromJson(Map<String, dynamic> json) => AuditResult(
    totalScore: ((json['total_score'] ?? json['totalScore'] ?? 0) as num).toInt(),
    formatScore: ((json['format_score'] ?? json['formatScore'] ?? 0) as num).toInt(),
    semanticScore: ((json['semantic_score'] ?? json['semanticScore'] ?? 0) as num).toInt(),
    findings: (json['findings'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(Finding.fromJson)
        .toList(),
  );

  Map<String, dynamic> toJson() => {
    'total_score': totalScore,
    'format_score': formatScore,
    'semantic_score': semanticScore,
    'findings': findings.map((finding) => finding.toJson()).toList(),
  };

  static const demo = AuditResult(
    totalScore: 86,
    formatScore: 92,
    semanticScore: 82,
    findings: demoFindings,
  );
}
