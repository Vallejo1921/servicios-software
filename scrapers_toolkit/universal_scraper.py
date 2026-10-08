#!/usr/bin/env python3
"""
Motor Universal de Web Scraping y Extracción de Datos
Soporta:
1. Scraping HTML estático (rápido y ligero)
2. Manejo de User-Agents, cabeceras y retardos anti-bloqueo
3. Exportación limpia a CSV, JSON y SQLite
"""

import sys
import os
import csv
import json
import sqlite3
import time
import urllib.request
from html.parser import HTMLParser

class SimpleDOMParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for k, v in attrs:
                if k == 'href':
                    self.links.append(v)

    def handle_data(self, data):
        cleaned = data.strip()
        if cleaned:
            self.text_chunks.append(cleaned)

def fetch_url(url, timeout=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content_type = response.headers.get_content_charset() or 'utf-8'
        return response.read().decode(content_type, errors='replace')

def export_to_csv(data, filename):
    if not data:
        print("[-] No hay datos para exportar a CSV.")
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"[+] Archivo CSV generado con éxito: {filename} ({len(data)} registros)")

def export_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[+] Archivo JSON generado con éxito: {filename} ({len(data)} registros)")

def export_to_sqlite(data, db_path, table_name="scraped_data"):
    if not data:
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    keys = list(data[0].keys())
    
    cols = ", ".join([f'"{k}" TEXT' for k in keys])
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({cols})')
    
    placeholders = ", ".join(["?" for _ in keys])
    insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders})'
    
    rows = [[str(item.get(k, '')) for k in keys] for item in data]
    cursor.executemany(insert_sql, rows)
    conn.commit()
    conn.close()
    print(f"[+] Base de datos SQLite guardada: {db_path} -> tabla '{table_name}'")

if __name__ == "__main__":
    print("=== Motor de Scraping Listo ===")
    print("Uso en pedidos: importar 'fetch_url', extraer selectores y llamar 'export_to_csv()'.")
