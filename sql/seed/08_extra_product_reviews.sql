-- Extra product reviews for semantic search demo
-- Adds balanced realistic reviews for every active product

WITH active_products AS (
    SELECT
        u.urun_id,
        u.ad AS urun_adi,
        row_number() OVER (ORDER BY u.ad, u.urun_id) AS product_no,
        lower(
            concat_ws(
                ' ',
                u.ad,
                COALESCE(string_agg(DISTINCT k.ad, ' '), ''),
                COALESCE(string_agg(DISTINCT ust.ad, ' '), '')
            )
        ) AS search_context
    FROM public.urunler u
    LEFT JOIN public.urun_kategorileri uk
        ON uk.urun_id = u.urun_id
    LEFT JOIN public.kategoriler k
        ON k.kategori_id = uk.kategori_id
    LEFT JOIN public.kategoriler ust
        ON ust.kategori_id = k.ust_kategori_id
    WHERE u.aktif_mi = true
    GROUP BY u.urun_id, u.ad
),
customers AS (
    SELECT
        m.musteri_id,
        row_number() OVER (ORDER BY m.musteri_id) AS customer_no
    FROM public.musteriler m
    WHERE m.aktif_mi = true
),
available_customers AS (
    SELECT
        ap.urun_id,
        c.musteri_id,
        row_number() OVER (
            PARTITION BY ap.urun_id
            ORDER BY mod((ap.product_no + c.customer_no)::integer, 30), c.customer_no
        ) AS available_no
    FROM active_products ap
    CROSS JOIN customers c
    LEFT JOIN public.urun_yorumlari uy
        ON uy.urun_id = ap.urun_id
       AND uy.musteri_id = c.musteri_id
    WHERE uy.yorum_id IS NULL
),
review_template AS (
    SELECT *
    FROM (
        VALUES
        (1, 5),
        (2, 5),
        (3, 4),
        (4, 4),
        (5, 3),
        (6, 2),
        (7, 1)
    ) AS template(review_no, puan)
),
review_rows AS (
    SELECT
        ap.urun_id,
        ap.urun_adi,
        ap.search_context,
        rt.review_no,
        rt.puan,
        ac.musteri_id,
        (
            substr(md5('extra-review-' || ap.urun_id::text || '-' || rt.review_no::text), 1, 8) || '-' ||
            substr(md5('extra-review-' || ap.urun_id::text || '-' || rt.review_no::text), 9, 4) || '-' ||
            substr(md5('extra-review-' || ap.urun_id::text || '-' || rt.review_no::text), 13, 4) || '-' ||
            substr(md5('extra-review-' || ap.urun_id::text || '-' || rt.review_no::text), 17, 4) || '-' ||
            substr(md5('extra-review-' || ap.urun_id::text || '-' || rt.review_no::text), 21, 12)
        )::uuid AS yorum_id,
        CASE
            WHEN ap.search_context ~ '(telefon|iphone|galaxy|redmi|poco|oppo|vivo|realme|honor)' THEN 'telefon'
            WHEN ap.search_context ~ '(laptop|macbook|thinkpad|ideapad|vivobook|zenbook|victus|nitro|matebook|monster|tulpar|abra)' THEN 'laptop'
            WHEN ap.search_context ~ '(kulaklık|kulakligi|kulaklığı|airpods|buds|hoparlör|hoparlor)' THEN 'ses'
            WHEN ap.search_context ~ '(tişört|tisort|sweatshirt|gömlek|gomlek|pantolon|mont|giyim)' THEN 'giyim'
            WHEN ap.search_context ~ '(ayakkabı|ayakkabi|bot|sneaker)' THEN 'ayakkabi'
            WHEN ap.search_context ~ '(monitör|monitor)' THEN 'monitor'
            WHEN ap.search_context ~ '(mouse|klavye|keyboard)' THEN 'ekipman'
            WHEN ap.search_context ~ '(powerbank|şarj|sarj|kablo)' THEN 'sarj'
            WHEN ap.search_context ~ '(saat|bileklik|watch)' THEN 'giyilebilir'
            WHEN ap.search_context ~ '(ssd|ram|ekran kartı|ekran karti)' THEN 'parca'
            WHEN ap.search_context ~ '(kahve|süpürge|supurge|ütü|utu|hava temizleyici)' THEN 'ev'
            ELSE 'genel'
        END AS review_group
    FROM active_products ap
    CROSS JOIN review_template rt
    JOIN available_customers ac
        ON ac.urun_id = ap.urun_id
       AND ac.available_no = rt.review_no
),
review_text AS (
    SELECT
        rr.*,
        CASE rr.review_group
            WHEN 'telefon' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Batarya çok iyi' ELSE 'Kamera başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Günlük kullanımda iyi' ELSE 'Fiyatına göre başarılı' END
                    WHEN 3 THEN 'Isınma bazen hissediliyor'
                    WHEN 2 THEN 'Beklediğimden yavaş'
                    ELSE 'Batarya beklentimi karşılamadı'
                END
            WHEN 'laptop' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Performansı çok iyi' ELSE 'Yazılım ve ofis için başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Ekran ve klavye iyi' ELSE 'Oyun performansı yeterli' END
                    WHEN 3 THEN 'Fan sesi orta seviyede'
                    WHEN 2 THEN 'Isınma fazla'
                    ELSE 'Beklentimi karşılamadı'
                END
            WHEN 'ses' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Ses kalitesi çok iyi' ELSE 'Pil süresi başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Bluetooth bağlantısı stabil' ELSE 'Konforlu kullanım' END
                    WHEN 3 THEN 'Baslar biraz baskın'
                    WHEN 2 THEN 'Mikrofon zayıf'
                    ELSE 'Bağlantı sorunları yaşadım'
                END
            WHEN 'giyim' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Kumaşı kaliteli' ELSE 'Kalıbı çok iyi' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Rengi güzel duruyor' ELSE 'Rahat ve kullanışlı' END
                    WHEN 3 THEN 'Beden konusunda kararsız kaldım'
                    WHEN 2 THEN 'Yıkamada biraz çekti'
                    ELSE 'Kumaşı beklentimin altında'
                END
            WHEN 'ayakkabi' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Çok rahat' ELSE 'Tabanı başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Günlük kullanım için iyi' ELSE 'Kalıbı rahat' END
                    WHEN 3 THEN 'Numarası biraz dar'
                    WHEN 2 THEN 'Uzun yürüyüşte rahatsız etti'
                    ELSE 'Numarası küçük geldi'
                END
            WHEN 'monitor' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Ekran kalitesi çok iyi' ELSE 'Oyun için akıcı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Renkleri başarılı' ELSE 'Ofis için yeterli' END
                    WHEN 3 THEN 'Ayak kısmı daha sağlam olabilirdi'
                    WHEN 2 THEN 'Işık sızması fark ettim'
                    ELSE 'Ölü piksel sorunu yaşadım'
                END
            WHEN 'ekipman' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Ergonomisi çok iyi' ELSE 'Oyun performansı başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Tuş hissi güzel' ELSE 'Bağlantı stabil' END
                    WHEN 3 THEN 'RGB güzel ama yazılım karışık'
                    WHEN 2 THEN 'Gecikme hissettirdi'
                    ELSE 'Tuşlar beklentimi karşılamadı'
                END
            WHEN 'sarj' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Şarj hızı iyi' ELSE 'Kapasitesi yeterli' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Fiyat performans başarılı' ELSE 'Malzeme kalitesi iyi' END
                    WHEN 3 THEN 'Biraz ısınıyor'
                    WHEN 2 THEN 'Beklediğim kadar hızlı değil'
                    ELSE 'Kısa sürede sorun çıkardı'
                END
            WHEN 'giyilebilir' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Pil süresi iyi' ELSE 'Spor takibi başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Bildirimler pratik' ELSE 'Ekranı net' END
                    WHEN 3 THEN 'GPS bazen geç bağlanıyor'
                    WHEN 2 THEN 'Nabız ölçümü tutarsız'
                    ELSE 'Bağlantı sık koptu'
                END
            WHEN 'parca' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Performansı çok iyi' ELSE 'Stabil çalışıyor' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Oyunlarda fark ettirdi' ELSE 'Hızı yeterli' END
                    WHEN 3 THEN 'Kurulum sonrası ayar gerekti'
                    WHEN 2 THEN 'Sıcaklık yüksek'
                    ELSE 'Stabilite sorunu yaşadım'
                END
            WHEN 'ev' THEN
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Kullanımı çok kolay' ELSE 'Performansı başarılı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Fiyatına göre iyi' ELSE 'Günlük kullanımda pratik' END
                    WHEN 3 THEN 'Gürültüsü orta seviyede'
                    WHEN 2 THEN 'Beklediğim kadar güçlü değil'
                    ELSE 'Memnun kalmadım'
                END
            ELSE
                CASE rr.puan
                    WHEN 5 THEN CASE rr.review_no WHEN 1 THEN 'Çok memnun kaldım' ELSE 'Beklentimi karşıladı' END
                    WHEN 4 THEN CASE rr.review_no WHEN 3 THEN 'Genel olarak iyi' ELSE 'Fiyatına göre başarılı' END
                    WHEN 3 THEN 'Ortalama bir deneyim'
                    WHEN 2 THEN 'Beklentimin altında kaldı'
                    ELSE 'Memnun kalmadım'
                END
        END AS baslik,
        CASE rr.review_group
            WHEN 'telefon' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' batarya, ekran ve kamera tarafında günlük kullanımda çok iyi bir deneyim sundu.'
                    WHEN 4 THEN rr.urun_adi || ' genel olarak başarılı; performans iyi ancak fiyat biraz daha uygun olabilirdi.'
                    WHEN 3 THEN rr.urun_adi || ' günlük işlerde yeterli fakat uzun kullanımda ısınma ve pil tüketimi fark ediliyor.'
                    WHEN 2 THEN rr.urun_adi || ' beklentimin altında kaldı; uygulama geçişleri ve batarya performansı daha iyi olmalıydı.'
                    ELSE rr.urun_adi || ' ile ciddi memnuniyetsizlik yaşadım; batarya ve performans tarafı beklentimi karşılamadı.'
                END
            WHEN 'laptop' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' ofis, ders ve yazılım geliştirme işlerinde hızlı ve stabil çalışıyor.'
                    WHEN 4 THEN rr.urun_adi || ' performans olarak iyi; fan sesi zaman zaman artsa da genel kullanım başarılı.'
                    WHEN 3 THEN rr.urun_adi || ' temel işler için yeterli fakat ekran ve pil tarafında ortalama bir deneyim sunuyor.'
                    WHEN 2 THEN rr.urun_adi || ' yük altında fazla ısınıyor ve fan sesi beklediğimden yüksek.'
                    ELSE rr.urun_adi || ' beklentimi karşılamadı; performans ve pil deneyimi ciddi şekilde zayıf kaldı.'
                END
            WHEN 'ses' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' ses kalitesi, bağlantı kararlılığı ve konfor açısından oldukça başarılı.'
                    WHEN 4 THEN rr.urun_adi || ' müzik ve görüşmeler için iyi; mikrofon tarafında küçük eksikler var.'
                    WHEN 3 THEN rr.urun_adi || ' günlük kullanımda idare ediyor fakat bas ve konfor dengesi daha iyi olabilirdi.'
                    WHEN 2 THEN rr.urun_adi || ' mikrofon ve bağlantı kalitesi beklentimin altında kaldı.'
                    ELSE rr.urun_adi || ' kullanımında bağlantı kopmaları ve zayıf ses kalitesi nedeniyle memnun kalmadım.'
                END
            WHEN 'giyim' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' kumaş kalitesi, renk ve kalıp açısından beklentimi karşıladı.'
                    WHEN 4 THEN rr.urun_adi || ' rahat ve kullanışlı; yıkama sonrası çok az form değişikliği oldu.'
                    WHEN 3 THEN rr.urun_adi || ' fena değil ama beden ve kalıp konusunda kararsız bıraktı.'
                    WHEN 2 THEN rr.urun_adi || ' yıkama sonrası çekme yaptı ve kumaş dokusu beklentimin altında kaldı.'
                    ELSE rr.urun_adi || ' kumaş, kalıp ve beden uyumu açısından beni memnun etmedi.'
                END
            WHEN 'ayakkabi' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' taban rahatlığı ve kalıp açısından günlük kullanımda çok iyi.'
                    WHEN 4 THEN rr.urun_adi || ' genel olarak rahat; uzun yürüyüşte biraz daha destekli olabilirdi.'
                    WHEN 3 THEN rr.urun_adi || ' kısa kullanımda iyi fakat numara ve kalıp biraz dar geldi.'
                    WHEN 2 THEN rr.urun_adi || ' uzun kullanımda ayağı rahatsız etti ve taban desteği yetersiz kaldı.'
                    ELSE rr.urun_adi || ' numarası küçük geldi ve rahatlık açısından beklentimi karşılamadı.'
                END
            WHEN 'monitor' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' ekran kalitesi, renkler ve yenileme hızı açısından oldukça başarılı.'
                    WHEN 4 THEN rr.urun_adi || ' oyun ve ofis kullanımı için iyi; stand daha sağlam olabilirdi.'
                    WHEN 3 THEN rr.urun_adi || ' görüntü kalitesi orta seviyede, renk ayarı yapmak gerekiyor.'
                    WHEN 2 THEN rr.urun_adi || ' ışık sızması ve panel homojenliği konusunda beklentimin altında kaldı.'
                    ELSE rr.urun_adi || ' ölü piksel ve görüntü sorunları nedeniyle memnun kalmadım.'
                END
            WHEN 'ekipman' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' ergonomi, bağlantı ve oyun performansı açısından çok başarılı.'
                    WHEN 4 THEN rr.urun_adi || ' tuş hissi ve gecikme performansı iyi; yazılımı daha sade olabilirdi.'
                    WHEN 3 THEN rr.urun_adi || ' günlük kullanımda yeterli fakat ergonomi herkes için uygun olmayabilir.'
                    WHEN 2 THEN rr.urun_adi || ' bağlantı ve gecikme tarafında beklentimin altında kaldı.'
                    ELSE rr.urun_adi || ' tuş/klik hissi ve kullanım kararlılığı açısından memnun etmedi.'
                END
            WHEN 'sarj' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' şarj hızı, kapasite ve malzeme kalitesi açısından beklentimi karşıladı.'
                    WHEN 4 THEN rr.urun_adi || ' günlük kullanımda iyi; biraz ısınma olsa da işini yapıyor.'
                    WHEN 3 THEN rr.urun_adi || ' ortalama bir ürün, hız ve dayanıklılık tarafı daha iyi olabilir.'
                    WHEN 2 THEN rr.urun_adi || ' beklediğim kadar hızlı şarj etmedi ve kullanımda ısınma yaptı.'
                    ELSE rr.urun_adi || ' kısa sürede sorun çıkardığı için memnun kalmadım.'
                END
            WHEN 'giyilebilir' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' pil, ekran ve spor takibi tarafında oldukça başarılı.'
                    WHEN 4 THEN rr.urun_adi || ' bildirimler ve günlük takip için iyi; GPS bazen geç bağlanıyor.'
                    WHEN 3 THEN rr.urun_adi || ' temel takiplerde yeterli fakat ölçümler her zaman tutarlı değil.'
                    WHEN 2 THEN rr.urun_adi || ' nabız ve spor takibi tarafında beklentimin altında kaldı.'
                    ELSE rr.urun_adi || ' bağlantı kopmaları ve zayıf pil deneyimi nedeniyle memnun etmedi.'
                END
            WHEN 'parca' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' hız, stabilite ve performans tarafında bilgisayara net katkı sağladı.'
                    WHEN 4 THEN rr.urun_adi || ' genel olarak stabil çalışıyor; sıcaklıklar takip edilmeli.'
                    WHEN 3 THEN rr.urun_adi || ' performans orta seviyede, kurulum sonrası ek ayar yapmak gerekti.'
                    WHEN 2 THEN rr.urun_adi || ' yük altında sıcaklık ve stabilite sorunları yaşattı.'
                    ELSE rr.urun_adi || ' performans ve kararlılık açısından beklentimi karşılamadı.'
                END
            WHEN 'ev' THEN
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' kullanım kolaylığı ve performans açısından evde çok pratik oldu.'
                    WHEN 4 THEN rr.urun_adi || ' günlük kullanımda başarılı; gürültü seviyesi biraz daha düşük olabilirdi.'
                    WHEN 3 THEN rr.urun_adi || ' işini yapıyor fakat fiyat performans açısından ortalama kaldı.'
                    WHEN 2 THEN rr.urun_adi || ' performansı beklentimin altında ve kullanımı sandığım kadar pratik değil.'
                    ELSE rr.urun_adi || ' kullanım deneyimi ve performansı nedeniyle memnun kalmadım.'
                END
            ELSE
                CASE rr.puan
                    WHEN 5 THEN rr.urun_adi || ' beklentimi karşıladı ve günlük kullanımda başarılı oldu.'
                    WHEN 4 THEN rr.urun_adi || ' genel olarak iyi, küçük eksikleri dışında memnun kaldım.'
                    WHEN 3 THEN rr.urun_adi || ' ortalama bir deneyim sundu, daha iyi olabilirdi.'
                    WHEN 2 THEN rr.urun_adi || ' beklentimin altında kaldı ve bazı sorunlar yaşattı.'
                    ELSE rr.urun_adi || ' memnun kalmadığım bir alışveriş deneyimi oldu.'
                END
        END AS icerik
    FROM review_rows rr
)
INSERT INTO public.urun_yorumlari
(yorum_id, urun_id, musteri_id, puan, baslik, icerik, olusturma_tarihi)
SELECT
    yorum_id,
    urun_id,
    musteri_id,
    puan,
    baslik,
    icerik,
    now() - ((review_no * 3 + mod(abs(hashtext(urun_id::text)), 27))::text || ' days')::interval
FROM review_text
ON CONFLICT DO NOTHING;

-- Kontrol sorguları:
-- Toplam yorum sayısı
-- SELECT COUNT(*) FROM urun_yorumlari;

-- Yorumsuz aktif ürün var mı?
-- SELECT u.urun_id, u.ad
-- FROM urunler u
-- LEFT JOIN urun_yorumlari uy ON uy.urun_id = u.urun_id
-- WHERE u.aktif_mi = true
-- GROUP BY u.urun_id, u.ad
-- HAVING COUNT(uy.yorum_id) = 0;

-- Ürün başına yorum sayısı
-- SELECT u.ad, COUNT(uy.yorum_id) AS yorum_sayisi
-- FROM urunler u
-- LEFT JOIN urun_yorumlari uy ON uy.urun_id = u.urun_id
-- WHERE u.aktif_mi = true
-- GROUP BY u.ad
-- ORDER BY yorum_sayisi ASC, u.ad;

-- Puan dağılımı
-- SELECT puan, COUNT(*) AS yorum_sayisi
-- FROM urun_yorumlari
-- GROUP BY puan
-- ORDER BY puan;
