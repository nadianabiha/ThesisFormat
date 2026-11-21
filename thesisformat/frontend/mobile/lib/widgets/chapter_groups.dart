import 'package:flutter/material.dart';

import '../models/audit_result.dart';
import '../theme/app_theme.dart';
import 'finding_card.dart';
import 'responsive.dart';

/// Label bab dari backend yang bukan judul bab dokumen.
const _wholeDocument = 'Seluruh dokumen';
const _cover = 'Halaman sampul';
const _front = 'Halaman awal';

const _labels = {
  _wholeDocument: 'Entire document',
  _cover: 'Cover page',
  _front: 'Front matter',
};

/// Urutan halaman awal sesuai pedoman (pengesahan, abstrak, ..., daftar isi).
const _frontTitles = [
  'HALAMAN PENGESAHAN', 'LEMBAR PENGESAHAN', 'PENGESAHAN', 'PERNYATAAN',
  'ABSTRAK', 'ABSTRACT', 'RINGKASAN', 'SUMMARY', 'RIWAYAT HIDUP',
  'PERSEMBAHAN', 'MOTTO', 'KATA PENGANTAR', 'PRAKATA', 'SANWACANA',
  'UCAPAN TERIMA KASIH', 'DAFTAR ISI', 'DAFTAR TABEL', 'DAFTAR GAMBAR',
  'DAFTAR LAMPIRAN',
];

String chapterLabel(String raw) =>
    _labels[raw] ?? (raw.isEmpty ? _labels[_wholeDocument]! : raw);

int _romanValue(String text) {
  const values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100};
  var total = 0;
  for (var i = 0; i < text.length; i++) {
    final value = values[text[i]] ?? 0;
    final next = i + 1 < text.length ? values[text[i + 1]] ?? 0 : 0;
    total += value < next ? -value : value;
  }
  return total;
}

/// Urutan tampil: seluruh dokumen, sampul, halaman awal, BAB I, II, ...,
/// daftar pustaka, lampiran. Bab tanpa nomor mengikuti urutan kemunculan.
double chapterRank(String chapter, int firstSeen) {
  final upper = chapter.toUpperCase();
  if (chapter.isEmpty || chapter == _wholeDocument) return 0;
  if (chapter == _cover) return 1;
  if (chapter == _front) return 2;
  final front = _frontTitles.indexWhere(
    (t) => upper == t || upper.startsWith('$t '),
  );
  if (front >= 0) return 3 + front / 100;
  final bab = RegExp(r'^BAB\s+([IVXLC]+|\d+)\b').firstMatch(upper);
  if (bab != null) {
    final raw = bab.group(1)!;
    return 10.0 + (int.tryParse(raw) ?? _romanValue(raw));
  }
  if (upper.startsWith('DAFTAR PUSTAKA')) return 900;
  if (upper.startsWith('LAMPIRAN')) return 950;
  return 500 + firstSeen / 1000;
}

/// Temuan dikelompokkan per bab (sesuai Laporan Perancangan:
/// "daftar kesalahan per bab").
class ChapterGroups extends StatelessWidget {
  const ChapterGroups({super.key, required this.findings});

  final List<Finding> findings;

  @override
  Widget build(BuildContext context) {
    final groups = <String, List<Finding>>{};
    for (final finding in findings) {
      final key = finding.chapter.isEmpty ? _wholeDocument : finding.chapter;
      groups.putIfAbsent(key, () => []).add(finding);
    }
    final keys = groups.keys.toList();
    final firstSeen = {for (final (i, key) in keys.indexed) key: i};
    keys.sort(
      (a, b) => chapterRank(a, firstSeen[a]!).compareTo(
        chapterRank(b, firstSeen[b]!),
      ),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final key in keys) ...[
          _ChapterHeader(title: chapterLabel(key), findings: groups[key]!),
          const SizedBox(height: 10),
          ResponsiveWrapGrid(
            minItemWidth: 320,
            maxColumns: 2,
            spacing: 10,
            children: [
              for (final finding in groups[key]!) FindingCard(finding: finding),
            ],
          ),
          const SizedBox(height: 20),
        ],
      ],
    );
  }
}

class _ChapterHeader extends StatelessWidget {
  const _ChapterHeader({required this.title, required this.findings});

  final String title;
  final List<Finding> findings;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final errors = findings.where((f) => f.type == 'error').length;
    final ok = errors == 0;

    return Row(
      children: [
        Container(
          width: 30,
          height: 30,
          decoration: BoxDecoration(
            color: c.primarySoft.withValues(alpha: .45),
            borderRadius: BorderRadius.circular(9),
          ),
          child: Icon(Icons.menu_book_rounded, size: 17, color: c.primaryDark),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: c.textPrimary,
              fontSize: 14,
              fontWeight: FontWeight.w800,
            ),
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: ok ? c.successBackground : c.errorBackground,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            ok ? 'No errors' : '$errors ${errors == 1 ? 'error' : 'errors'}',
            style: TextStyle(
              color: ok ? c.success : c.error,
              fontSize: 11.5,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ],
    );
  }
}
