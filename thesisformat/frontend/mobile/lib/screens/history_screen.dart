import 'package:flutter/material.dart';

import '../models/document_model.dart';
import '../models/document_type.dart';
import '../services/api_service.dart';
import '../services/document_events.dart';
import '../theme/app_theme.dart';
import '../widgets/document_card.dart';
import '../widgets/responsive.dart';
import '../widgets/ui_kit.dart';
import 'result_screen.dart';

class HistoryScreen extends StatefulWidget {
  final bool embedded;

  const HistoryScreen({super.key, this.embedded = false});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final TextEditingController _search = TextEditingController();

  /// null = semua jenis dokumen.
  String? _filter;

  late Future<List<DocumentModel>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _historyFuture = _loadHistory();
    DocumentEvents.instance.addListener(_onDocumentsChanged);
  }

  // Dipanggil setelah upload berhasil: muat ulang riwayat.
  void _onDocumentsChanged() {
    if (!mounted) return;
    setState(() {
      _historyFuture = _loadHistory();
    });
  }

  Future<List<DocumentModel>> _loadHistory() {
    final future = const ApiService().getDocumentHistory();
    // Error tetap ditampilkan oleh FutureBuilder; ignore() mencegah
    // "unhandled exception" jika layar sudah ditutup sebelum selesai.
    future.ignore();
    return future;
  }

  Future<void> _refreshHistory() async {
    setState(() {
      _historyFuture = _loadHistory();
    });

    try {
      await _historyFuture;
    } catch (_) {
      // Pesan error ditampilkan oleh FutureBuilder.
    }
  }

  @override
  void dispose() {
    DocumentEvents.instance.removeListener(_onDocumentsChanged);
    _search.dispose();
    super.dispose();
  }

  // Memeriksa jenis dokumen berdasarkan filter yang dipilih.
  bool _matchesType(DocumentModel document) {
    if (_filter == null) return true;
    return DocumentType.fromRaw(document.documentType)?.id == _filter;
  }

  // Menerapkan pencarian nama file dan filter jenis dokumen.
  List<DocumentModel> _getFilteredDocuments(List<DocumentModel> documents) {
    final String keyword = _search.text.toLowerCase().trim();

    return documents.where((document) {
      final bool matchesSearch = document.fileName.toLowerCase().contains(
        keyword,
      );

      return matchesSearch && _matchesType(document);
    }).toList();
  }

  Widget _scrollMessage(Widget child) => RefreshIndicator(
    onRefresh: _refreshHistory,
    child: ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.fromLTRB(22, 24, 22, 24),
      children: [child],
    ),
  );

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    final Widget content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.fromLTRB(22, widget.embedded ? 20 : 4, 22, 0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (widget.embedded) ...[
                Text(
                  'History',
                  style: TextStyle(
                    color: c.textPrimary,
                    fontSize: 24,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -.3,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'All documents you have reviewed.',
                  style: TextStyle(color: c.textSecondary, fontSize: 13),
                ),
                const SizedBox(height: 18),
              ],

              // Kolom pencarian dokumen.
              TextField(
                controller: _search,
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  hintText: 'Cari dokumen...',
                  prefixIcon: const Icon(Icons.search_rounded),
                  suffixIcon: _search.text.isNotEmpty
                      ? IconButton(
                          onPressed: () {
                            _search.clear();
                            setState(() {});
                          },
                          icon: const Icon(Icons.close_rounded),
                        )
                      : null,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: BorderSide(color: c.border),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: BorderSide(color: c.border),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: BorderSide(color: c.primaryDark, width: 1.5),
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 14),

        // Pilihan kategori dokumen.
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 22),
          child: Row(
            children: [
              PillChip(
                label: 'All',
                icon: Icons.apps_rounded,
                selected: _filter == null,
                onTap: () => setState(() => _filter = null),
              ),
              for (final type in DocumentType.all) ...[
                const SizedBox(width: 8),
                Builder(
                  builder: (context) {
                    final style = DocTypeStyle.of(context, type.id);
                    return PillChip(
                      label: type.label,
                      icon: style.icon,
                      color: style.color,
                      selected: _filter == type.id,
                      onTap: () => setState(() => _filter = type.id),
                    );
                  },
                ),
              ],
            ],
          ),
        ),

        const SizedBox(height: 6),

        // Mengambil riwayat dari backend Django.
        Expanded(
          child: FutureBuilder<List<DocumentModel>>(
            future: _historyFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }

              if (snapshot.hasError) {
                return _scrollMessage(
                  EmptyState(
                    icon: Icons.cloud_off_rounded,
                    message: 'Gagal memuat riwayat dokumen.',
                    buttonText: 'Coba Lagi',
                    onPressed: () => setState(() {
                      _historyFuture = _loadHistory();
                    }),
                  ),
                );
              }

              final filteredDocuments = _getFilteredDocuments(
                snapshot.data ?? [],
              );

              // Tampilan ketika hasil pencarian atau kategori kosong.
              if (filteredDocuments.isEmpty) {
                return _scrollMessage(
                  const EmptyState(
                    icon: Icons.folder_open_rounded,
                    message: 'Tidak ada dokumen ditemukan.',
                  ),
                );
              }

              // Daftar dokumen sesuai pencarian dan kategori.
              return RefreshIndicator(
                onRefresh: _refreshHistory,
                child: ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(22, 10, 22, 24),
                  children: [
                    Text(
                      '${filteredDocuments.length} documents',
                      style: TextStyle(
                        color: c.textSecondary,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 10),
                    // HP: 1 kolom, tablet: 2 kolom, desktop: 3 kolom.
                    ResponsiveWrapGrid(
                      minItemWidth: 300,
                      maxColumns: 3,
                      spacing: 12,
                      children: [
                        for (final document in filteredDocuments)
                          DocumentCard(
                            document: document,
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute<void>(
                                  builder: (context) =>
                                      ResultScreen(document: document),
                                ),
                              );
                            },
                          ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );

    if (widget.embedded) {
      return content;
    }

    return Scaffold(
      appBar: AppBar(title: const Text('History')),
      body: MobileFrame(maxWidth: context.contentMaxWidth, child: content),
    );
  }
}
