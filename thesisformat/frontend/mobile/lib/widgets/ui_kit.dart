import 'package:flutter/material.dart';

import '../models/document_type.dart';
import '../theme/app_theme.dart';

/// Lebar maksimum konten agar tampilan tetap seperti aplikasi mobile
/// saat dibuka di browser (flutter run -d chrome).
class MobileFrame extends StatelessWidget {
  const MobileFrame({super.key, required this.child, this.maxWidth = 560});

  final Widget child;
  final double maxWidth;

  @override
  Widget build(BuildContext context) => Align(
    alignment: Alignment.topCenter,
    child: ConstrainedBox(
      constraints: BoxConstraints(maxWidth: maxWidth),
      child: child,
    ),
  );
}

/// Kartu putih dengan sudut membulat dan bayangan lembut.
class SoftCard extends StatelessWidget {
  const SoftCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
    this.color,
    this.gradient,
    this.radius = 20,
    this.borderColor,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final Color? color;
  final Gradient? gradient;
  final double radius;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final shape = BorderRadius.circular(radius);
    final plain = gradient == null && color == null;
    final border = borderColor ?? (c.isDark && plain ? c.border : null);

    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: shape,
        boxShadow: c.isDark || !plain
            ? null
            : [
                BoxShadow(
                  color: c.primaryDark.withValues(alpha: .07),
                  blurRadius: 22,
                  offset: const Offset(0, 8),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: shape,
        clipBehavior: Clip.antiAlias,
        child: Ink(
          decoration: BoxDecoration(
            color: gradient == null ? (color ?? c.card) : null,
            gradient: gradient,
            borderRadius: shape,
            border: border == null ? null : Border.all(color: border, width: 1.3),
          ),
          child: InkWell(
            onTap: onTap,
            child: Padding(padding: padding, child: child),
          ),
        ),
      ),
    );
  }
}

/// Chip berbentuk pil, dipakai untuk filter dan pilihan.
class PillChip extends StatelessWidget {
  const PillChip({
    super.key,
    required this.label,
    required this.selected,
    required this.onTap,
    this.icon,
    this.color,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;
  final IconData? icon;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final accent = color ?? c.primaryDark;
    final onAccent = color == null ? c.onPrimary : Colors.white;

    return Material(
      color: selected ? accent : c.card,
      shape: StadiumBorder(
        side: BorderSide(color: selected ? accent : c.border),
      ),
      child: InkWell(
        customBorder: const StadiumBorder(),
        onTap: onTap,
        child: Padding(
          padding: EdgeInsets.fromLTRB(icon == null ? 16 : 7, 7, 16, 7),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    color: selected
                        ? Colors.white.withValues(alpha: .25)
                        : accent.withValues(alpha: .12),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    icon,
                    size: 14,
                    color: selected ? onAccent : accent,
                  ),
                ),
                const SizedBox(width: 7),
              ],
              Text(
                label,
                style: TextStyle(
                  color: selected ? onAccent : c.textPrimary,
                  fontWeight: FontWeight.w600,
                  fontSize: 12.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Judul bagian dengan tautan aksi di sebelah kanan.
class SectionHeader extends StatelessWidget {
  const SectionHeader({
    super.key,
    required this.title,
    this.action,
    this.onTap,
  });

  final String title;
  final String? action;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Expanded(
        child: Text(
          title,
          style: TextStyle(
            color: context.appColors.textPrimary,
            fontSize: 17,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      if (action != null)
        TextButton(
          onPressed: onTap,
          style: TextButton.styleFrom(
            visualDensity: VisualDensity.compact,
            textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
          ),
          child: Text(action!),
        ),
    ],
  );
}

/// Cincin skor 0-100.
class ScoreRing extends StatelessWidget {
  const ScoreRing({
    super.key,
    required this.score,
    this.size = 120,
    this.stroke = 10,
    this.color,
    this.trackColor,
    this.textColor,
    this.caption = '/100',
  });

  final int score;
  final double size;
  final double stroke;
  final Color? color;
  final Color? trackColor;
  final Color? textColor;
  final String? caption;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final value = score.clamp(0, 100);
    final text = textColor ?? c.textPrimary;

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox.expand(
            child: CircularProgressIndicator(
              value: value / 100,
              strokeWidth: stroke,
              strokeCap: StrokeCap.round,
              color: color ?? scoreColor(context, value),
              backgroundColor: trackColor ?? c.surfaceSecondary,
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '$value',
                style: TextStyle(
                  color: text,
                  fontSize: size * (caption == null ? .32 : .28),
                  fontWeight: FontWeight.w800,
                  height: 1.1,
                ),
              ),
              if (caption != null)
                Text(
                  caption!,
                  style: TextStyle(
                    color: text.withValues(alpha: .7),
                    fontSize: (size * .1).clamp(9, 13).toDouble(),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Warna sesuai tingkat skor.
Color scoreColor(BuildContext context, int score) {
  final c = context.appColors;
  if (score >= 90) return c.success;
  if (score >= 75) return c.primaryDark;
  return c.warning;
}

Color scoreBackground(BuildContext context, int score) {
  final c = context.appColors;
  if (score >= 90) return c.successBackground;
  if (score >= 75) return c.primarySoft;
  return c.warningBackground;
}

/// Ikon dan warna untuk tiap jenis dokumen.
class DocTypeStyle {
  const DocTypeStyle(this.icon, this.color);

  final IconData icon;
  final Color color;

  Color background(BuildContext context) =>
      color.withValues(alpha: context.appColors.isDark ? .2 : .12);

  static DocTypeStyle of(BuildContext context, String rawType) {
    final c = context.appColors;
    return switch (DocumentType.fromRaw(rawType)?.id) {
      'praktik' => DocTypeStyle(Icons.science_outlined, c.primaryDark),
      'pkl' => DocTypeStyle(Icons.work_outline_rounded, c.warning),
      'tugas_akhir' => DocTypeStyle(Icons.school_outlined, c.info),
      'proposal_pengabdian' => DocTypeStyle(
        Icons.volunteer_activism_outlined,
        c.success,
      ),
      'proposal_penelitian' => DocTypeStyle(
        Icons.lightbulb_outline_rounded,
        c.isDark ? const Color(0xFF2DD4BF) : const Color(0xFF0F9F8F),
      ),
      'makalah_ilmiah' => DocTypeStyle(
        Icons.article_outlined,
        c.isDark ? const Color(0xFFF472B6) : const Color(0xFFDB2777),
      ),
      _ => DocTypeStyle(Icons.description_outlined, c.primaryDark),
    };
  }
}

/// Kotak ikon berwarna untuk jenis dokumen.
class DocTypeIcon extends StatelessWidget {
  const DocTypeIcon({super.key, required this.type, this.size = 46});

  final String type;
  final double size;

  @override
  Widget build(BuildContext context) {
    final style = DocTypeStyle.of(context, type);
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: style.background(context),
        borderRadius: BorderRadius.circular(size * .32),
      ),
      child: Icon(style.icon, color: style.color, size: size * .5),
    );
  }
}

/// Ilustrasi sederhana: gumpalan warna, kertas dokumen, dan lencana.
/// Dibuat dari bentuk dasar, tanpa aset gambar.
class BlobIllustration extends StatelessWidget {
  const BlobIllustration({
    super.key,
    this.size = 160,
    this.icon = Icons.fact_check_rounded,
    this.badgeIcon = Icons.check_rounded,
    this.blobColor,
    this.badgeColor,
  });

  final double size;
  final IconData icon;
  final IconData badgeIcon;
  final Color? blobColor;
  final Color? badgeColor;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = size;

    Widget line(double width) => Container(
      width: width,
      height: s * .032,
      decoration: BoxDecoration(
        color: c.primaryLight,
        borderRadius: BorderRadius.circular(s),
      ),
    );

    Widget dot(double d, Color color) => Container(
      width: d,
      height: d,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );

    return SizedBox(
      width: s,
      height: s,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned(
            left: s * .06,
            top: s * .08,
            child: Container(
              width: s * .88,
              height: s * .84,
              decoration: BoxDecoration(
                color: blobColor ?? c.primaryLight,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(s * .5),
                  topRight: Radius.circular(s * .36),
                  bottomLeft: Radius.circular(s * .34),
                  bottomRight: Radius.circular(s * .5),
                ),
              ),
            ),
          ),
          Positioned(
            right: s * .02,
            top: s * .04,
            child: dot(s * .09, c.warning.withValues(alpha: .85)),
          ),
          Positioned(
            left: 0,
            bottom: s * .18,
            child: dot(s * .06, c.primaryDark.withValues(alpha: .45)),
          ),
          Positioned(
            left: s * .27,
            top: s * .19,
            child: Container(
              width: s * .46,
              height: s * .58,
              padding: EdgeInsets.all(s * .055),
              decoration: BoxDecoration(
                color: c.card,
                borderRadius: BorderRadius.circular(s * .07),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: .10),
                    blurRadius: 16,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(icon, color: c.primaryDark, size: s * .13),
                  SizedBox(height: s * .04),
                  line(s * .33),
                  SizedBox(height: s * .03),
                  line(s * .26),
                  SizedBox(height: s * .03),
                  line(s * .31),
                  SizedBox(height: s * .03),
                  line(s * .18),
                ],
              ),
            ),
          ),
          Positioned(
            right: s * .12,
            bottom: s * .13,
            child: Container(
              width: s * .21,
              height: s * .21,
              decoration: BoxDecoration(
                color: badgeColor ?? c.warning,
                shape: BoxShape.circle,
                border: Border.all(color: c.surface, width: 3),
              ),
              child: Icon(badgeIcon, color: Colors.white, size: s * .11),
            ),
          ),
        ],
      ),
    );
  }
}

/// Tampilan kosong / error yang ramah.
class EmptyState extends StatelessWidget {
  const EmptyState({
    super.key,
    required this.message,
    this.icon = Icons.inbox_outlined,
    this.buttonText,
    this.onPressed,
  });

  final String message;
  final IconData icon;
  final String? buttonText;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    return SoftCard(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 22),
      child: Column(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              color: c.primarySoft,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: c.primaryDark),
          ),
          const SizedBox(height: 12),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(color: c.textSecondary, fontSize: 13),
          ),
          if (buttonText != null && onPressed != null) ...[
            const SizedBox(height: 8),
            TextButton.icon(
              onPressed: onPressed,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: Text(buttonText!),
            ),
          ],
        ],
      ),
    );
  }
}
