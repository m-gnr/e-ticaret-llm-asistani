BEGIN;

-- =========================================================
-- 03_embedding_views.sql
-- E-Ticaret LLM Asistanı - Embedding Text View'ları
-- =========================================================
-- Bu dosya, farklı tablolardaki kayıtları semantic search için
-- metinsel forma dönüştürür.
--
-- Python tarafında semantic_index_builder.py bu view'lardan okuyup
-- embedding üretir ve semantic_index tablosuna yazar.
-- =========================================================


-- =========================================================
-- 1. ÜRÜN / VARYANT EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_urunler CASCADE;

CREATE VIEW public.vw_semantic_urunler AS
SELECT
    'urun_varyantlari'::text AS kaynak_tablo,
    uv.varyant_id AS kaynak_id,

    concat_ws(' - ', u.ad, uv.varyant_adi) AS baslik,

    concat_ws(' ',
        'Ürün adı:', u.ad || '.',
        'Marka:', COALESCE(m.ad, 'Belirtilmemiş') || '.',
        'Kategori:', COALESCE(string_agg(DISTINCT k.ad, ', '), 'Belirtilmemiş') || '.',
        'Varyant:', uv.varyant_adi || '.',
        'SKU:', uv.sku || '.',
        'Özellikler:', uv.ozellikler::text || '.',
        'Liste fiyatı:', uv.liste_fiyati::text, uv.para_birimi || '.',
        'Satış fiyatı:', COALESCE(uv.satis_fiyati, uv.liste_fiyati)::text, uv.para_birimi || '.',
        'Stok:', COALESCE(s.elde_adet, 0)::text, 'adet.',
        'Ürün açıklaması:', COALESCE(u.aciklama, '')
    ) AS icerik,

    jsonb_build_object(
        'urun_id', u.urun_id,
        'varyant_id', uv.varyant_id,
        'marka', m.ad,
        'kategoriler', COALESCE(jsonb_agg(DISTINCT k.ad) FILTER (WHERE k.ad IS NOT NULL), '[]'::jsonb),
        'sku', uv.sku,
        'varyant_adi', uv.varyant_adi,
        'ozellikler', uv.ozellikler,
        'liste_fiyati', uv.liste_fiyati,
        'satis_fiyati', COALESCE(uv.satis_fiyati, uv.liste_fiyati),
        'para_birimi', uv.para_birimi,
        'stok', COALESCE(s.elde_adet, 0),
        'aktif_mi', u.aktif_mi AND uv.aktif_mi
    ) AS metadata

FROM public.urun_varyantlari uv
JOIN public.urunler u
    ON u.urun_id = uv.urun_id
LEFT JOIN public.markalar m
    ON m.marka_id = u.marka_id
LEFT JOIN public.stok s
    ON s.varyant_id = uv.varyant_id
LEFT JOIN public.urun_kategorileri uk
    ON uk.urun_id = u.urun_id
LEFT JOIN public.kategoriler k
    ON k.kategori_id = uk.kategori_id
GROUP BY
    uv.varyant_id,
    u.urun_id,
    u.ad,
    u.aciklama,
    u.aktif_mi,
    m.ad,
    uv.varyant_adi,
    uv.sku,
    uv.ozellikler,
    uv.liste_fiyati,
    uv.satis_fiyati,
    uv.para_birimi,
    uv.aktif_mi,
    s.elde_adet;


-- =========================================================
-- 2. KATEGORİ EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_kategoriler CASCADE;

CREATE VIEW public.vw_semantic_kategoriler AS
SELECT
    'kategoriler'::text AS kaynak_tablo,
    k.kategori_id AS kaynak_id,

    k.ad AS baslik,

    concat_ws(' ',
        'Kategori:', k.ad || '.',
        'Üst kategori:', COALESCE(ust.ad, 'Ana kategori') || '.',
        'Bu kategori e-ticaret ürün sınıflandırmasında kullanılır.'
    ) AS icerik,

    jsonb_build_object(
        'kategori_id', k.kategori_id,
        'kategori', k.ad,
        'ust_kategori_id', k.ust_kategori_id,
        'ust_kategori', ust.ad
    ) AS metadata

FROM public.kategoriler k
LEFT JOIN public.kategoriler ust
    ON ust.kategori_id = k.ust_kategori_id;


-- =========================================================
-- 3. MARKA EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_markalar CASCADE;

CREATE VIEW public.vw_semantic_markalar AS
SELECT
    'markalar'::text AS kaynak_tablo,
    m.marka_id AS kaynak_id,

    m.ad AS baslik,

    concat_ws(' ',
        'Marka:', m.ad || '.',
        'Bu marka e-ticaret sisteminde ürünlerle ilişkilidir.',
        'Bu markaya ait ürün sayısı:', COUNT(u.urun_id)::text || '.'
    ) AS icerik,

    jsonb_build_object(
        'marka_id', m.marka_id,
        'marka', m.ad,
        'urun_sayisi', COUNT(u.urun_id)
    ) AS metadata

FROM public.markalar m
LEFT JOIN public.urunler u
    ON u.marka_id = m.marka_id
GROUP BY m.marka_id, m.ad;


-- =========================================================
-- 4. ÜRÜN YORUMLARI EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_yorumlar CASCADE;

CREATE VIEW public.vw_semantic_yorumlar AS
SELECT
    'urun_yorumlari'::text AS kaynak_tablo,
    y.yorum_id AS kaynak_id,

    concat_ws(' - ', u.ad, y.baslik) AS baslik,

    concat_ws(' ',
        'Ürün yorumu.',
        'Ürün:', u.ad || '.',
        'Marka:', COALESCE(m.ad, 'Belirtilmemiş') || '.',
        'Kategori:', COALESCE(string_agg(DISTINCT k.ad, ', '), 'Belirtilmemiş') || '.',
        'Üst kategori:', COALESCE(string_agg(DISTINCT ust.ad, ', '), 'Belirtilmemiş') || '.',
        'Müşteri:', mus.ad, mus.soyad || '.',
        'Puan:', y.puan::text || '.',
        'Başlık:', COALESCE(y.baslik, '') || '.',
        'Yorum içeriği:', COALESCE(y.icerik, '') || '.'
    ) AS icerik,

    jsonb_build_object(
        'yorum_id', y.yorum_id,
        'urun_id', u.urun_id,
        'urun', u.ad,
        'marka', m.ad,
        'musteri_id', mus.musteri_id,
        'puan', y.puan,
        'baslik', y.baslik,
        'olusturma_tarihi', y.olusturma_tarihi,
        'kategoriler',
            COALESCE(
                jsonb_agg(DISTINCT k.ad) FILTER (WHERE k.ad IS NOT NULL),
                '[]'::jsonb
            ),
        'ust_kategoriler',
            COALESCE(
                jsonb_agg(DISTINCT ust.ad) FILTER (WHERE ust.ad IS NOT NULL),
                '[]'::jsonb
            )
    ) AS metadata

FROM public.urun_yorumlari y
JOIN public.urunler u
    ON u.urun_id = y.urun_id
LEFT JOIN public.markalar m
    ON m.marka_id = u.marka_id
JOIN public.musteriler mus
    ON mus.musteri_id = y.musteri_id
LEFT JOIN public.urun_kategorileri uk
    ON uk.urun_id = u.urun_id
LEFT JOIN public.kategoriler k
    ON k.kategori_id = uk.kategori_id
LEFT JOIN public.kategoriler ust
    ON ust.kategori_id = k.ust_kategori_id
GROUP BY
    y.yorum_id,
    y.urun_id,
    y.musteri_id,
    y.puan,
    y.baslik,
    y.icerik,
    y.olusturma_tarihi,
    u.urun_id,
    u.ad,
    m.ad,
    mus.musteri_id,
    mus.ad,
    mus.soyad;


-- =========================================================
-- 5. SİPARİŞ EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_siparisler CASCADE;

CREATE VIEW public.vw_semantic_siparisler AS
SELECT
    'siparisler'::text AS kaynak_tablo,
    s.siparis_id AS kaynak_id,

    concat_ws(' - ', 'Sipariş', s.siparis_no) AS baslik,

    concat_ws(' ',
        'Sipariş kaydı.',
        'Sipariş no:', s.siparis_no || '.',
        'Müşteri:', m.ad, m.soyad || '.',
        'Sipariş durumu:', s.durum::text || '.',
        'Sipariş tarihi:', s.siparis_tarihi::text || '.',
        'Ara toplam:', s.ara_toplam_tutar::text, s.para_birimi || '.',
        'İndirim tutarı:', s.indirim_tutar::text, s.para_birimi || '.',
        'Kargo tutarı:', s.kargo_tutar::text, s.para_birimi || '.',
        'Genel toplam:', s.genel_toplam_tutar::text, s.para_birimi || '.',
        'Notlar:', COALESCE(s.notlar, '') || '.',
        'Sipariş ürünleri:', COALESCE(string_agg(so.urun_adi_anlik || ' adet ' || so.adet::text, ', '), 'Ürün yok') || '.'
    ) AS icerik,

    jsonb_build_object(
        'siparis_id', s.siparis_id,
        'siparis_no', s.siparis_no,
        'musteri_id', s.musteri_id,
        'musteri_ad_soyad', concat_ws(' ', m.ad, m.soyad),
        'durum', s.durum,
        'para_birimi', s.para_birimi,
        'ara_toplam_tutar', s.ara_toplam_tutar,
        'indirim_tutar', s.indirim_tutar,
        'kargo_tutar', s.kargo_tutar,
        'vergi_tutar', s.vergi_tutar,
        'genel_toplam_tutar', s.genel_toplam_tutar,
        'siparis_tarihi', s.siparis_tarihi,
        'urun_sayisi', COUNT(so.siparis_oge_id)
    ) AS metadata

FROM public.siparisler s
JOIN public.musteriler m
    ON m.musteri_id = s.musteri_id
LEFT JOIN public.siparis_ogeleri so
    ON so.siparis_id = s.siparis_id
GROUP BY
    s.siparis_id,
    s.siparis_no,
    s.musteri_id,
    m.ad,
    m.soyad,
    s.durum,
    s.para_birimi,
    s.ara_toplam_tutar,
    s.indirim_tutar,
    s.kargo_tutar,
    s.vergi_tutar,
    s.genel_toplam_tutar,
    s.siparis_tarihi,
    s.notlar;


-- =========================================================
-- 6. KARGO EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_kargolar CASCADE;

CREATE VIEW public.vw_semantic_kargolar AS
SELECT
    'kargolar'::text AS kaynak_tablo,
    k.kargo_id AS kaynak_id,

    concat_ws(' - ', 'Kargo', s.siparis_no, k.kargo_firmasi) AS baslik,

    concat_ws(' ',
        'Kargo kaydı.',
        'Sipariş no:', s.siparis_no || '.',
        'Kargo firması:', k.kargo_firmasi || '.',
        'Takip no:', COALESCE(k.takip_no, 'Belirtilmemiş') || '.',
        'Kargo durumu:', k.durum::text || '.',
        'Müşteri:', m.ad, m.soyad || '.',
        'Kargoya verilme tarihi:', COALESCE(k.kargoya_verilme_tarihi::text, 'Henüz kargoya verilmedi') || '.',
        'Teslim tarihi:', COALESCE(k.teslim_tarihi::text, 'Henüz teslim edilmedi') || '.'
    ) AS icerik,

    jsonb_build_object(
        'kargo_id', k.kargo_id,
        'siparis_id', k.siparis_id,
        'siparis_no', s.siparis_no,
        'kargo_firmasi', k.kargo_firmasi,
        'takip_no', k.takip_no,
        'durum', k.durum,
        'musteri_id', s.musteri_id,
        'musteri_ad_soyad', concat_ws(' ', m.ad, m.soyad),
        'kargoya_verilme_tarihi', k.kargoya_verilme_tarihi,
        'teslim_tarihi', k.teslim_tarihi
    ) AS metadata

FROM public.kargolar k
JOIN public.siparisler s
    ON s.siparis_id = k.siparis_id
JOIN public.musteriler m
    ON m.musteri_id = s.musteri_id;


-- =========================================================
-- 7. İADE EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_iadeler CASCADE;

CREATE VIEW public.vw_semantic_iadeler AS
SELECT
    'iadeler'::text AS kaynak_tablo,
    i.iade_id AS kaynak_id,

    concat_ws(' - ', 'İade', s.siparis_no) AS baslik,

    concat_ws(' ',
        'İade kaydı.',
        'Sipariş no:', s.siparis_no || '.',
        'Müşteri:', m.ad, m.soyad || '.',
        'İade durumu:', i.durum || '.',
        'İade nedeni:', COALESCE(i.neden, 'Belirtilmemiş') || '.',
        'İade edilen ürünler:', COALESCE(string_agg(so.urun_adi_anlik || ' adet ' || io.adet::text, ', '), 'Ürün belirtilmemiş') || '.',
        'Oluşturma tarihi:', i.olusturma_tarihi::text || '.'
    ) AS icerik,

    jsonb_build_object(
        'iade_id', i.iade_id,
        'siparis_id', i.siparis_id,
        'siparis_no', s.siparis_no,
        'musteri_id', i.musteri_id,
        'musteri_ad_soyad', concat_ws(' ', m.ad, m.soyad),
        'durum', i.durum,
        'neden', i.neden,
        'olusturma_tarihi', i.olusturma_tarihi,
        'iade_oge_sayisi', COUNT(io.iade_oge_id)
    ) AS metadata

FROM public.iadeler i
JOIN public.siparisler s
    ON s.siparis_id = i.siparis_id
JOIN public.musteriler m
    ON m.musteri_id = i.musteri_id
LEFT JOIN public.iade_ogeleri io
    ON io.iade_id = i.iade_id
LEFT JOIN public.siparis_ogeleri so
    ON so.siparis_oge_id = io.siparis_oge_id
GROUP BY
    i.iade_id,
    i.siparis_id,
    i.musteri_id,
    i.neden,
    i.durum,
    i.olusturma_tarihi,
    s.siparis_no,
    m.ad,
    m.soyad;


-- =========================================================
-- 8. KUPON EMBEDDING VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_kuponlar CASCADE;

CREATE VIEW public.vw_semantic_kuponlar AS
SELECT
    'kuponlar'::text AS kaynak_tablo,
    k.kupon_id AS kaynak_id,

    concat_ws(' - ', 'Kupon', k.kod) AS baslik,

    concat_ws(' ',
        'Kupon kaydı.',
        'Kupon kodu:', k.kod || '.',
        'İndirim türü:', k.indirim_turu::text || '.',
        'İndirim değeri:', k.deger::text, k.para_birimi || '.',
        'Minimum sipariş tutarı:', COALESCE(k.min_siparis_tutari, 0)::text, k.para_birimi || '.',
        'Kullanım limiti:', COALESCE(k.kullanim_limiti::text, 'Limitsiz') || '.',
        'Kullanılan adet:', k.kullanilan_adet::text || '.',
        'Aktif mi:', CASE WHEN k.aktif_mi THEN 'Evet' ELSE 'Hayır' END || '.',
        'Başlangıç tarihi:', COALESCE(k.baslangic_tarihi::text, 'Belirtilmemiş') || '.',
        'Bitiş tarihi:', COALESCE(k.bitis_tarihi::text, 'Belirtilmemiş') || '.'
    ) AS icerik,

    jsonb_build_object(
        'kupon_id', k.kupon_id,
        'kod', k.kod,
        'indirim_turu', k.indirim_turu,
        'deger', k.deger,
        'para_birimi', k.para_birimi,
        'min_siparis_tutari', k.min_siparis_tutari,
        'kullanim_limiti', k.kullanim_limiti,
        'kullanilan_adet', k.kullanilan_adet,
        'aktif_mi', k.aktif_mi,
        'baslangic_tarihi', k.baslangic_tarihi,
        'bitis_tarihi', k.bitis_tarihi
    ) AS metadata

FROM public.kuponlar k;


-- =========================================================
-- 9. MÜŞTERİ EMBEDDING VIEW
-- =========================================================
-- Not:
-- Kişisel veri içerdiği için gerçek projede dikkatli kullanılmalıdır.
-- Bu proje sentetik veri kullandığı için dahil ediyoruz.

DROP VIEW IF EXISTS public.vw_semantic_musteriler CASCADE;

CREATE VIEW public.vw_semantic_musteriler AS
SELECT
    'musteriler'::text AS kaynak_tablo,
    m.musteri_id AS kaynak_id,

    concat_ws(' ', m.ad, m.soyad) AS baslik,

    concat_ws(' ',
        'Müşteri kaydı.',
        'Ad soyad:', m.ad, m.soyad || '.',
        'E-posta:', m.eposta || '.',
        'Telefon:', COALESCE(m.telefon, 'Belirtilmemiş') || '.',
        'Aktif mi:', CASE WHEN m.aktif_mi THEN 'Evet' ELSE 'Hayır' END || '.',
        'Adres ili:', COALESCE(a.il, 'Belirtilmemiş') || '.',
        'Adres ilçesi:', COALESCE(a.ilce, 'Belirtilmemiş') || '.'
    ) AS icerik,

    jsonb_build_object(
        'musteri_id', m.musteri_id,
        'ad', m.ad,
        'soyad', m.soyad,
        'eposta', m.eposta,
        'telefon', m.telefon,
        'aktif_mi', m.aktif_mi,
        'il', a.il,
        'ilce', a.ilce
    ) AS metadata

FROM public.musteriler m
LEFT JOIN public.musteri_adresleri a
    ON a.musteri_id = m.musteri_id
   AND a.varsayilan_mi = true;


-- =========================================================
-- 10. TÜM SEMANTIC KAYITLARI BİRLEŞTİREN VIEW
-- =========================================================

DROP VIEW IF EXISTS public.vw_semantic_all CASCADE;

CREATE VIEW public.vw_semantic_all AS
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_urunler
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_kategoriler
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_markalar
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_yorumlar
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_siparisler
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_kargolar
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_iadeler
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_kuponlar
UNION ALL
SELECT kaynak_tablo, kaynak_id, baslik, icerik, metadata FROM public.vw_semantic_musteriler;


COMMIT;