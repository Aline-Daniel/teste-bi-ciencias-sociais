-- ============================================================
-- SQL Queries - Análise de Produção Científica
-- Compatível com SQLite / PostgreSQL
-- ============================================================

-- 1. Distribuição QUALIS
SELECT qualis, COUNT(*) AS total
FROM artigos_fi1
GROUP BY qualis
ORDER BY total DESC;

-- 2. Top 10 periódicos por SJR (view unificada)
SELECT titulo, sjr, qualis, quartile, h_index, country
FROM vw_unified
WHERE sjr > 0
ORDER BY sjr DESC
LIMIT 10;

-- 3. Correlação Citações x QUALIS
SELECT
    qualis,
    COUNT(*) AS n,
    ROUND(AVG(citacoes_media), 1) AS media_citacoes,
    ROUND(AVG(sjr), 3) AS media_sjr
FROM vw_unified
WHERE citacoes_media > 0
GROUP BY qualis
ORDER BY media_citacoes DESC;

-- 4. Benchmark Brasil vs Internacional
SELECT
    CASE WHEN is_brazilian = 1 THEN 'Brasil' ELSE 'Internacional' END AS grupo,
    COUNT(*) AS total_periodicos,
    ROUND(AVG(sjr), 3) AS sjr_medio,
    ROUND(AVG(h_index), 1) AS h_index_medio,
    ROUND(100.0 * SUM(CASE WHEN quartile = 'Q1' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_q1,
    ROUND(100.0 * SUM(CASE WHEN quartile = 'Q2' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_q2
FROM vw_unified
WHERE country != ''
GROUP BY is_brazilian;

-- 5. Distribuição por Quartile
SELECT quartile, COUNT(*) AS total
FROM vw_unified
WHERE quartile != '-'
GROUP BY quartile
ORDER BY quartile;

-- 6. Top 15 países por número de periódicos
SELECT country, COUNT(*) AS total
FROM vw_unified
WHERE country != ''
GROUP BY country
ORDER BY total DESC
LIMIT 15;

-- 7. Periódicos brasileiros com melhor classificação
SELECT titulo, sjr, qualis, quartile, h_index, citacoes_media
FROM vw_unified
WHERE is_brazilian = 1 AND sjr > 0
ORDER BY sjr DESC
LIMIT 20;

-- 8. Análise de concentração: QUALIS A1 por país
SELECT country, COUNT(*) AS total_a1
FROM vw_unified
WHERE qualis = 'A1' AND country != ''
GROUP BY country
ORDER BY total_a1 DESC
LIMIT 10;
