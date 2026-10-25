
import 'package:flutter/material.dart';

import '../models/document_model.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/document_card.dart';
import 'result_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key, this.embedded = false});

  final bool embedded;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final _search = TextEditingController();
  String _filter = 'All';

  final _filters = const ['All', 'Thesis', 'Proposal', 'Reports'];

  late Future<List<DocumentModel>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  void _loadHistory() {
    _historyFuture = const ApiService().getDocumentHistory();
  }

  Future<void> _refreshHistory() async {
    setState(_loadHistory);
    await _historyFuture;
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  bool _matchesType(DocumentModel document) {
    final type = document.documentType.toLowerCase();

    switch (_filter) {
      case 'Thesis':
        return type == 'skripsi' || type == 'thesis';
      case 'Proposal':
        return type == 'proposal';
      case 'Reports':
        return [
          'laporan',
          'laporan_penelitian',
          'research report',
          'karya_tulis_ilmiah',
          'research paper',
        ].contains(type);
      default:
        return true;
    }
  }

  @override
  Widget build(BuildContext context) {
    final query = _search.text.trim().toLowerCase();

    final heading = Padding(
      padding: EdgeInsets.fromLTRB(20, 24, 20, 0),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text(
          'Document History',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
        ),
      ),
    );

    final content = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (!widget.embedded)
          Padding(
            padding: EdgeInsets.fromLTRB(20, 8, 20, 0),
            child: Text(
              'Find your previous document reviews.',
              style: TextStyle(color: context.appColors.textSecondary),
            ),
          ),
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
          child: TextField(
            controller: _search,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(
              hintText: 'Search documents...',
              prefixIcon: Icon(Icons.search_rounded),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 14, 20, 0),
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _filters.map((filter) {
              final selected = _filter == filter;

              return ChoiceChip(
                label: Text(
                  filter,
                  style: TextStyle(
                    color: selected ? context.appColors.primaryExtraDark : context.appColors.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                selected: selected,
                onSelected: (_) => setState(() => _filter = filter),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 12),
        Expanded(
          child: FutureBuilder<List<DocumentModel>>(
            future: _historyFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return Center(
                  child: CircularProgressIndicator(),
                );
              }

              if (snapshot.hasError) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.cloud_off_outlined,
                          size: 42,
                          color: context.appColors.textSecondary,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Gagal memuat riwayat dari server.',
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${snapshot.error}',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: context.appColors.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () {
                            setState(_loadHistory);
                          },
                          child: Text('Coba lagi'),
                        ),
                      ],
                    ),
                  ),
                );
              }

              final allDocuments = snapshot.data ?? <DocumentModel>[];

              final documents = allDocuments.where((document) {
                final matchesName =
                    document.fileName.toLowerCase().contains(query);

                return matchesName && _matchesType(document);
              }).toList();

              if (documents.isEmpty) {
                return RefreshIndicator(
                  onRefresh: _refreshHistory,
                  child: ListView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.only(top: 50),
                    children: [
                      Icon(
                        Icons.history_rounded,
                        color: context.appColors.textSecondary,
                        size: 40,
                      ),
                      SizedBox(height: 12),
                      Center(
                        child: Text(
                          'Belum ada dokumen yang ditemukan.',
                          style: TextStyle(
                            color: context.appColors.textSecondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }

              return RefreshIndicator(
                onRefresh: _refreshHistory,
                child: ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                  children: [
                    Text(
                      '${documents.length} documents',
                      style: TextStyle(
                        color: context.appColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 10),
                    ...documents.map(
                      (document) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: DocumentCard(
                          document: document,
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute<void>(
                                builder: (_) =>
                                    ResultScreen(document: document),
                              ),
                            );
                          },
                        ),
                      ),
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
      return Column(
        children: [
          heading,
          Expanded(child: content),
        ],
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Document History')),
      body: SafeArea(child: content),
    );
  }
}
