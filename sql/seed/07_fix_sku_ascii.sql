BEGIN;

-- Fix SKU values generated with Turkish characters in earlier demo seed runs.
-- Keeps SKU values limited to ASCII uppercase letters, digits and hyphen.

WITH sku_candidates AS (
    SELECT
        uv.varyant_id,
        uv.sku AS old_sku,
        regexp_replace(
            upper(
                translate(
                    uv.sku,
                    'çğıiöşüÇĞİÖŞÜéÉ',
                    'cgiiosuCGIOSUEE'
                )
            ),
            '[^A-Z0-9-]',
            '',
            'g'
        ) AS new_sku
    FROM public.urun_varyantlari uv
    WHERE uv.sku ~ '[^A-Z0-9-]'
),
deduplicated_candidates AS (
    SELECT *
    FROM (
        SELECT
            sc.*,
            count(*) OVER (PARTITION BY sc.new_sku) AS new_sku_count
        FROM sku_candidates sc
        WHERE sc.new_sku <> sc.old_sku
    ) candidate
    WHERE candidate.new_sku_count = 1
)
UPDATE public.urun_varyantlari uv
SET sku = dc.new_sku
FROM deduplicated_candidates dc
WHERE uv.varyant_id = dc.varyant_id
  AND NOT EXISTS (
      SELECT 1
      FROM public.urun_varyantlari existing
      WHERE existing.sku = dc.new_sku
        AND existing.varyant_id <> dc.varyant_id
  );

COMMIT;
