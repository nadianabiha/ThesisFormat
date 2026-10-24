
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

    if isinstance(styles, str):
        styles = [styles]

    return [
        paragraph
        for paragraph in paragraphs
        if paragraph.get("style") in styles
    ]


def check_physical_rules(parsed_document, rules):
    """
    Memeriksa format fisik dokumen berdasarkan MasterRule.

    Mendukung rules berbentuk dictionary:
    {
        "font_name": {"value": "Times New Roman"},
        "font_size": {"value": 12}
    }
    """

    findings = []

    # Backend mengirim rules sebagai dictionary dengan rule_key
    # sebagai key dan rule_value sebagai value.
    if isinstance(rules, dict):
        rule_items = rules.items()
    else:
        # Mendukung juga daftar objek MasterRule.
        rule_items = (
            (rule.rule_key, rule.rule_value)
            for rule in rules
        )

    for rule_key, rule_value in rule_items:
        if not isinstance(rule_value, dict):
            rule_value = {"value": rule_value}

        # ==========================================
        # RULE: FONT NAME
        # ==========================================
        if rule_key == "font_name":
            expected_font = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(
                parsed_document, styles
            )

            found_fonts = {
                run.get("font_name")
                for paragraph in target_paragraphs
                for run in paragraph.get("runs", [])
                if run.get("font_name")
            }

            if not found_fonts:
                status = "pending"
                message = (
                    "Informasi font tidak ditemukan secara eksplisit "
                    "pada hasil parsing dokumen."
                )
            else:
                invalid_fonts = [
                    font for font in found_fonts
                    if font != expected_font
                ]

                if invalid_fonts:
                    status = "failed"
                    message = (
                        f"Font tidak sesuai. Ditemukan: "
                        f"{', '.join(sorted(invalid_fonts))}. "
                        f"Seharusnya: {expected_font}."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua font yang terbaca sesuai dengan "
                        f"aturan {expected_font}."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_font,
                "found": sorted(found_fonts),
            })

        # ==========================================
        # RULE: FONT SIZE
        # ==========================================
        elif rule_key == "font_size":
            expected_size = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(
                parsed_document, styles
            )

            found_sizes = {
                run.get("font_size")
                for paragraph in target_paragraphs
                for run in paragraph.get("runs", [])
                if run.get("font_size") is not None
            }

            if not found_sizes:
                status = "pending"
                message = (
                    "Informasi ukuran font tidak ditemukan secara "
                    "eksplisit pada hasil parsing dokumen."
                )
            else:
                invalid_sizes = [
                    size for size in found_sizes
                    if not _cm_close(size, expected_size, tolerance=0.01)
                ]

                if invalid_sizes:
                    status = "failed"
                    message = (
                        f"Ukuran font tidak sesuai. Ditemukan: "
                        f"{', '.join(map(str, sorted(invalid_sizes)))} pt. "
                        f"Seharusnya: {expected_size} pt."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua ukuran font yang terbaca sesuai "
                        f"dengan aturan {expected_size} pt."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_size,
                "found": sorted(found_sizes),
            })

        # ==========================================
        # RULE: ALIGNMENT
        # ==========================================
        elif rule_key == "alignment":
            expected_alignment = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(
                parsed_document, styles
            )

            found_alignments = {
                paragraph.get("alignment")
                for paragraph in target_paragraphs
                if paragraph.get("alignment")
            }

            if not found_alignments:
                status = "pending"
                message = (
                    "Informasi alignment tidak ditemukan secara "
                    "eksplisit pada hasil parsing dokumen."
                )
            else:
                invalid_alignments = [
                    alignment for alignment in found_alignments
                    if alignment != expected_alignment
                ]

                if invalid_alignments:
                    status = "failed"
                    message = (
                        f"Alignment tidak sesuai. Ditemukan: "
                        f"{', '.join(sorted(invalid_alignments))}. "
                        f"Seharusnya: {expected_alignment}."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua alignment yang terbaca sesuai "
                        f"dengan aturan {expected_alignment}."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_alignment,
                "found": sorted(found_alignments),
            })

        # ==========================================
        # RULE: LINE SPACING
        # ==========================================
        elif rule_key == "line_spacing":
            expected_spacing = rule_value.get("value")
            styles = rule_value.get("styles")
            target_paragraphs = _get_target_paragraphs(
                parsed_document, styles
            )

            found_spacings = {
                paragraph.get("line_spacing")
                for paragraph in target_paragraphs
                if paragraph.get("line_spacing") is not None
                and isinstance(
                    paragraph.get("line_spacing"), (int, float)
                )
            }

            if not found_spacings:
                status = "pending"
                message = (
                    "Informasi line spacing numerik tidak ditemukan "
                    "pada hasil parsing dokumen."
                )
            else:
                invalid_spacings = [
                    spacing for spacing in found_spacings
                    if not _cm_close(
                        spacing, expected_spacing, tolerance=0.01
                    )
                ]

                if invalid_spacings:
                    status = "failed"
                    message = (
                        f"Line spacing tidak sesuai. Ditemukan: "
                        f"{', '.join(map(str, sorted(invalid_spacings)))}. "
                        f"Seharusnya: {expected_spacing}."
                    )
                else:
                    status = "passed"
                    message = (
                        f"Semua line spacing yang terbaca sesuai "
                        f"dengan aturan {expected_spacing}."
                    )

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_spacing,
                "found": sorted(found_spacings),
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
                    "message": "Konfigurasi rule margin belum valid.",
                    "expected": rule_value,
                    "found": None,
                })
                continue

            found_sections = parsed_document.get("sections", [])

            if not found_sections:
                findings.append({
                    "rule_key": rule_key,
                    "status": "pending",
                    "message": "Informasi margin tidak ditemukan.",
                    "expected": expected_margin,
                    "found": [],
                })
                continue

            invalid_sections = []

            for index, section in enumerate(found_sections, start=1):
                section_errors = []

                for margin_key in (
                    "top_margin",
                    "bottom_margin",
                    "left_margin",
                    "right_margin",
                ):
                    expected = expected_margin.get(margin_key)
                    found = section.get(margin_key)

                    if (
                        expected is not None
                        and not _cm_close(found, expected)
                    ):
                        section_errors.append(
                            f"{margin_key}: ditemukan {found}, "
                            f"seharusnya {expected} cm"
                        )

                if section_errors:
                    invalid_sections.append({
                        "section": index,
                        "errors": section_errors,
                        "found": section,
                    })

            if invalid_sections:
                status = "failed"
                message = "Margin tidak sesuai pada beberapa section."
            else:
                status = "passed"
                message = "Semua section sesuai dengan aturan margin."

            findings.append({
                "rule_key": rule_key,
                "status": status,
                "message": message,
                "expected": expected_margin,
                "found": (
                    invalid_sections if invalid_sections else found_sections
                ),
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
                    "logika pemeriksaan."
                ),
                "expected": rule_value,
                "found": None,
            })

    return findings
