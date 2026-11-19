import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Bottom navigation melayang dengan indikator berbentuk pil.
class AppBottomNav extends StatelessWidget {
  const AppBottomNav({
    super.key,
    required this.selectedIndex,
    required this.onSelected,
  });

  final int selectedIndex;
  final ValueChanged<int> onSelected;

  static const _items = [
    (Icons.home_outlined, Icons.home_rounded, 'Home'),
    (Icons.folder_outlined, Icons.folder_rounded, 'Documents'),
    (Icons.person_outline_rounded, Icons.person_rounded, 'Profile'),
  ];

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return SafeArea(
      top: false,
      child: Align(
        heightFactor: 1,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 4, 16, 12),
            child: Container(
              height: 64,
              padding: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                color: c.navSurface,
                borderRadius: BorderRadius.circular(24),
                border: c.isDark ? Border.all(color: c.border) : null,
                boxShadow: c.isDark
                    ? null
                    : [
                        BoxShadow(
                          color: c.primaryDark.withValues(alpha: .28),
                          blurRadius: 24,
                          offset: const Offset(0, 10),
                        ),
                      ],
              ),
              child: Row(
                children: [
                  for (var i = 0; i < _items.length; i++)
                    Expanded(
                      child: _NavItem(
                        icon: _items[i].$1,
                        selectedIcon: _items[i].$2,
                        label: _items[i].$3,
                        selected: i == selectedIndex,
                        onTap: () => onSelected(i),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Navigasi samping untuk tablet & desktop.
/// [extended] = true menampilkan ikon + teks (desktop),
/// false hanya ikon dengan label kecil (tablet).
class AppSideNav extends StatelessWidget {
  const AppSideNav({
    super.key,
    required this.selectedIndex,
    required this.onSelected,
    this.extended = false,
  });

  final int selectedIndex;
  final ValueChanged<int> onSelected;
  final bool extended;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Container(
      width: extended ? 232 : 92,
      decoration: BoxDecoration(
        color: c.navSurface,
        border: c.isDark ? Border(right: BorderSide(color: c.divider)) : null,
      ),
      child: SafeArea(
        right: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 22),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: extended ? 20 : 0),
              child: Row(
                mainAxisAlignment: extended
                    ? MainAxisAlignment.start
                    : MainAxisAlignment.center,
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: c.navSelected,
                      borderRadius: BorderRadius.circular(13),
                    ),
                    child: Icon(
                      Icons.auto_stories_rounded,
                      color: c.navOnSelected,
                      size: 22,
                    ),
                  ),
                  if (extended) ...[
                    const SizedBox(width: 10),
                    Flexible(
                      child: Text(
                        'ThesisFormat',
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: c.navOnSurface,
                          fontWeight: FontWeight.w800,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 30),
            for (var i = 0; i < AppBottomNav._items.length; i++)
              Padding(
                padding: EdgeInsets.fromLTRB(
                  extended ? 14 : 10,
                  0,
                  extended ? 14 : 10,
                  8,
                ),
                child: _SideNavItem(
                  icon: AppBottomNav._items[i].$1,
                  selectedIcon: AppBottomNav._items[i].$2,
                  label: AppBottomNav._items[i].$3,
                  selected: i == selectedIndex,
                  extended: extended,
                  onTap: () => onSelected(i),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _SideNavItem extends StatelessWidget {
  const _SideNavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.selected,
    required this.extended,
    required this.onTap,
  });

  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final bool selected;
  final bool extended;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final iconWidget = Icon(
      selected ? selectedIcon : icon,
      size: 22,
      color: selected ? c.navOnSelected : c.navUnselected,
    );
    final text = Text(
      label,
      maxLines: 1,
      overflow: TextOverflow.ellipsis,
      style: TextStyle(
        fontSize: extended ? 14 : 11,
        fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
        color: selected ? c.navOnSelected : c.navUnselected,
      ),
    );

    return Semantics(
      selected: selected,
      button: true,
      child: Material(
        color: selected ? c.navSelected : Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: extended ? 14 : 4,
              vertical: extended ? 13 : 10,
            ),
            child: extended
                ? Row(
                    children: [
                      iconWidget,
                      const SizedBox(width: 12),
                      Expanded(child: text),
                    ],
                  )
                : Column(
                    children: [iconWidget, const SizedBox(height: 4), text],
                  ),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Semantics(
      selected: selected,
      button: true,
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: Center(
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 220),
            curve: Curves.easeOut,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
            decoration: BoxDecoration(
              color: selected ? c.navSelected : Colors.transparent,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  selected ? selectedIcon : icon,
                  size: 22,
                  color: selected ? c.navOnSelected : c.navUnselected,
                ),
                const SizedBox(width: 6),
                Flexible(
                  child: Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                      color: selected ? c.navOnSelected : c.navUnselected,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
