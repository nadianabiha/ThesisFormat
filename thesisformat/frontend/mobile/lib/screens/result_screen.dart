import 'package:flutter/material.dart';

import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../theme/app_theme.dart';
import '../widgets/finding_card.dart';
import '../widgets/responsive.dart';
import '../widgets/score_card.dart';
import '../widgets/ui_kit.dart';
import 'upload_screen.dart';

class ResultScreen extends StatefulWidget {
  const ResultScreen({super.key, required this.document});

  final DocumentModel document;

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  /// null = semua temuan; selain itu 'error' / 'warning' / 'success'.
  String? _filter;

  void _reviewAnother() {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute<void>(builder: (_) => const UploadScreen()),
      (route) => route.isFirst,
    );
  }

  Widget _reviewAnotherButton() => ElevatedButton.icon(
    onPressed: _reviewAnother,
    icon: const Icon(Icons.refresh_rounded),
    label: const Text('Review Another Document'),
  );

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final document = widget.document;

    // Gunakan hasil pemeriksaan asli jika tersedia.
    final AuditResult? result = document.result;

    if (result == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Review Results')),
        body: SafeArea(
          child: MobileFrame(
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                const Center(
                  child: BlobIllustration(
                    size: 160,
                    icon: Icons.hourglass_empty_rounded,
                    badgeIcon: Icons.priority_high_rounded,
                  ),
                ),
                const SizedBox(height: 20),
                const Text(
                  'Hasil pemeriksaan belum tersedia.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                Text(
                  'Data hasil pemeriksaan belum diterima aplikasi. '
                  'Silakan periksa koneksi API dan integrasi hasil '
                  'dari server.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: c.textSecondary),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _reviewAnother,
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
    final int? semanticScore = result.hasSemanticScore
        ? result.semanticScore.clamp(0, 100)
        : null;

    int count(String type) =>
        result.findings.where((f) => f.type.toLowerCase() == type).length;

    final filtered = _filter == null
        ? result.findings
        : result.findings
              .where((f) => f.type.toLowerCase() == _filter)
              .toList();

    final verdict = score >= 90
        ? 'Excellent'
        : score >= 75
        ? 'Your document is looking good'
        : 'Your document needs improvement';

    // ---------- Ringkasan skor ----------
    final summary = <Widget>[
      SoftCard(
        gradient: c.heroGradient,
        radius: 24,
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            ScoreRing(
              score: score,
              size: 112,
              stroke: 10,
              color: Colors.white,
              trackColor: Colors.white.withValues(alpha: .25),
              textColor: Colors.white,
            ),
            const SizedBox(width: 18),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    verdict,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                      height: 1.25,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    document.fileName,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: .92),
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${document.displayDocumentType} · ${document.uploadDate}',
                    style: TextStyle(
                      color: Colors.white.withValues(alpha: .8),
                      fontSize: 11.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 14),
      Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: ScoreCard(
              title: 'Document Format',
              score: formatScore,
              icon: Icons.straighten_rounded,
              color: c.primaryDark,
              weight: '40%',
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ScoreCard(
              title: 'Structure & Content',
              score: semanticScore,
              icon: Icons.psychology_alt_outlined,
              color: c.warning,
              weight: '60%',
            ),
          ),
        ],
      ),
    ];

    // ---------- Daftar temuan ----------
    final findings = <Widget>[
      SectionHeader(title: 'Findings (${result.findings.length})'),
      const SizedBox(height: 10),
      if (result.findings.isNotEmpty) ...[
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              PillChip(
                label: 'All',
                selected: _filter == null,
                onTap: () => setState(() => _filter = null),
              ),
              for (final (type, label, color) in [
                ('error', 'Errors', c.error),
                ('warning', 'Warnings', c.warning),
                ('success', 'Passed', c.success),
              ]) ...[
                const SizedBox(width: 8),
                PillChip(
                  label: '$label ${count(type)}',
                  color: color,
                  selected: _filter == type,
                  onTap: () => setState(() => _filter = type),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 12),
      ],
      if (result.findings.isEmpty)
        const EmptyState(
          icon: Icons.inbox_outlined,
          message: 'Belum ada temuan yang diterima dari server.',
        )
      else if (filtered.isEmpty)
        const EmptyState(
          icon: Icons.filter_alt_off_outlined,
          message: 'Tidak ada temuan untuk filter ini.',
        )
      else
        // Tablet: temuan 2 kolom; HP & desktop (kolom kanan): menyesuaikan.
        ResponsiveWrapGrid(
          minItemWidth: 320,
          maxColumns: 2,
          spacing: 10,
          children: [
            for (final finding in filtered) FindingCard(finding: finding),
          ],
        ),
    ];

    final wide = context.isExpanded;

    // ---------- Desktop: dua kolom ----------
    if (wide) {
      return Scaffold(
        appBar: AppBar(title: const Text('Review Results')),
        body: SafeArea(
          child: MobileFrame(
            maxWidth: context.contentMaxWidth,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Kolom kiri: ringkasan skor tetap terlihat.
                SizedBox(
                  width: 400,
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(28, 6, 14, 24),
                    children: [
                      ...summary,
                      const SizedBox(height: 18),
                      _reviewAnotherButton(),
                    ],
                  ),
                ),
                // Kolom kanan: daftar temuan.
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(14, 6, 28, 24),
                    children: findings,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // ---------- HP & tablet: satu kolom ----------
    return Scaffold(
      appBar: AppBar(title: const Text('Review Results')),
      body: SafeArea(
        bottom: false,
        child: MobileFrame(
          maxWidth: context.contentMaxWidth,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(22, 6, 22, 24),
            children: [...summary, const SizedBox(height: 24), ...findings],
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Align(
          heightFactor: 1,
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: context.contentMaxWidth),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(22, 8, 22, 14),
              child: _reviewAnotherButton(),
            ),
          ),
        ),
      ),
    );
  }
}
