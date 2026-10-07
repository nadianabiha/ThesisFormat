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

            found_fonts = set()

            for paragraph in parsed_document.get("paragraphs", []):
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

            found_sizes = set()

            for paragraph in parsed_document.get("paragraphs", []):
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

            found_alignments = set()

            for paragraph in parsed_document.get("paragraphs", []):
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

            found_spacings = set()

            for paragraph in parsed_document.get("paragraphs", []):
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