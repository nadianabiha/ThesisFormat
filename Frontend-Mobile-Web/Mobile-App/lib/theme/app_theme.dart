import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFF073B55);
  static const primaryDark = Color(0xFF062F49);
  static const primaryLight = Color(0xFFE4F7F5);
  static const secondary = Color(0xFF55D6CE);
  static const secondaryLight = Color(0xFFE6F9F7);
  static const accent = Color(0xFFFFCF3F);
  static const background = Color(0xFFF5FAFA);
  static const surface = Color(0xFFFFFFFF);
  static const textPrimary = Color(0xFF123249);
  static const textSecondary = Color(0xFF627984);
  static const border = Color(0xFFDCE9E9);
  static const success = Color(0xFF147D78);
  static const successBackground = Color(0xFFE6F9F7);
  static const warning = Color(0xFF062F49);
  static const warningBackground = Color(0xFFFFF6D9);
  static const error = Color(0xFF062F49);
  static const errorBackground = Color(0xFFE4F7F5);
  static const info = Color(0xFF062F49);
  static const infoBackground = Color(0xFFE6F9F7);
}

class AppTheme {
  static ThemeData get light {
    final scheme = ColorScheme.fromSeed(seedColor: AppColors.primary, brightness: Brightness.light)
        .copyWith(primary: AppColors.primary, onPrimary: Colors.white, secondary: AppColors.secondary, onSecondary: AppColors.primaryDark, surface: AppColors.surface, onSurface: AppColors.textPrimary, onSurfaceVariant: AppColors.textSecondary, error: AppColors.error);
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: AppColors.background,
      textTheme: Typography.material2021().black.apply(bodyColor: AppColors.textPrimary, displayColor: AppColors.textPrimary),
      appBarTheme: const AppBarTheme(backgroundColor: AppColors.background, foregroundColor: AppColors.textPrimary, elevation: 0, centerTitle: false, titleTextStyle: TextStyle(color: AppColors.textPrimary, fontSize: 20, fontWeight: FontWeight.w700)),
      cardTheme: CardThemeData(color: AppColors.surface, elevation: 0, margin: EdgeInsets.zero, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: const BorderSide(color: AppColors.border))),
      inputDecorationTheme: InputDecorationTheme(filled: true, fillColor: AppColors.surface, hintStyle: const TextStyle(color: AppColors.textSecondary), contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15), border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.border)), enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.border)), focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: AppColors.primary, width: 1.5))),
      elevatedButtonTheme: ElevatedButtonThemeData(style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white, minimumSize: const Size.fromHeight(52), textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)))),
      outlinedButtonTheme: OutlinedButtonThemeData(style: OutlinedButton.styleFrom(foregroundColor: AppColors.primary, minimumSize: const Size.fromHeight(48), side: const BorderSide(color: AppColors.border), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)))),
      navigationBarTheme: NavigationBarThemeData(backgroundColor: AppColors.surface, indicatorColor: AppColors.primaryLight, height: 70, labelTextStyle: WidgetStateProperty.resolveWith((s) => TextStyle(fontSize: 11, fontWeight: s.contains(WidgetState.selected) ? FontWeight.w700 : FontWeight.w500, color: s.contains(WidgetState.selected) ? AppColors.primary : AppColors.textSecondary))),
      chipTheme: ChipThemeData(backgroundColor: AppColors.surface, selectedColor: AppColors.primaryLight, side: const BorderSide(color: AppColors.border), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)), labelStyle: const TextStyle(fontSize: 12)),
      progressIndicatorTheme: const ProgressIndicatorThemeData(color: AppColors.primary, linearTrackColor: AppColors.secondaryLight),
      snackBarTheme: SnackBarThemeData(behavior: SnackBarBehavior.floating, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
    );
  }
}
