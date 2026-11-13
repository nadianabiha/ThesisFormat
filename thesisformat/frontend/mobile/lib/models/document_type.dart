/// Jenis dokumen sesuai Panduan Penulisan Karya Ilmiah Polinela.
/// `id` harus sama dengan Document.DocumentType di backend Django.
class DocumentType {
  const DocumentType(this.id, this.label, [this.aliases = const {}]);

  final String id;
  final String label;

  /// Nilai lama di database yang dianggap jenis ini (dokumen sebelum revisi).
  final Set<String> aliases;

  bool matches(String raw) {
    final value = raw.toLowerCase().trim().replaceAll(RegExp(r'[\s-]'), '_');
    return value == id || aliases.contains(value);
  }

  static const all = <DocumentType>[
    DocumentType('praktik', 'Laporan Praktik', {'praktikum'}),
    DocumentType('pkl', 'Laporan PKL/Magang', {'magang', 'praktik_kerja_lapangan'}),
    DocumentType('tugas_akhir', 'Laporan TA/Skripsi', {'laporan_ta', 'skripsi', 'thesis'}),
    DocumentType('proposal_pengabdian', 'Proposal Pengabdian Masyarakat'),
    DocumentType('proposal_penelitian', 'Proposal Penelitian', {'proposal', 'proposal_ta'}),
    DocumentType('makalah_ilmiah', 'Makalah Ilmiah'),
  ];

  static DocumentType? fromRaw(String raw) {
    for (final type in all) {
      if (type.matches(raw)) return type;
    }
    return null;
  }

  static String labelOf(String raw) => fromRaw(raw)?.label ?? raw;
}
