import 'package:flutter/material.dart';

/// Palet warna aplikasi.
/// Gaya: biru langit yang lembut dengan aksen oranye, kartu putih
/// tanpa garis tepi, dan sudut membulat.
@immutable
class AppPalette extends ThemeExtension<AppPalette> {
  const AppPalette({
    required this.primary,
    required this.primaryDark,
    required this.primaryExtraDark,
    required this.primaryLight,
    required this.primarySoft,
    required this.background,
    required this.surface,
    required this.surfaceSecondary,
    required this.card,
    required this.border,
    required this.divider,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.navUnselected,
    required this.onPrimary,
    required this.success,
    required this.successBackground,
    required this.warning,
    required this.warningBackground,
    required this.error,
    required this.errorBackground,
    required this.info,
    required this.infoBackground,
    required this.heroStart,
    required this.heroEnd,
  });

  final Color primary, primaryDark, primaryExtraDark, primaryLight, primarySoft;
  final Color background, surface, surfaceSecondary, card, border, divider;
  final Color textPrimary, textSecondary, textMuted, navUnselected, onPrimary;
  final Color success, successBackground, warning, warningBackground;
  final Color error, errorBackground, info, infoBackground;

  /// Warna gradasi untuk kartu utama (banner, skor, profil).
  final Color heroStart, heroEnd;

  bool get isDark => background.computeLuminance() < 0.1;

  /// Aksen oranye (dipakai juga untuk status "warning").
  Color get accent => warning;
  Color get accentSoft => warningBackground;

  // Nama lama tetap ada agar kode lain tidak rusak.
  Color get secondary => primaryExtraDark;
  Color get secondaryLight => surfaceSecondary;
  Color get purple => info;
  Color get purpleSoft => infoBackground;

  LinearGradient get heroGradient => LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [heroStart, heroEnd],
  );

  static const light = AppPalette(
    primary: Color(0xFF5CC6F7),
    primaryDark: Color(0xFF1E88D6),
    primaryExtraDark: Color(0xFF136DAE),
    primaryLight: Color(0xFFCDEBFC),
    primarySoft: Color(0xFFE8F5FE),
    background: Color(0xFFF4F9FD),
    surface: Color(0xFFFFFFFF),
    surfaceSecondary: Color(0xFFEEF5FB),
    card: Color(0xFFFFFFFF),
    border: Color(0xFFE1ECF5),
    divider: Color(0xFFEDF3F8),
    textPrimary: Color(0xFF1B2A3A),
    textSecondary: Color(0xFF66778A),
    textMuted: Color(0xFF9DABBA),
    navUnselected: Color(0xFF9DABBA),
    onPrimary: Color(0xFFFFFFFF),
    success: Color(0xFF1FA874),
    successBackground: Color(0xFFE3F6EE),
    warning: Color(0xFFF59E1B),
    warningBackground: Color(0xFFFFF1DA),
    error: Color(0xFFE5484D),
    errorBackground: Color(0xFFFDECEC),
    info: Color(0xFF7C6CF2),
    infoBackground: Color(0xFFEFEDFE),
    heroStart: Color(0xFF2F9BE0),
    heroEnd: Color(0xFF1766B0),
  );

  static const dark = AppPalette(
    primary: Color(0xFF5CC6F7),
    primaryDark: Color(0xFF4AB3F0),
    primaryExtraDark: Color(0xFF8AD3FA),
    primaryLight: Color(0xFF1A3A52),
    primarySoft: Color(0xFF142D42),
    background: Color(0xFF0E1620),
    surface: Color(0xFF16212D),
    surfaceSecondary: Color(0xFF1C2937),
    card: Color(0xFF17222F),
    border: Color(0xFF263545),
    divider: Color(0xFF223040),
    textPrimary: Color(0xFFF1F5F9),
    textSecondary: Color(0xFFA9B6C4),
    textMuted: Color(0xFF7D8B9A),
    navUnselected: Color(0xFF7D8B9A),
    onPrimary: Color(0xFF0B1620),
    success: Color(0xFF4ADE9B),
    successBackground: Color(0xFF123A2A),
    warning: Color(0xFFFBB54A),
    warningBackground: Color(0xFF3A2C12),
    error: Color(0xFFF87171),
    errorBackground: Color(0xFF3B1D1D),
    info: Color(0xFFA79BFA),
    infoBackground: Color(0xFF2A2550),
    heroStart: Color(0xFF1F6FA8),
    heroEnd: Color(0xFF14456E),
  );

  @override
  AppPalette copyWith({
    Color? primary,
    Color? primaryDark,
    Color? primaryExtraDark,
    Color? primaryLight,
    Color? primarySoft,
    Color? background,
    Color? surface,
    Color? surfaceSecondary,
    Color? card,
    Color? border,
    Color? divider,
    Color? textPrimary,
    Color? textSecondary,
    Color? textMuted,
    Color? navUnselected,
    Color? onPrimary,
    Color? success,
    Color? successBackground,
    Color? warning,
    Color? warningBackground,
    Color? error,
    Color? errorBackground,
    Color? info,
    Color? infoBackground,
    Color? heroStart,
    Color? heroEnd,
  }) => AppPalette(
    primary: primary ?? this.primary,
    primaryDark: primaryDark ?? this.primaryDark,
    primaryExtraDark: primaryExtraDark ?? this.primaryExtraDark,
    primaryLight: primaryLight ?? this.primaryLight,
    primarySoft: primarySoft ?? this.primarySoft,
    background: background ?? this.background,
    surface: surface ?? this.surface,
    surfaceSecondary: surfaceSecondary ?? this.surfaceSecondary,
    card: card ?? this.card,
    border: border ?? this.border,
    divider: divider ?? this.divider,
    textPrimary: textPrimary ?? this.textPrimary,
    textSecondary: textSecondary ?? this.textSecondary,
    textMuted: textMuted ?? this.textMuted,
    navUnselected: navUnselected ?? this.navUnselected,
    onPrimary: onPrimary ?? this.onPrimary,
    success: success ?? this.success,
    successBackground: successBackground ?? this.successBackground,
    warning: warning ?? this.warning,
    warningBackground: warningBackground ?? this.warningBackground,
    error: error ?? this.error,
    errorBackground: errorBackground ?? this.errorBackground,
    info: info ?? this.info,
    infoBackground: infoBackground ?? this.infoBackground,
    heroStart: heroStart ?? this.heroStart,
    heroEnd: heroEnd ?? this.heroEnd,
  );

  @override
  AppPalette lerp(ThemeExtension<AppPalette>? other, double t) {
    if (other is! AppPalette) return this;
    Color l(Color a, Color b) => Color.lerp(a, b, t)!;
    return AppPalette(
      primary: l(primary, other.primary),
      primaryDark: l(primaryDark, other.primaryDark),
      primaryExtraDark: l(primaryExtraDark, other.primaryExtraDark),
      primaryLight: l(primaryLight, other.primaryLight),
      primarySoft: l(primarySoft, other.primarySoft),
      background: l(background, other.background),
      surface: l(surface, other.surface),
      surfaceSecondary: l(surfaceSecondary, other.surfaceSecondary),
      card: l(card, other.card),
      border: l(border, other.border),
      divider: l(divider, other.divider),
      textPrimary: l(textPrimary, other.textPrimary),
      textSecondary: l(textSecondary, other.textSecondary),
      textMuted: l(textMuted, other.textMuted),
      navUnselected: l(navUnselected, other.navUnselected),
      onPrimary: l(onPrimary, other.onPrimary),
      success: l(success, other.success),
      successBackground: l(successBackground, other.successBackground),
      warning: l(warning, other.warning),
      warningBackground: l(warningBackground, other.warningBackground),
      error: l(error, other.error),
      errorBackground: l(errorBackground, other.errorBackground),
      info: l(info, other.info),
      infoBackground: l(infoBackground, other.infoBackground),
      heroStart: l(heroStart, other.heroStart),
      heroEnd: l(heroEnd, other.heroEnd),
    );
  }
}

extension AppPaletteContext on BuildContext {
  AppPalette get appColors =>
      Theme.of(this).extension<AppPalette>() ?? AppPalette.light;
}

class AppTheme {
  static ThemeData get lightTheme => _build(AppPalette.light, Brightness.light);
  static ThemeData get darkTheme => _build(AppPalette.dark, Brightness.dark);
  static ThemeData get light => lightTheme;

  static ThemeData _build(AppPalette palette, Brightness brightness) {
    final isDark = brightness == Brightness.dark;
    final scheme = ColorScheme(
      brightness: brightness,
      primary: palette.primaryDark,
      onPrimary: palette.onPrimary,
      primaryContainer: palette.primarySoft,
      onPrimaryContainer: palette.textPrimary,
      secondary: palette.warning,
      onSecondary: palette.onPrimary,
      secondaryContainer: palette.warningBackground,
      onSecondaryContainer: palette.textPrimary,
      error: palette.error,
      onError: palette.onPrimary,
      surface: palette.surface,
      onSurface: palette.textPrimary,
      onSurfaceVariant: palette.textSecondary,
      outline: palette.border,
      outlineVariant: palette.divider,
      shadow: Colors.black,
      scrim: Colors.black,
      inverseSurface: palette.textPrimary,
      onInverseSurface: palette.surface,
      inversePrimary: palette.primaryDark,
      surfaceTint: Colors.transparent,
    );
    final textTheme = isDark
        ? Typography.material2021().white
        : Typography.material2021().black;

    const pill = StadiumBorder();

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      extensions: <ThemeExtension<dynamic>>[palette],
      scaffoldBackgroundColor: palette.background,
      dividerColor: palette.divider,
      hintColor: palette.textMuted,
      iconTheme: IconThemeData(color: palette.textSecondary),
      textTheme: textTheme.apply(
        bodyColor: palette.textPrimary,
        displayColor: palette.textPrimary,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: palette.background,
        foregroundColor: palette.textPrimary,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: palette.textPrimary,
          fontSize: 17,
          fontWeight: FontWeight.w700,
        ),
      ),
      cardTheme: CardThemeData(
        color: palette.card,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: isDark ? BorderSide(color: palette.border) : BorderSide.none,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: isDark ? palette.surfaceSecondary : palette.surface,
        hintStyle: TextStyle(color: palette.textMuted, fontSize: 13),
        prefixIconColor: palette.textMuted,
        suffixIconColor: palette.textMuted,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 16,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: palette.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: palette.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: palette.primaryDark, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: palette.error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: palette.error, width: 1.5),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: palette.primaryDark,
          foregroundColor: palette.onPrimary,
          disabledBackgroundColor: palette.primaryLight,
          disabledForegroundColor: palette.textMuted,
          elevation: 0,
          minimumSize: const Size.fromHeight(54),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
          shape: pill,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: palette.textPrimary,
          minimumSize: const Size.fromHeight(50),
          side: BorderSide(color: palette.textPrimary.withValues(alpha: .7)),
          textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          shape: pill,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: palette.primaryDark,
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: palette.card,
        selectedColor: palette.primaryDark,
        side: BorderSide(color: palette.border),
        shape: pill,
        showCheckmark: false,
        labelStyle: TextStyle(color: palette.textPrimary, fontSize: 12),
        secondaryLabelStyle: TextStyle(color: palette.onPrimary, fontSize: 12),
      ),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.selected)
              ? Colors.white
              : palette.textMuted,
        ),
        trackColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.selected)
              ? palette.primaryDark
              : palette.surfaceSecondary,
        ),
        trackOutlineColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.selected)
              ? Colors.transparent
              : palette.border,
        ),
      ),
      listTileTheme: ListTileThemeData(
        iconColor: palette.textSecondary,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: palette.surface,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        titleTextStyle: TextStyle(
          color: palette.textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w700,
        ),
        contentTextStyle: TextStyle(color: palette.textSecondary),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: palette.primaryDark,
        linearTrackColor: palette.primaryLight,
        circularTrackColor: palette.primaryLight,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: palette.textPrimary,
        contentTextStyle: TextStyle(color: palette.background),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    );
  }
}
