
import 'package:flutter/material.dart';

import '../models/document_model.dart';
import '../models/document_type.dart';
import '../services/api_service.dart';
import '../widgets/document_card.dart';
import 'result_screen.dart';

class HistoryScreen extends StatefulWidget {
  final bool embedded;

  const HistoryScreen({
    super.key,
    this.embedded = false,
  });

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final TextEditingController _search = TextEditingController();

  String _filter = 'All';

  final List<String> _filters = [
    'All',
    ...DocumentType.all.map((type) => type.label),
  ];

  late Future<List<DocumentModel>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _historyFuture = _loadHistory();
  }

  Future<List<DocumentModel>> _loadHistory() async {
    return const ApiService().getDocumentHistory();
  }

  Future<void> _refreshHistory() async {
    setState(() {
      _historyFuture = _loadHistory();
    });

    await _historyFuture;
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  // Memeriksa jenis dokumen berdasarkan filter yang dipilih.
  bool _matchesType(DocumentModel document) {
    if (_filter == 'All') return true;
    return DocumentType.fromRaw(document.documentType)?.label == _filter;
  }

  // Menerapkan pencarian nama file dan filter jenis dokumen.
  List<DocumentModel> _getFilteredDocuments(
    List<DocumentModel> documents,
  ) {
    final String keyword = _search.text.toLowerCase().trim();

    return documents.where((document) {
      final bool matchesSearch =
          document.fileName.toLowerCase().contains(keyword);

      final bool matchesFilter = _matchesType(document);

      return matchesSearch && matchesFilter;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final Widget content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (!widget.embedded) ...[
          Text(
            'Riwayat Dokumen',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 6),
          Text(
            'Lihat dokumen yang pernah kamu unggah.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 20),
        ],

        // Kolom pencarian dokumen.
        TextField(
          controller: _search,
          onChanged: (_) {
            setState(() {});
          },
          decoration: InputDecoration(
            hintText: 'Cari dokumen...',
            prefixIcon: const Icon(Icons.search),
            suffixIcon: _search.text.isNotEmpty
                ? IconButton(
                    onPressed: () {
                      _search.clear();
                      setState(() {});
                    },
                    icon: const Icon(Icons.close),
                  )
                : null,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Pilihan kategori dokumen.
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: _filters.map((filter) {
              final bool selected = _filter == filter;

              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(filter),
                  selected: selected,
                  onSelected: (_) {
                    setState(() {
                      _filter = filter;
                    });
                  },
                ),
              );
            }).toList(),
          ),
        ),

        const SizedBox(height: 16),

        // Mengambil riwayat dari backend Django.
        Expanded(
          child: FutureBuilder<List<DocumentModel>>(
            future: _historyFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: CircularProgressIndicator(),
                );
              }

              if (snapshot.hasError) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 48,
                          color: Colors.red,
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Gagal memuat riwayat dokumen.',
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(
                          onPressed: () {
                            setState(() {
                              _historyFuture = _loadHistory();
                            });
                          },
                          icon: const Icon(Icons.refresh),
                          label: const Text('Coba Lagi'),
                        ),
                      ],
                    ),
                  ),
                );
              }

              final List<DocumentModel> documents =
                  snapshot.data ?? [];

              final List<DocumentModel> filteredDocuments =
                  _getFilteredDocuments(documents);

              // Tampilan ketika hasil pencarian atau kategori kosong.
              if (filteredDocuments.isEmpty) {
                return RefreshIndicator(
                  onRefresh: _refreshHistory,
                  child: ListView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    children: const [
                      SizedBox(height: 100),
                      Icon(
                        Icons.folder_open,
                        size: 64,
                        color: Colors.grey,
                      ),
                      SizedBox(height: 16),
                      Center(
                        child: Text(
                          'Tidak ada dokumen ditemukan.',
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  ),
                );
              }

              // Daftar dokumen sesuai pencarian dan kategori.
              return RefreshIndicator(
                onRefresh: _refreshHistory,
                child: ListView.builder(
                  physics: const AlwaysScrollableScrollPhysics(),
                  itemCount: filteredDocuments.length,
                  itemBuilder: (context, index) {
                    final DocumentModel document =
                        filteredDocuments[index];

                    return DocumentCard(
                      document: document,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => ResultScreen(
                              document: document,
                            ),
                          ),
                        );
                      },
                    );
                  },
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
      appBar: AppBar(
        title: const Text('Riwayat Dokumen'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: content,
      ),
    );
  }
}
