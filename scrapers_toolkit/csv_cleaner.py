#!/usr/bin/env python3
"""
Limpiador y Normalizador Automático de Excel / CSV
Convierte archivos desordenados en datos limpios:
- Elimina duplicados
- Estandariza números de teléfono (formato internacional)
- Limpia espacios en blanco y mayúsculas/minúsculas
- Exporta reporte de limpieza
"""

import sys
import os
import csv
import re

def clean_phone_number(phone_str):
    if not phone_str:
        return ""
    digits = re.sub(r'\D', '', str(phone_str))
    if len(digits) == 10:
        return f"+52 {digits[:2]} {digits[2:6]} {digits[6:]}"
    elif len(digits) == 12 and digits.startswith('52'):
        return f"+{digits[:2]} {digits[2:4]} {digits[4:8]} {digits[8:]}"
    return digits

def clean_csv_file(input_path, output_path, deduplicate_by=None):
    if not os.path.exists(input_path):
        print(f"[-] Archivo no encontrado: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    initial_count = len(rows)
    cleaned_rows = []
    seen_keys = set()

    for row in rows:
        cleaned_row = {}
        for k, v in row.items():
            if v is not None:
                cleaned_val = re.sub(r'\s+', ' ', str(v).strip())
                if 'tel' in k.lower() or 'phone' in k.lower() or 'cel' in k.lower():
                    cleaned_val = clean_phone_number(cleaned_val)
                cleaned_row[k] = cleaned_val
            else:
                cleaned_row[k] = ""

        # Deduplicación opcional
        if deduplicate_by and deduplicate_by in cleaned_row:
            dedup_val = cleaned_row[deduplicate_by].lower()
            if dedup_val in seen_keys:
                continue
            seen_keys.add(dedup_val)

        cleaned_rows.append(cleaned_row)

    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    final_count = len(cleaned_rows)
    removed_count = initial_count - final_count
    print(f"[+] Limpieza completada con éxito:")
    print(f"    - Registros originales: {initial_count}")
    print(f"    - Duplicados eliminados: {removed_count}")
    print(f"    - Registros finales limpios: {final_count}")
    print(f"    - Archivo generado: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 csv_cleaner.py <archivo_origen.csv> <archivo_destino.csv> [columna_deduplicar]")
        sys.exit(1)
    col = sys.argv[3] if len(sys.argv) > 3 else None
    clean_csv_file(sys.argv[1], sys.argv[2], col)
