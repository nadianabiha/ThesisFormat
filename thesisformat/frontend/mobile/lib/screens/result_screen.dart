import 'package:flutter/material.dart';

import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../theme/app_theme.dart';
import '../widgets/finding_card.dart';
import '../widgets/score_card.dart';
import 'upload_screen.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({
    super.key,
    required this.document,
  });

  final DocumentModel document;

  @override
  Widget build(BuildContext context) {
    // Gunakan hasil pemeriksaan asli jika tersedia.
    final AuditResult? result = document.result;

    if (result == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Review Results'),
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.hourglass_empty_rounded,
                  size: 56,
                  color: context.appColors.textSecondary,
                ),
                const SizedBox(height: 16),
                const Text(
                  'Hasil pemeriksaan belum tersedia.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Data hasil pemeriksaan belum diterima aplikasi. '
                  'Silakan periksa koneksi API dan integrasi hasil '
                  'dari server.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: context.appColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pushAndRemoveUntil(
                      MaterialPageRoute<void>(
                        builder: (_) => const UploadScreen(),
                      ),
                      (route) => route.isFirst,
                    );
                  },
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('Kembali ke Upload'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final score = result.totalScore.clamp(0, 100);
    final formatScore = result.formatScore.clamp(0, 100);

    // Skor semantik hanya ditampilkan sebagai angka jika tersedia.
    final bool semanticAvailable = result.hasSemanticScore;
    final semanticScore = result.semanticScore.clamp(0, 100);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Review Results'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 6, 20, 28),
        children: [
          Text(
            document.fileName,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            '${document.displayDocumentType} · ${document.uploadDate}',
            style: TextStyle(
              color: context.appColors.textSecondary,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 16),

          // Ringkasan skor
          Card(
            child: Padding(
              padding: const EdgeInsets.all(19),
              child: Column(
                children: [
                  SizedBox(
                    width: 126,
                    height: 126,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        SizedBox(
                          width: 126,
                          height: 126,
                          child: CircularProgressIndicator(
                            value: score / 100,
                            strokeWidth: 10,
                            strokeCap: StrokeCap.round,
                            backgroundColor:
                                context.appColors.secondaryLight,
                          ),
                        ),
                        Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '$score',
                              style: TextStyle(
                                color: context.appColors.textPrimary,
                                fontSize: 38,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            Text(
                              '/100',
                              style: TextStyle(
                                color: context.appColors.textSecondary,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    score >= 90
                        ? 'Excellent'
                        : score >= 75
                            ? 'Your document is looking good'
                            : 'Your document needs improvement',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    'Hasil berdasarkan data pemeriksaan yang diterima.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: context.appColors.textSecondary,
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 18),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: ScoreCard(
                          title: 'Document Format',
                          score: formatScore,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: semanticAvailable
                            ? ScoreCard(
                                title: 'Structure & Content',
                                score: semanticScore,
                              )
                            : _ScoreUnavailableCard(
                                title: 'Structure & Content',
                              ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 23),

          // Daftar temuan pemeriksaan tetap dipertahankan.
          Row(
            children: [
              const Expanded(
                child: Text(
                  'Findings',
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              Text(
                '${result.findings.length} findings',
                style: TextStyle(
                  color: context.appColors.textSecondary,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          if (result.findings.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Text(
                'Belum ada temuan yang diterima dari server.',
                textAlign: TextAlign.center,
              ),
            )
          else
            ...result.findings.map(
              (finding) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: FindingCard(finding: finding),
              ),
            ),

          const SizedBox(height: 10),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute<void>(
                  builder: (_) => const UploadScreen(),
                ),
                (route) => route.isFirst,
              );
            },
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('Review Another Document'),
          ),
        ],
      ),
    );
  }
}

class _ScoreUnavailableCard extends StatelessWidget {
  const _ScoreUnavailableCard({
    required this.title,
  });

  final String title;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              '—',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Skor belum tersedia',
              style: TextStyle(
                color: context.appColors.textSecondary,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }
}