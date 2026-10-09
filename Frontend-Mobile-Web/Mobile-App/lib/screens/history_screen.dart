import 'package:flutter/material.dart';
import '../models/document_model.dart';
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
  @override
  void dispose() { _search.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final query = _search.text.toLowerCase();
    final documents = ThesisDocument.history.where((d) {
      final matchesName = d.name.toLowerCase().contains(query);
      final matchesType = switch (_filter) {
        'All' => true,
        'Thesis' => d.documentType.toLowerCase() == 'skripsi' || d.documentType.toLowerCase() == 'thesis',
        'Proposal' => d.documentType.toLowerCase() == 'proposal',
        'Reports' => d.documentType.toLowerCase() == 'laporan_penelitian' || d.documentType.toLowerCase() == 'research report' || d.documentType.toLowerCase() == 'karya_tulis_ilmiah' || d.documentType.toLowerCase() == 'research paper',
        _ => true,
      };
      return matchesName && matchesType;
    }).toList();
    final content = ListView(padding: const EdgeInsets.fromLTRB(20, 8, 20, 24), children: [
      if (!widget.embedded) const Text('Find your previous document reviews.', style: TextStyle(color: AppColors.textSecondary)),
      const SizedBox(height: 12),
      TextField(controller: _search, onChanged: (_) => setState(() {}), decoration: const InputDecoration(hintText: 'Search documents...', prefixIcon: Icon(Icons.search_rounded))),
      const SizedBox(height: 14),
      Wrap(spacing: 8, children: _filters.map((f) => ChoiceChip(label: Text(f, style: TextStyle(color: _filter == f ? AppColors.primary : AppColors.textPrimary, fontWeight: FontWeight.w600)), selected: _filter == f, onSelected: (_) => setState(() => _filter = f))).toList()),
      const SizedBox(height: 17),
      Text('${documents.length} documents', style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
      const SizedBox(height: 10),
      if (documents.isEmpty) const Padding(padding: EdgeInsets.only(top: 50), child: Column(children: [Icon(Icons.search_off_rounded, color: AppColors.textSecondary, size: 36), SizedBox(height: 10), Text('No documents found', style: TextStyle(color: AppColors.textSecondary))])),
      ...documents.map((d) => Padding(padding: const EdgeInsets.only(bottom: 10), child: DocumentCard(document: d, onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ResultScreen(document: d)))))),
    ]);
    if (widget.embedded) {
      return Column(children: [
        const Padding(padding: EdgeInsets.fromLTRB(20, 24, 20, 0), child: Align(alignment: Alignment.centerLeft, child: Text('Document History', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800)))),
        Expanded(child: content),
      ]);
    }
    return Scaffold(appBar: AppBar(title: const Text('Document History')), body: content);
  }
}
