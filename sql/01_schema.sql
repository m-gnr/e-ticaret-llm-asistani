BEGIN;

-- =========================================================
-- 01_schema.sql
-- E-Ticaret LLM Asistanı - Ana Veritabanı Şeması
-- =========================================================
-- İçerik:
-- 1. Extensions
-- 2. Enum Tipleri
-- 3. Ana Tablolar
-- 4. Foreign Key İlişkileri
-- 5. Indexler
-- =========================================================


-- =========================================================
-- 1. EXTENSIONS
-- =========================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =========================================================
-- 2. ENUM TİPLERİ
-- =========================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'indirim_tur') THEN
        CREATE TYPE indirim_tur AS ENUM ('yuzde', 'tutar');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'siparis_durum') THEN
        CREATE TYPE siparis_durum AS ENUM (
            'olusturuldu',
            'onaylandi',
            'hazirlaniyor',
            'kargoya_verildi',
            'teslim_edildi',
            'iptal_edildi',
            'iade_edildi'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'odeme_durum') THEN
        CREATE TYPE odeme_durum AS ENUM (
            'beklemede',
            'basarili',
            'basarisiz',
            'iade_edildi'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kargo_durum') THEN
        CREATE TYPE kargo_durum AS ENUM (
            'olusturuldu',
            'hazirlaniyor',
            'kargoya_verildi',
            'yolda',
            'teslim_edildi',
            'iade_edildi'
        );
    END IF;
END
$$;


-- =========================================================
-- 3. ANA TABLOLAR
-- =========================================================

-- ---------------------------------------------------------
-- 3.1 Müşteriler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.musteriler
(
    musteri_id uuid NOT NULL DEFAULT gen_random_uuid(),
    eposta text NOT NULL,
    telefon text,
    ad text NOT NULL,
    soyad text NOT NULL,
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),
    aktif_mi boolean NOT NULL DEFAULT true,

    CONSTRAINT musteriler_pkey PRIMARY KEY (musteri_id),
    CONSTRAINT musteriler_eposta_key UNIQUE (eposta)
);


-- ---------------------------------------------------------
-- 3.2 Markalar
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.markalar
(
    marka_id uuid NOT NULL DEFAULT gen_random_uuid(),
    ad text NOT NULL,

    CONSTRAINT markalar_pkey PRIMARY KEY (marka_id),
    CONSTRAINT markalar_ad_key UNIQUE (ad)
);


-- ---------------------------------------------------------
-- 3.3 Kategoriler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.kategoriler
(
    kategori_id uuid NOT NULL DEFAULT gen_random_uuid(),
    ad text NOT NULL,
    ust_kategori_id uuid,

    CONSTRAINT kategoriler_pkey PRIMARY KEY (kategori_id),
    CONSTRAINT kategoriler_ust_kategori_id_ad_key UNIQUE (ust_kategori_id, ad)
);


-- ---------------------------------------------------------
-- 3.4 Kuponlar
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.kuponlar
(
    kupon_id uuid NOT NULL DEFAULT gen_random_uuid(),
    kod text NOT NULL,
    indirim_turu indirim_tur NOT NULL,
    deger numeric(12,2) NOT NULL,
    para_birimi char(3) NOT NULL DEFAULT 'TRY',
    baslangic_tarihi timestamp with time zone,
    bitis_tarihi timestamp with time zone,
    min_siparis_tutari numeric(12,2) DEFAULT 0,
    kullanim_limiti integer,
    kullanilan_adet integer NOT NULL DEFAULT 0,
    aktif_mi boolean NOT NULL DEFAULT true,

    CONSTRAINT kuponlar_pkey PRIMARY KEY (kupon_id),
    CONSTRAINT kuponlar_kod_key UNIQUE (kod)
);


-- ---------------------------------------------------------
-- 3.5 Ürünler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.urunler
(
    urun_id uuid NOT NULL DEFAULT gen_random_uuid(),
    marka_id uuid,
    ad text NOT NULL,
    aciklama text,
    aktif_mi boolean NOT NULL DEFAULT true,
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT urunler_pkey PRIMARY KEY (urun_id)
);


-- ---------------------------------------------------------
-- 3.6 Müşteri Adresleri
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.musteri_adresleri
(
    adres_id uuid NOT NULL DEFAULT gen_random_uuid(),
    musteri_id uuid NOT NULL,
    etiket text NOT NULL,
    ad_soyad text NOT NULL,
    telefon text,
    ulke text NOT NULL DEFAULT 'TR',
    il text NOT NULL,
    ilce text NOT NULL,
    mahalle text,
    adres_satiri text NOT NULL,
    posta_kodu text,
    varsayilan_mi boolean NOT NULL DEFAULT false,
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT musteri_adresleri_pkey PRIMARY KEY (adres_id)
);


-- ---------------------------------------------------------
-- 3.7 Ürün Varyantları
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.urun_varyantlari
(
    varyant_id uuid NOT NULL DEFAULT gen_random_uuid(),
    urun_id uuid NOT NULL,
    sku text NOT NULL,
    varyant_adi text NOT NULL,
    ozellikler jsonb NOT NULL DEFAULT '{}'::jsonb,
    para_birimi char(3) NOT NULL DEFAULT 'TRY',
    liste_fiyati numeric(12,2) NOT NULL,
    satis_fiyati numeric(12,2),
    kdv_orani numeric(5,2) NOT NULL DEFAULT 20.00,
    aktif_mi boolean NOT NULL DEFAULT true,

    CONSTRAINT urun_varyantlari_pkey PRIMARY KEY (varyant_id),
    CONSTRAINT urun_varyantlari_sku_key UNIQUE (sku)
);


-- ---------------------------------------------------------
-- 3.8 Stok
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.stok
(
    varyant_id uuid NOT NULL,
    elde_adet integer NOT NULL DEFAULT 0,
    rezerve_adet integer NOT NULL DEFAULT 0,
    guncelleme_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT stok_pkey PRIMARY KEY (varyant_id)
);


-- ---------------------------------------------------------
-- 3.9 Ürün Resimleri
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.urun_resimleri
(
    resim_id uuid NOT NULL DEFAULT gen_random_uuid(),
    urun_id uuid NOT NULL,
    url text NOT NULL,
    sira_no integer NOT NULL DEFAULT 0,

    CONSTRAINT urun_resimleri_pkey PRIMARY KEY (resim_id)
);


-- ---------------------------------------------------------
-- 3.10 Ürün - Kategori İlişkisi
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.urun_kategorileri
(
    urun_id uuid NOT NULL,
    kategori_id uuid NOT NULL,

    CONSTRAINT urun_kategorileri_pkey PRIMARY KEY (urun_id, kategori_id)
);


-- ---------------------------------------------------------
-- 3.11 Sepetler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.sepetler
(
    sepet_id uuid NOT NULL DEFAULT gen_random_uuid(),
    musteri_id uuid NOT NULL,
    durum text NOT NULL DEFAULT 'aktif',
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),
    guncelleme_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT sepetler_pkey PRIMARY KEY (sepet_id)
);


-- ---------------------------------------------------------
-- 3.12 Sepet Öğeleri
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.sepet_ogeleri
(
    sepet_id uuid NOT NULL,
    varyant_id uuid NOT NULL,
    adet integer NOT NULL,
    eklenme_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT sepet_ogeleri_pkey PRIMARY KEY (sepet_id, varyant_id)
);


-- ---------------------------------------------------------
-- 3.13 Siparişler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.siparisler
(
    siparis_id uuid NOT NULL DEFAULT gen_random_uuid(),
    musteri_id uuid NOT NULL,
    siparis_no text NOT NULL,
    durum siparis_durum NOT NULL DEFAULT 'olusturuldu',
    teslimat_adres_id uuid,
    fatura_adres_id uuid,
    para_birimi char(3) NOT NULL DEFAULT 'TRY',
    ara_toplam_tutar numeric(12,2) NOT NULL,
    indirim_tutar numeric(12,2) NOT NULL DEFAULT 0,
    kargo_tutar numeric(12,2) NOT NULL DEFAULT 0,
    vergi_tutar numeric(12,2) NOT NULL DEFAULT 0,
    genel_toplam_tutar numeric(12,2) NOT NULL,
    siparis_tarihi timestamp with time zone NOT NULL DEFAULT now(),
    notlar text,

    CONSTRAINT siparisler_pkey PRIMARY KEY (siparis_id),
    CONSTRAINT siparisler_siparis_no_key UNIQUE (siparis_no)
);


-- ---------------------------------------------------------
-- 3.14 Sipariş Öğeleri
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.siparis_ogeleri
(
    siparis_oge_id uuid NOT NULL DEFAULT gen_random_uuid(),
    siparis_id uuid NOT NULL,
    varyant_id uuid NOT NULL,
    urun_adi_anlik text NOT NULL,
    sku_anlik text NOT NULL,
    birim_fiyat numeric(12,2) NOT NULL,
    adet integer NOT NULL,
    kdv_orani numeric(5,2) NOT NULL DEFAULT 0,
    satir_toplam numeric(12,2) NOT NULL,

    CONSTRAINT siparis_ogeleri_pkey PRIMARY KEY (siparis_oge_id)
);


-- ---------------------------------------------------------
-- 3.15 Sipariş İndirimleri
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.siparis_indirimleri
(
    siparis_id uuid NOT NULL,
    kupon_id uuid,
    kupon_kodu_anlik text,
    indirim_turu indirim_tur,
    indirim_deger numeric(12,2),

    CONSTRAINT siparis_indirimleri_pkey PRIMARY KEY (siparis_id)
);


-- ---------------------------------------------------------
-- 3.16 Ödemeler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.odemeler
(
    odeme_id uuid NOT NULL DEFAULT gen_random_uuid(),
    siparis_id uuid NOT NULL,
    saglayici text NOT NULL,
    saglayici_odeme_id text,
    durum odeme_durum NOT NULL DEFAULT 'beklemede',
    tutar numeric(12,2) NOT NULL,
    para_birimi char(3) NOT NULL DEFAULT 'TRY',
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),
    guncelleme_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT odemeler_pkey PRIMARY KEY (odeme_id)
);


-- ---------------------------------------------------------
-- 3.17 Kargolar
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.kargolar
(
    kargo_id uuid NOT NULL DEFAULT gen_random_uuid(),
    siparis_id uuid NOT NULL,
    kargo_firmasi text NOT NULL,
    takip_no text,
    durum kargo_durum NOT NULL DEFAULT 'olusturuldu',
    kargoya_verilme_tarihi timestamp with time zone,
    teslim_tarihi timestamp with time zone,

    CONSTRAINT kargolar_pkey PRIMARY KEY (kargo_id)
);


-- ---------------------------------------------------------
-- 3.18 İadeler
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.iadeler
(
    iade_id uuid NOT NULL DEFAULT gen_random_uuid(),
    siparis_id uuid NOT NULL,
    musteri_id uuid NOT NULL,
    neden text,
    durum text NOT NULL DEFAULT 'talep_edildi',
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT iadeler_pkey PRIMARY KEY (iade_id)
);


-- ---------------------------------------------------------
-- 3.19 İade Öğeleri
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.iade_ogeleri
(
    iade_oge_id uuid NOT NULL DEFAULT gen_random_uuid(),
    iade_id uuid NOT NULL,
    siparis_oge_id uuid NOT NULL,
    adet integer NOT NULL,

    CONSTRAINT iade_ogeleri_pkey PRIMARY KEY (iade_oge_id)
);


-- ---------------------------------------------------------
-- 3.20 Ürün Yorumları
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.urun_yorumlari
(
    yorum_id uuid NOT NULL DEFAULT gen_random_uuid(),
    urun_id uuid NOT NULL,
    musteri_id uuid NOT NULL,
    puan integer NOT NULL,
    baslik text,
    icerik text,
    olusturma_tarihi timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT urun_yorumlari_pkey PRIMARY KEY (yorum_id),
    CONSTRAINT urun_yorumlari_urun_id_musteri_id_key UNIQUE (urun_id, musteri_id)
);


-- =========================================================
-- 4. FOREIGN KEY İLİŞKİLERİ
-- =========================================================

ALTER TABLE IF EXISTS public.kategoriler
    ADD CONSTRAINT kategoriler_ust_kategori_id_fkey
    FOREIGN KEY (ust_kategori_id)
    REFERENCES public.kategoriler (kategori_id)
    ON UPDATE NO ACTION
    ON DELETE SET NULL;

ALTER TABLE IF EXISTS public.musteri_adresleri
    ADD CONSTRAINT musteri_adresleri_musteri_id_fkey
    FOREIGN KEY (musteri_id)
    REFERENCES public.musteriler (musteri_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.urunler
    ADD CONSTRAINT urunler_marka_id_fkey
    FOREIGN KEY (marka_id)
    REFERENCES public.markalar (marka_id)
    ON UPDATE NO ACTION
    ON DELETE SET NULL;

ALTER TABLE IF EXISTS public.urun_varyantlari
    ADD CONSTRAINT urun_varyantlari_urun_id_fkey
    FOREIGN KEY (urun_id)
    REFERENCES public.urunler (urun_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.stok
    ADD CONSTRAINT stok_varyant_id_fkey
    FOREIGN KEY (varyant_id)
    REFERENCES public.urun_varyantlari (varyant_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.urun_resimleri
    ADD CONSTRAINT urun_resimleri_urun_id_fkey
    FOREIGN KEY (urun_id)
    REFERENCES public.urunler (urun_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.urun_kategorileri
    ADD CONSTRAINT urun_kategorileri_urun_id_fkey
    FOREIGN KEY (urun_id)
    REFERENCES public.urunler (urun_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.urun_kategorileri
    ADD CONSTRAINT urun_kategorileri_kategori_id_fkey
    FOREIGN KEY (kategori_id)
    REFERENCES public.kategoriler (kategori_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.sepetler
    ADD CONSTRAINT sepetler_musteri_id_fkey
    FOREIGN KEY (musteri_id)
    REFERENCES public.musteriler (musteri_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.sepet_ogeleri
    ADD CONSTRAINT sepet_ogeleri_sepet_id_fkey
    FOREIGN KEY (sepet_id)
    REFERENCES public.sepetler (sepet_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.sepet_ogeleri
    ADD CONSTRAINT sepet_ogeleri_varyant_id_fkey
    FOREIGN KEY (varyant_id)
    REFERENCES public.urun_varyantlari (varyant_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.siparisler
    ADD CONSTRAINT siparisler_musteri_id_fkey
    FOREIGN KEY (musteri_id)
    REFERENCES public.musteriler (musteri_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.siparisler
    ADD CONSTRAINT siparisler_teslimat_adres_id_fkey
    FOREIGN KEY (teslimat_adres_id)
    REFERENCES public.musteri_adresleri (adres_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.siparisler
    ADD CONSTRAINT siparisler_fatura_adres_id_fkey
    FOREIGN KEY (fatura_adres_id)
    REFERENCES public.musteri_adresleri (adres_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.siparis_ogeleri
    ADD CONSTRAINT siparis_ogeleri_siparis_id_fkey
    FOREIGN KEY (siparis_id)
    REFERENCES public.siparisler (siparis_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.siparis_ogeleri
    ADD CONSTRAINT siparis_ogeleri_varyant_id_fkey
    FOREIGN KEY (varyant_id)
    REFERENCES public.urun_varyantlari (varyant_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.siparis_indirimleri
    ADD CONSTRAINT siparis_indirimleri_siparis_id_fkey
    FOREIGN KEY (siparis_id)
    REFERENCES public.siparisler (siparis_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.siparis_indirimleri
    ADD CONSTRAINT siparis_indirimleri_kupon_id_fkey
    FOREIGN KEY (kupon_id)
    REFERENCES public.kuponlar (kupon_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.odemeler
    ADD CONSTRAINT odemeler_siparis_id_fkey
    FOREIGN KEY (siparis_id)
    REFERENCES public.siparisler (siparis_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.kargolar
    ADD CONSTRAINT kargolar_siparis_id_fkey
    FOREIGN KEY (siparis_id)
    REFERENCES public.siparisler (siparis_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.iadeler
    ADD CONSTRAINT iadeler_siparis_id_fkey
    FOREIGN KEY (siparis_id)
    REFERENCES public.siparisler (siparis_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.iadeler
    ADD CONSTRAINT iadeler_musteri_id_fkey
    FOREIGN KEY (musteri_id)
    REFERENCES public.musteriler (musteri_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.iade_ogeleri
    ADD CONSTRAINT iade_ogeleri_iade_id_fkey
    FOREIGN KEY (iade_id)
    REFERENCES public.iadeler (iade_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.iade_ogeleri
    ADD CONSTRAINT iade_ogeleri_siparis_oge_id_fkey
    FOREIGN KEY (siparis_oge_id)
    REFERENCES public.siparis_ogeleri (siparis_oge_id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.urun_yorumlari
    ADD CONSTRAINT urun_yorumlari_urun_id_fkey
    FOREIGN KEY (urun_id)
    REFERENCES public.urunler (urun_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public.urun_yorumlari
    ADD CONSTRAINT urun_yorumlari_musteri_id_fkey
    FOREIGN KEY (musteri_id)
    REFERENCES public.musteriler (musteri_id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;


-- =========================================================
-- 5. INDEXLER
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_iadeler_siparis
    ON public.iadeler (siparis_id);

CREATE INDEX IF NOT EXISTS idx_kargolar_siparis
    ON public.kargolar (siparis_id);

CREATE INDEX IF NOT EXISTS idx_musteri_adresleri_musteri
    ON public.musteri_adresleri (musteri_id);

CREATE INDEX IF NOT EXISTS idx_odemeler_siparis
    ON public.odemeler (siparis_id);

CREATE INDEX IF NOT EXISTS idx_sepetler_musteri
    ON public.sepetler (musteri_id);

CREATE INDEX IF NOT EXISTS idx_siparisler_musteri
    ON public.siparisler (musteri_id);

CREATE INDEX IF NOT EXISTS idx_siparis_ogeleri_siparis
    ON public.siparis_ogeleri (siparis_id);

CREATE INDEX IF NOT EXISTS idx_urun_kategorileri_kategori
    ON public.urun_kategorileri (kategori_id);

CREATE INDEX IF NOT EXISTS idx_urun_varyantlari_urun
    ON public.urun_varyantlari (urun_id);


COMMIT;