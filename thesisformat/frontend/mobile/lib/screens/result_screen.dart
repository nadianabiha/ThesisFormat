import 'package:flutter/material.dart';

import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../models/document_type.dart';
import '../services/api_service.dart';
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

  /// Dokumen yang ditampilkan; diperbarui setelah "Check again".
  late DocumentModel _document = widget.document;
  bool _rechecking = false;

  /// Cek ulang file yang sama tanpa unggah ulang. Mahasiswa bisa
  /// mengganti jenis dokumen dulu (mis. salah pilih Laporan TA).
  Future<void> _recheck() async {
    final id = _document.id;
    if (id == null || _rechecking) return;

    final chosenType = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (_) => _RecheckSheet(
        currentType: DocumentType.fromRaw(_document.documentType)?.id ??
            _document.documentType,
      ),
    );
    if (chosenType == null || !mounted) return;

    setState(() => _rechecking = true);
    final messenger = ScaffoldMessenger.of(context);
    final navigator = Navigator.of(context);
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) => const _CheckingDialog(),
    );

    try {
      final result = await const ApiService().recheckDocument(
        id,
        documentType: chosenType,
      );
      if (!mounted) return;
      navigator.pop(); // tutup dialog
      setState(() {
        _document = _document.copyWith(
          documentType: chosenType,
          result: result,
          score: result.totalScore,
          findingsCount: result.findings.length,
        );
        _filter = null;
      });
      messenger.showSnackBar(
        const SnackBar(content: Text('Check complete. Results updated.')),
      );
    } on SessionExpiredException {
      // Halaman Login dibuka otomatis (lihat main.dart).
    } on ApiException catch (error) {
      if (!mounted) return;
      navigator.pop();
      messenger.showSnackBar(SnackBar(content: Text(error.message)));
    } catch (error) {
      if (!mounted) return;
      navigator.pop();
      messenger.showSnackBar(
        SnackBar(content: Text('Tidak dapat terhubung ke backend: $error')),
      );
    } finally {
      if (mounted) setState(() => _rechecking = false);
    }
  }

  Widget _recheckButton() => OutlinedButton.icon(
    onPressed: _document.id == null || _rechecking ? null : _recheck,
    icon: const Icon(Icons.restart_alt_rounded),
    label: const Text('Check again'),
  );

  void _reviewAnother() {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute<void>(builder: (_) => const UploadScreen()),
      (route) => route.isFirst,
    );
  }

  Widget _reviewAnotherButton() => ElevatedButton.icon(
    onPressed: _rechecking ? null : _reviewAnother,
    icon: const Icon(Icons.upload_file_rounded),
    label: const Text('Review Another Document'),
  );

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final document = _document;

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

    // AI gagal: nilai yang tersimpan hanya nilai format, jadi belum ada
    // nilai akhir. Jangan tampilkan seolah dokumen sudah dinilai lengkap.
    final incomplete = !result.hasSemanticScore;

    final verdict = incomplete
        ? 'Check incomplete'
        : score >= 90
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
              score: incomplete ? null : score,
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
      if (incomplete) ...[
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: c.warningBackground,
            borderRadius: BorderRadius.circular(18),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.warning_amber_rounded, color: c.warning, size: 22),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'The content check did not finish because the AI server was '
                  'busy. Your final score will appear once format and content '
                  'are both checked. Tap "Check again" to try again.',
                  style: TextStyle(
                    color: c.textPrimary,
                    fontSize: 12.5,
                    height: 1.45,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
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
                      _recheckButton(),
                      const SizedBox(height: 10),
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
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _recheckButton(),
                  const SizedBox(height: 8),
                  _reviewAnotherButton(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}


/// Pilihan jenis dokumen sebelum cek ulang.
class _RecheckSheet extends StatefulWidget {
  const _RecheckSheet({required this.currentType});

  final String currentType;

  @override
  State<_RecheckSheet> createState() => _RecheckSheetState();
}

class _RecheckSheetState extends State<_RecheckSheet> {
  late String _selected = widget.currentType;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(22, 0, 22, 18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Check this document again',
              style: TextStyle(
                color: c.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Your uploaded file will be checked again, no need to upload. '
              'Make sure the document type is correct.',
              style: TextStyle(
                color: c.textSecondary,
                fontSize: 12.5,
                height: 1.45,
              ),
            ),
            const SizedBox(height: 14),
            RadioGroup<String>(
              groupValue: _selected,
              onChanged: (value) {
                if (value != null) setState(() => _selected = value);
              },
              child: Column(
                children: [
                  for (final type in DocumentType.all)
                    RadioListTile<String>(
                      value: type.id,
                      contentPadding: EdgeInsets.zero,
                      dense: true,
                      title: Text(
                        type.label,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                      subtitle: type.id == widget.currentType
                          ? const Text('Current type')
                          : null,
                    ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: () => Navigator.of(context).pop(_selected),
              icon: const Icon(Icons.restart_alt_rounded),
              label: const Text('Check again'),
            ),
          ],
        ),
      ),
    );
  }
}

/// Dialog tunggu selama cek ulang (AI bisa sampai sekitar 2 menit).
class _CheckingDialog extends StatelessWidget {
  const _CheckingDialog();

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return PopScope(
      canPop: false,
      child: AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const BlobIllustration(size: 110),
            const SizedBox(height: 14),
            Text(
              'Checking your document...',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: c.textPrimary,
                fontSize: 16,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Format and content are being reviewed. '
              'This can take up to 2 minutes.',
              textAlign: TextAlign.center,
              style: TextStyle(color: c.textSecondary, fontSize: 12.5),
            ),
            const SizedBox(height: 16),
            const LinearProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
