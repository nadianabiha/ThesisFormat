import 'package:flutter/material.dart';
import '../models/audit_result.dart';
import '../models/document_model.dart';
import '../theme/app_theme.dart';
import '../widgets/finding_card.dart';
import '../widgets/score_card.dart';
import 'upload_screen.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key, required this.document});
  final DocumentModel document;

  @override
  Widget build(BuildContext context) {
    // The result payload comes from the API model; the static result is for the demo flow.
    final result = document.result ?? AuditResult.demo; // TODO: Fetch the result payload from the backend when API integration is enabled.
    return Scaffold(
      appBar: AppBar(title: const Text('Review Results')),
      body: ListView(padding: const EdgeInsets.fromLTRB(20, 6, 20, 28), children: [
        Text(document.fileName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
        const SizedBox(height: 5),
        Text('${document.displayDocumentType} · ${document.uploadDate}', style: TextStyle(color: context.appColors.textSecondary, fontSize: 12)),
        const SizedBox(height: 16),
        Card(child: Padding(padding: const EdgeInsets.all(19), child: Column(children: [
          SizedBox(width: 126, height: 126, child: Stack(alignment: Alignment.center, children: [
            SizedBox(width: 126, height: 126, child: CircularProgressIndicator(value: result.totalScore / 100, strokeWidth: 10, strokeCap: StrokeCap.round, backgroundColor: context.appColors.secondaryLight)),
            Column(mainAxisSize: MainAxisSize.min, children: [Text(result.totalScore.toString(), style: TextStyle(color: context.appColors.textPrimary, fontSize: 38, fontWeight: FontWeight.w800)), Text('/100', style: TextStyle(color: context.appColors.textSecondary, fontSize: 12))]),
          ])),
          const SizedBox(height: 14),
          const Text('Your document is looking good', textAlign: TextAlign.center, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800)),
          const SizedBox(height: 5),
          Text('A few items still need your attention.', textAlign: TextAlign.center, style: TextStyle(color: context.appColors.textSecondary, fontSize: 12)),
          const SizedBox(height: 18),
          Row(children: [
            Expanded(child: ScoreCard(title: 'Document Format', score: result.formatScore)),
            const SizedBox(width: 10),
            Expanded(child: ScoreCard(title: 'Structure & Content', score: result.semanticScore)),
          ]),
        ]))),
        const SizedBox(height: 23),
        Row(children: [
          const Expanded(child: Text('Findings', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800))),
          Text('${result.findings.length} findings', style: TextStyle(color: context.appColors.textSecondary, fontSize: 12)),
        ]),
        const SizedBox(height: 12),
        ...result.findings.map((finding) => Padding(padding: const EdgeInsets.only(bottom: 10), child: FindingCard(finding: finding))),
        const SizedBox(height: 8),
        OutlinedButton(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Semua findings ditampilkan di halaman ini.'))), child: const Text('Lihat Semua Findings')),
        const SizedBox(height: 10),
        ElevatedButton.icon(
          onPressed: () => Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute<void>(builder: (_) => const UploadScreen()), (route) => route.isFirst),
          icon: const Icon(Icons.refresh_rounded),
          label: const Text('Review Another Document'),
        ),
      ]),
    );
  }
}
