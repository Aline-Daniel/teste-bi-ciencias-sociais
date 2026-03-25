"""
ETL Script - Análise de Produção Científica em Ciências Sociais
Carrega, limpa, transforma e unifica as bases artigos_fi1.csv e artigos_fi2.csv em SQLite.
"""

import sqlite3
import csv
import os
import re

DB_PATH = "producao_cientifica.db"
FI1_PATH = "artigos_fi1.csv"
FI2_PATH = "artigos_fi2.csv"


def parse_decimal(val):
    """Converte strings com vírgula decimal para float."""
    if not val or val.strip() in ("-", ""):
        return 0.0
    return float(val.strip().replace(",", "."))


def parse_int(val):
    try:
        return int(val.strip())
    except (ValueError, AttributeError):
        return 0


def create_tables(cur):
    cur.executescript("""
    DROP TABLE IF EXISTS artigos_fi1;
    DROP TABLE IF EXISTS artigos_fi2;
    DROP VIEW IF EXISTS vw_unified;

    CREATE TABLE artigos_fi1 (
        issn          TEXT PRIMARY KEY,
        periodico     TEXT,
        qualis        TEXT,
        sjr           REAL,
        h_index       INTEGER,
        citacoes_3anos INTEGER,
        citacoes_media INTEGER
    );

    CREATE TABLE artigos_fi2 (
        rank_pos       INTEGER,
        sourceid       INTEGER,
        title          TEXT,
        type           TEXT,
        issn           TEXT,
        sjr            REAL,
        quartile       TEXT,
        h_index        INTEGER,
        total_docs_2022    INTEGER,
        total_docs_3years  INTEGER,
        total_refs         INTEGER,
        total_cites_3years INTEGER,
        citable_docs_3years INTEGER,
        cites_per_doc_2years REAL,
        ref_per_doc      REAL,
        country        TEXT,
        region         TEXT,
        publisher      TEXT,
        coverage       TEXT,
        categories     TEXT,
        areas          TEXT
    );
    """)


def load_fi1(cur, path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append((
                r.get("ISSN", "").strip(),
                r.get("PERIÓDICO", "").strip(),
                r.get("QUALIS", "").strip(),
                parse_decimal(r.get("FI (SJR)", "")),
                parse_int(r.get("H-index", "0")),
                parse_int(r.get("Citações (2019-2021)", "0")),
                parse_int(r.get("Citações (média)", "0")),
            ))
        cur.executemany(
            "INSERT OR IGNORE INTO artigos_fi1 VALUES (?,?,?,?,?,?,?)", rows
        )
    print(f"  artigos_fi1: {len(rows)} registros carregados")


def load_fi2(cur, path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append((
                parse_int(r.get("Rank", "0")),
                parse_int(r.get("Sourceid", "0")),
                r.get("Title", "").strip(),
                r.get("Type", "").strip(),
                r.get("Issn", "").strip(),
                parse_decimal(r.get("SJR", "")),
                r.get("SJR Best Quartile", "-").strip(),
                parse_int(r.get("H index", "0")),
                parse_int(r.get("Total Docs. (2022)", "0")),
                parse_int(r.get("Total Docs. (3years)", "0")),
                parse_int(r.get("Total Refs.", "0")),
                parse_int(r.get("Total Cites (3years)", "0")),
                parse_int(r.get("Citable Docs. (3years)", "0")),
                parse_decimal(r.get("Cites / Doc. (2years)", "")),
                parse_decimal(r.get("Ref. / Doc.", "")),
                r.get("Country", "").strip(),
                r.get("Region", "").strip(),
                r.get("Publisher", "").strip(),
                r.get("Coverage", "").strip(),
                r.get("Categories", "").strip(),
                r.get("Areas", "").strip(),
            ))
        cur.executemany(
            "INSERT INTO artigos_fi2 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            rows,
        )
    print(f"  artigos_fi2: {len(rows)} registros carregados")


def create_unified_view(cur):
    cur.execute("""
    CREATE VIEW vw_unified AS
    SELECT
        COALESCE(f1.periodico, f2.title)   AS titulo,
        f1.issn,
        f1.qualis,
        COALESCE(NULLIF(f1.sjr, 0), f2.sjr) AS sjr,
        COALESCE(NULLIF(f1.h_index, 0), f2.h_index) AS h_index,
        COALESCE(f2.quartile, '-')          AS quartile,
        COALESCE(f2.country, '')            AS country,
        COALESCE(f2.region, '')             AS region,
        f1.citacoes_media,
        f1.citacoes_3anos,
        COALESCE(f2.total_docs_2022, 0)     AS total_docs,
        CASE WHEN LOWER(f2.country) = 'brazil' THEN 1 ELSE 0 END AS is_brazilian,
        COALESCE(f2.categories, '')         AS categories
    FROM artigos_fi1 f1
    LEFT JOIN artigos_fi2 f2
        ON REPLACE(REPLACE(f1.issn, '-', ''), ' ', '')
           IN (
               REPLACE(REPLACE(TRIM(SUBSTR(f2.issn, 1, INSTR(f2.issn || ',', ',') - 1)), '-', ''), ' ', ''),
               REPLACE(REPLACE(TRIM(SUBSTR(f2.issn, INSTR(f2.issn || ',', ',') + 1)), '-', ''), ' ', '')
           );
    """)
    print("  vw_unified: view criada com sucesso")


def run_sample_queries(cur):
    print("\n===== ANÁLISES =====\n")

    print("1. Distribuição QUALIS:")
    for row in cur.execute(
        "SELECT qualis, COUNT(*) AS n FROM artigos_fi1 GROUP BY qualis ORDER BY n DESC"
    ):
        print(f"   {row[0]:>4s}: {row[1]}")

    print("\n2. Top 5 periódicos por SJR:")
    for row in cur.execute(
        "SELECT titulo, sjr, qualis, quartile, country FROM vw_unified WHERE sjr > 0 ORDER BY sjr DESC LIMIT 5"
    ):
        print(f"   SJR={row[1]:.2f} | {row[2]} | {row[3]} | {row[4]} | {row[0][:60]}")

    print("\n3. Benchmark Brasil vs Internacional (periódicos com match):")
    cur.execute("""
        SELECT
            CASE WHEN is_brazilian = 1 THEN 'Brasil' ELSE 'Internacional' END AS grupo,
            COUNT(*) AS n,
            ROUND(AVG(sjr), 3) AS avg_sjr,
            ROUND(AVG(h_index), 1) AS avg_h,
            ROUND(100.0 * SUM(CASE WHEN quartile = 'Q1' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_q1
        FROM vw_unified
        WHERE country != ''
        GROUP BY is_brazilian
    """)
    for row in cur.fetchall():
        print(f"   {row[0]:15s}: n={row[1]}, SJR={row[2]}, H={row[3]}, %Q1={row[4]}%")

    print("\n4. Citações médias por QUALIS:")
    cur.execute("""
        SELECT qualis, ROUND(AVG(citacoes_media), 1) AS avg_cit, COUNT(*) AS n
        FROM vw_unified
        WHERE citacoes_media > 0
        GROUP BY qualis
        ORDER BY avg_cit DESC
    """)
    for row in cur.fetchall():
        print(f"   {row[0]:>4s}: média={row[1]}, n={row[2]}")


def main():
    print("=" * 60)
    print("ETL - Produção Científica em Ciências Sociais")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\n[1/4] Criando tabelas...")
    create_tables(cur)

    print("[2/4] Carregando dados...")
    load_fi1(cur, FI1_PATH)
    load_fi2(cur, FI2_PATH)

    print("[3/4] Criando view unificada...")
    create_unified_view(cur)

    conn.commit()

    print("[4/4] Executando análises de validação...")
    run_sample_queries(cur)

    conn.close()
    print(f"\nBanco SQLite salvo em: {DB_PATH}")
    print("ETL concluído com sucesso!")


if __name__ == "__main__":
    main()
