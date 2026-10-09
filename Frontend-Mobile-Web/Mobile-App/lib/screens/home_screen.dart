import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../services/auth_service.dart';
import '../theme/app_theme.dart';
import 'history_screen.dart';
import 'login_screen.dart';
import 'profile_screen.dart';
import 'result_screen.dart';
import 'upload_screen.dart';
import '../widgets/app_bottom_nav.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tab = 0;
  void _openUpload() => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => const UploadScreen()));

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: AuthService.instance,
    builder: (context, _) {
      final fullName = AuthService.instance.currentUser?.name.trim() ?? '';
      final welcomeName = fullName.isEmpty ? '' : fullName.split(RegExp(r'\s+')).first;
      final pages = [
        _Dashboard(welcomeName: welcomeName, onUpload: _openUpload, onHistory: () => setState(() => _tab = 1)),
        const HistoryScreen(embedded: true),
        ProfileScreen(embedded: true, onLogout: () {
          AuthService.instance.logout();
          Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute<void>(builder: (_) => const LoginScreen()), (_) => false);
        }),
      ];
      return Scaffold(
        body: SafeArea(child: IndexedStack(index: _tab, children: pages)),
        bottomNavigationBar: AppBottomNav(selectedIndex: _tab, onSelected: (i) => setState(() => _tab = i)),
      );
    },
  );
}
class _Dashboard extends StatelessWidget {
  const _Dashboard({required this.welcomeName, required this.onUpload, required this.onHistory});
  final String welcomeName;
  final VoidCallback onUpload;
  final VoidCallback onHistory;

  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.fromLTRB(22, 18, 22, 28), children: [
    Row(children: [
      Container(width: 44, height: 44, decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(14)), child: const Icon(Icons.auto_stories_rounded, color: AppColors.primary)),
      const SizedBox(width: 12),
      const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('ThesisFormat', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w800, fontSize: 17)),
        Text('Academic writing assistant', style: TextStyle(color: AppColors.textSecondary, fontSize: 11)),
      ])),
      IconButton(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('You have no new notifications.'))), icon: const Icon(Icons.notifications_none_rounded)),
    ]),
    const SizedBox(height: 28),
    Text(welcomeName.isEmpty ? 'Welcome' : 'Welcome, $welcomeName', style: const TextStyle(color: AppColors.textPrimary, fontSize: 24, fontWeight: FontWeight.w800, letterSpacing: -.4)),
    const SizedBox(height: 7),
    const Text('Review your document before your next advising session.', style: TextStyle(color: AppColors.textSecondary, fontSize: 14)),
    const SizedBox(height: 23),
    Material(color: AppColors.secondary, borderRadius: BorderRadius.circular(20), child: InkWell(
      borderRadius: BorderRadius.circular(20), onTap: onUpload,
      child: Padding(padding: const EdgeInsets.all(20), child: Row(children: [
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('Review a New Document', style: TextStyle(color: AppColors.primaryDark, fontSize: 18, fontWeight: FontWeight.w800)),
          const SizedBox(height: 6),
          const Text('Upload a PDF or DOCX to get a formatting summary.', style: TextStyle(color: AppColors.primaryDark, height: 1.45, fontSize: 12)),
          const SizedBox(height: 15),
          Container(padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 9), decoration: BoxDecoration(color: AppColors.primaryDark, borderRadius: BorderRadius.circular(11)), child: const Row(mainAxisSize: MainAxisSize.min, children: [Text('Start review', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 12)), SizedBox(width: 7), Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 16)])),
        ])),
        const SizedBox(width: 12),
        Container(width: 56, height: 56, decoration: BoxDecoration(color: AppColors.primaryDark.withValues(alpha: .10), borderRadius: BorderRadius.circular(18)), child: const Icon(Icons.upload_file_rounded, color: AppColors.primaryDark, size: 30)),
      ])),
    )),
    const SizedBox(height: 27),
    _SectionTitle(title: 'Latest Review', action: 'View result', onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ResultScreen(document: ThesisDocument.samples[0])))),
    const SizedBox(height: 12),
    _LastAudit(onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ResultScreen(document: ThesisDocument.samples[0])))),
    const SizedBox(height: 27),
    _SectionTitle(title: 'Document History', action: 'View all', onTap: onHistory),
    const SizedBox(height: 12),
    ...ThesisDocument.history.map((d) => Padding(padding: const EdgeInsets.only(bottom: 10), child: _DocumentRow(document: d))),
  ]);
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title, this.action, this.onTap});
  final String title;
  final String? action;
  final VoidCallback? onTap;
  @override
  Widget build(BuildContext context) => Row(children: [
    Expanded(child: Text(title, style: const TextStyle(color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.w800))),
    if (action != null) TextButton(onPressed: onTap, child: Text(action!)),
  ]);
}

class _LastAudit extends StatelessWidget {
  const _LastAudit({required this.onTap});
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Card(child: InkWell(borderRadius: BorderRadius.circular(16), onTap: onTap, child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
    Row(children: [
      Container(width: 42, height: 42, decoration: BoxDecoration(color: AppColors.infoBackground, borderRadius: BorderRadius.circular(13)), child: const Icon(Icons.description_outlined, color: AppColors.info)),
      const SizedBox(width: 12),
      const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Proposal_Thesis.docx', style: TextStyle(fontWeight: FontWeight.w700)), SizedBox(height: 4), Text('Proposal · Oct 6, 2026', style: TextStyle(color: AppColors.textSecondary, fontSize: 11))])),
      const Text('86', style: TextStyle(color: AppColors.primary, fontSize: 24, fontWeight: FontWeight.w800)),
      const Text('/100', style: TextStyle(color: AppColors.textSecondary, fontSize: 11)),
    ]),
    const SizedBox(height: 15),
    const ClipRRect(borderRadius: BorderRadius.all(Radius.circular(8)), child: LinearProgressIndicator(value: .86, minHeight: 7)),
    const SizedBox(height: 9),
    const Row(children: [Icon(Icons.info_outline_rounded, size: 15, color: AppColors.warning), SizedBox(width: 6), Text('5 items need attention', style: TextStyle(color: AppColors.textSecondary, fontSize: 11))]),
  ]))));
}

class _DocumentRow extends StatelessWidget {
  const _DocumentRow({required this.document});
  final ThesisDocument document;
  @override
  Widget build(BuildContext context) => Card(child: InkWell(borderRadius: BorderRadius.circular(16), onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ResultScreen(document: document))), child: Padding(padding: const EdgeInsets.all(14), child: Row(children: [
    const Icon(Icons.description_outlined, color: AppColors.secondary),
    const SizedBox(width: 11),
    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(document.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)), const SizedBox(height: 4), Text('${document.displayDocumentType} · ${document.date}', style: const TextStyle(color: AppColors.textSecondary, fontSize: 10))])),
    Text(document.score.toString(), style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w800, fontSize: 18)),
    const Icon(Icons.chevron_right_rounded, color: AppColors.textSecondary),
  ]))));
}
