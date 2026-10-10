from typing import Any, Dict, List, Optional


def _get_rule_value(rule_value):
    if isinstance(rule_value, dict):
        return rule_value.get("value", rule_value)
    return rule_value


def _cm_close(found, expected, tolerance=0.05):
    try:
        return abs(float(found) - float(expected)) <= tolerance
    except (TypeError, ValueError):
        return False


def _get_target_paragraphs(parsed_document, styles=None):
    paragraphs = parsed_document.get("paragraphs", [])
    if not styles:
        return paragraphs
    return [p for p in paragraphs if p.get("style") in styles]


def check_physical_rules(parsed_document, rules):
    """
    Memeriksa hasil parsing dokumen terhadap
    aturan physical dari MasterRule.
    """

    findings = []

    for rule in rules:
        rule_key = rule.rule_key
        rule_value = rule.rule_value

        # ==========================================
        # RULE: FONT NAME
        # ==========================================
        if rule_key == "font_name":
            expected_font = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(parsed_document, styles)

            found_fonts = set()

            for paragraph in target_paragraphs:
                for run in paragraph.get("runs", []):
                    font_name = run.get("font_name")

                    if font_name:
                        found_fonts.add(font_name)

            if not found_fonts:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": "Tidak ditemukan informasi font pada dokumen.",
                    "expected": expected_font,
                    "found": [],
                })
                continue

            invalid_fonts = [
                font for font in found_fonts
                if font != expected_font
            ]

            if invalid_fonts:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        f"Font tidak sesuai. "
                        f"Ditemukan: {', '.join(invalid_fonts)}. "
                        f"Seharusnya: {expected_font}."
                    ),
                    "expected": expected_font,
                    "found": list(found_fonts),
                })
            else:
                findings.append({
                    "rule_key": rule_key,
                    "status": "passed",
                    "message": (
                        f"Semua font sesuai dengan aturan "
                        f"{expected_font}."
                    ),
                    "expected": expected_font,
                    "found": list(found_fonts),
                })

        # ==========================================
        # RULE: FONT SIZE
        # ==========================================
        elif rule_key == "font_size":
            expected_size = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(parsed_document, styles)

            found_sizes = set()

            for paragraph in target_paragraphs:
                for run in paragraph.get("runs", []):
                    font_size = run.get("font_size")

                    if font_size is not None:
                        found_sizes.add(font_size)

            if not found_sizes:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        "Tidak ditemukan informasi ukuran font "
                        "pada dokumen."
                    ),
                    "expected": expected_size,
                    "found": [],
                })
                continue

            invalid_sizes = [
                size for size in found_sizes
                if size != expected_size
            ]

            if invalid_sizes:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        f"Ukuran font tidak sesuai. "
                        f"Ditemukan: "
                        f"{', '.join(map(str, invalid_sizes))} pt. "
                        f"Seharusnya: {expected_size} pt."
                    ),
                    "expected": expected_size,
                    "found": list(found_sizes),
                })
            else:
                findings.append({
                    "rule_key": rule_key,
                    "status": "passed",
                    "message": (
                        f"Semua ukuran font sesuai dengan "
                        f"aturan {expected_size} pt."
                    ),
                    "expected": expected_size,
                    "found": list(found_sizes),
                })

        # ==========================================
        # RULE: ALIGNMENT
        # ==========================================
        elif rule_key == "alignment":
            expected_alignment = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(parsed_document, styles)

            found_alignments = set()

            for paragraph in target_paragraphs:
                alignment = paragraph.get("alignment")

                if alignment:
                    found_alignments.add(alignment)

            if not found_alignments:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        "Tidak ditemukan informasi alignment "
                        "pada dokumen."
                    ),
                    "expected": expected_alignment,
                    "found": [],
                })
                continue

            invalid_alignments = [
                alignment
                for alignment in found_alignments
                if alignment != expected_alignment
            ]

            if invalid_alignments:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        f"Alignment tidak sesuai. "
                        f"Ditemukan: "
                        f"{', '.join(invalid_alignments)}. "
                        f"Seharusnya: {expected_alignment}."
                    ),
                    "expected": expected_alignment,
                    "found": list(found_alignments),
                })
            else:
                findings.append({
                    "rule_key": rule_key,
                    "status": "passed",
                    "message": (
                        f"Semua paragraf menggunakan alignment "
                        f"{expected_alignment}."
                    ),
                    "expected": expected_alignment,
                    "found": list(found_alignments),
                })

        # ==========================================
        # RULE: LINE SPACING
        # ==========================================
        elif rule_key == "line_spacing":
            expected_spacing = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(parsed_document, styles)

            found_spacings = set()

            for paragraph in target_paragraphs:
                line_spacing = paragraph.get("line_spacing")

                if line_spacing is not None:
                    found_spacings.add(line_spacing)

            if not found_spacings:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        "Tidak ditemukan informasi line spacing "
                        "pada dokumen."
                    ),
                    "expected": expected_spacing,
                    "found": [],
                })
                continue

            invalid_spacings = [
                spacing
                for spacing in found_spacings
                if spacing != expected_spacing
            ]

            if invalid_spacings:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        f"Line spacing tidak sesuai. "
                        f"Ditemukan: "
                        f"{', '.join(map(str, invalid_spacings))}. "
                        f"Seharusnya: {expected_spacing}."
                    ),
                    "expected": expected_spacing,
                    "found": list(found_spacings),
                })
            else:
                findings.append({
                    "rule_key": rule_key,
                    "status": "passed",
                    "message": (
                        f"Semua paragraf menggunakan line spacing "
                        f"{expected_spacing}."
                    ),
                    "expected": expected_spacing,
                    "found": list(found_spacings),
                })

        # ==========================================
        # RULE: MARGIN
        # ==========================================
        elif rule_key == "margin":
            expected_margin = _get_rule_value(rule_value)

            if not isinstance(expected_margin, dict):
                findings.append({
                    "rule_key": rule_key,
                    "status": "pending",
                    "message": (
                        "Rule margin belum memakai format value "
                        "yang benar."
                    ),
                    "expected": rule_value,
                    "found": None,
                })
                continue

            found_sections = parsed_document.get("sections", [])

            if not found_sections:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        "Tidak ditemukan informasi margin "
                        "pada dokumen."
                    ),
                    "expected": expected_margin,
                    "found": [],
                })
                continue

            invalid_sections = []

            for index, section in enumerate(found_sections, start=1):
                section_errors = []

                expected_top = expected_margin.get("top_margin")
                expected_bottom = expected_margin.get("bottom_margin")
                expected_left = expected_margin.get("left_margin")
                expected_right = expected_margin.get("right_margin")

                found_top = section.get("top_margin")
                found_bottom = section.get("bottom_margin")
                found_left = section.get("left_margin")
                found_right = section.get("right_margin")

                if expected_top is not None and not _cm_close(found_top, expected_top):
                    section_errors.append(
                        f"top_margin: ditemukan {found_top}, seharusnya {expected_top}"
                    )

                if expected_bottom is not None and not _cm_close(found_bottom, expected_bottom):
                    section_errors.append(
                        f"bottom_margin: ditemukan {found_bottom}, seharusnya {expected_bottom}"
                    )

                if expected_left is not None and not _cm_close(found_left, expected_left):
                    section_errors.append(
                        f"left_margin: ditemukan {found_left}, seharusnya {expected_left}"
                    )

                if expected_right is not None and not _cm_close(found_right, expected_right):
                    section_errors.append(
                        f"right_margin: ditemukan {found_right}, seharusnya {expected_right}"
                    )

                if section_errors:
                    invalid_sections.append({
                        "section": index,
                        "errors": section_errors,
                        "found": section,
                    })

            if invalid_sections:
                findings.append({
                    "rule_key": rule_key,
                    "status": "failed",
                    "message": (
                        "Margin tidak sesuai pada beberapa section."
                    ),
                    "expected": expected_margin,
                    "found": invalid_sections,
                })
            else:
                findings.append({
                    "rule_key": rule_key,
                    "status": "passed",
                    "message": (
                        "Semua section memiliki margin sesuai aturan."
                    ),
                    "expected": expected_margin,
                    "found": found_sections,
                })

        # ==========================================
        # RULE LAINNYA
        # ==========================================
        else:
            findings.append({
                "rule_key": rule_key,
                "status": "pending",
                "message": (
                    f"Rule '{rule_key}' belum memiliki "
                    "logic pemeriksaan."
                ),
                "expected": rule_value,
                "found": None,
            })

    return findings