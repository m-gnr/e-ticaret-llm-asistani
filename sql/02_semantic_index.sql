BEGIN;

-- =========================================================
-- 02_semantic_index.sql
-- E-Ticaret LLM Asistanı - Ortak Semantic Index Tablosu
-- =========================================================
-- Bu tablo, veritabanındaki farklı tablolardan üretilen metinleri
-- embedding vektörleriyle birlikte saklar.
--
-- Örnek kaynak tablolar:
-- urunler, urun_varyantlari, kategoriler, markalar,
-- urun_yorumlari, siparisler, kargolar, iadeler, kuponlar
-- =========================================================


-- =========================================================
-- 1. EXTENSIONS
-- =========================================================

CREATE EXTENSION IF NOT EXISTS vector;


-- =========================================================
-- 2. SEMANTIC INDEX TABLOSU
-- =========================================================

CREATE TABLE IF NOT EXISTS public.semantic_index
(
    semantic_id uuid NOT NULL DEFAULT gen_random_uuid(),

    kaynak_tablo text NOT NULL,
    kaynak_id uuid NOT NULL,

    baslik text,
    icerik text NOT NULL,

    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    embedding vector(384),

    model_adi text NOT NULL DEFAULT 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',

    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),
    guncelleme_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT semantic_index_pkey PRIMARY KEY (semantic_id),
    CONSTRAINT semantic_index_kaynak_unique UNIQUE (kaynak_tablo, kaynak_id)
);


-- =========================================================
-- 3. INDEXLER
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_semantic_index_kaynak_tablo
    ON public.semantic_index (kaynak_tablo);

CREATE INDEX IF NOT EXISTS idx_semantic_index_kaynak
    ON public.semantic_index (kaynak_tablo, kaynak_id);

CREATE INDEX IF NOT EXISTS idx_semantic_index_metadata
    ON public.semantic_index
    USING gin (metadata);

-- Not:
-- ivfflat index, tabloya veri eklendikten sonra daha anlamlıdır.
-- Yine de başlangıçta oluşturabiliriz.
CREATE INDEX IF NOT EXISTS idx_semantic_index_embedding
    ON public.semantic_index
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);


COMMIT;b