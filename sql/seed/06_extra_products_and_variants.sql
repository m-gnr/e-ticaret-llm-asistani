BEGIN;

-- Extra products and variants for semantic search demo
-- Adds realistic brand/product diversity and attribute-filter test data

-- =========================================================
-- 1. EK MARKALAR
-- =========================================================

INSERT INTO public.markalar (marka_id, ad) VALUES
('00000000-0000-0000-0000-000000000127', 'Koton'),
('00000000-0000-0000-0000-000000000128', 'Pierre Cardin'),
('00000000-0000-0000-0000-000000000129', 'Columbia'),
('00000000-0000-0000-0000-000000000130', 'Levi''s'),
('00000000-0000-0000-0000-000000000131', 'New Balance'),
('00000000-0000-0000-0000-000000000132', 'Skechers'),
('00000000-0000-0000-0000-000000000133', 'Converse'),
('00000000-0000-0000-0000-000000000134', 'Poco'),
('00000000-0000-0000-0000-000000000135', 'Oppo'),
('00000000-0000-0000-0000-000000000136', 'Vivo'),
('00000000-0000-0000-0000-000000000137', 'Realme'),
('00000000-0000-0000-0000-000000000138', 'Honor'),
('00000000-0000-0000-0000-000000000139', 'Acer'),
('00000000-0000-0000-0000-000000000140', 'HyperX')
ON CONFLICT (ad) DO NOTHING;

-- =========================================================
-- 2. EK ÜRÜNLER
-- =========================================================

WITH product_seed (code, brand_name, product_name, description, category_name) AS (
    VALUES
    -- Tişört
    ('TSH-LCW-BASIC', 'LC Waikiki', 'LC Waikiki Basic Tişört', 'Günlük kullanım için pamuklu kumaştan üretilmiş, sade tasarımlı basic tişörttür.', 'Tişört'),
    ('TSH-DEF-SLIM', 'Defacto', 'Defacto Slim Fit Tişört', 'Daha dar kalıp sevenler için pamuklu ve esnek yapılı slim fit tişörttür.', 'Tişört'),
    ('TSH-MAVI-OVR', 'Mavi', 'Mavi Oversize Tişört', 'Rahat kesimi ve yumuşak dokusuyla günlük kombinlere uygun oversize tişörttür.', 'Tişört'),
    ('TSH-KOTON-CREW', 'Koton', 'Koton Bisiklet Yaka Tişört', 'Bisiklet yaka tasarımıyla okul, iş ve günlük kullanım için uygun tişörttür.', 'Tişört'),
    ('TSH-NIKE-SW', 'Nike', 'Nike Sportswear Tişört', 'Spor ve günlük kullanım için hafif, nefes alabilen kumaşa sahip tişörttür.', 'Tişört'),
    ('TSH-ADI-ESS', 'Adidas', 'Adidas Essentials Tişört', 'Sade logosu ve rahat kalıbıyla antrenman sonrası günlük kullanım için uygun tişörttür.', 'Tişört'),

    -- Sweatshirt
    ('SWT-DEF-HOOD', 'Defacto', 'Defacto Kapüşonlu Sweatshirt', 'Serin havalarda günlük kullanım için uygun, kapüşonlu ve rahat kalıplı sweatshirt modelidir.', 'Sweatshirt'),
    ('SWT-LCW-BASIC', 'LC Waikiki', 'LC Waikiki Basic Sweatshirt', 'Yumuşak iç dokusu ve sade tasarımıyla günlük kombinler için uygun basic sweatshirttür.', 'Sweatshirt'),
    ('SWT-MAVI-OVR', 'Mavi', 'Mavi Oversize Sweatshirt', 'Bol kesimi ve modern görünümüyle günlük kullanım için rahat oversize sweatshirttür.', 'Sweatshirt'),
    ('SWT-KOTON-ZIP', 'Koton', 'Koton Fermuarlı Sweatshirt', 'Fermuarlı yapısı sayesinde katmanlı giyime uygun pratik sweatshirttür.', 'Sweatshirt'),
    ('SWT-ADI-ESS', 'Adidas', 'Adidas Essentials Sweatshirt', 'Spor sonrası ve günlük kullanım için yumuşak dokulu sweatshirt modelidir.', 'Sweatshirt'),
    ('SWT-NIKE-CLUB', 'Nike', 'Nike Club Fleece Sweatshirt', 'Fleece iç yüzeyiyle sıcak tutan, sade ve sportif sweatshirt modelidir.', 'Sweatshirt'),

    -- Gömlek
    ('GOM-DEF-OXF', 'Defacto', 'Defacto Oxford Gömlek', 'Ofis ve günlük kombinler için uygun, klasik kesimli pamuklu oxford gömlektir.', 'Gömlek'),
    ('GOM-LCW-REG', 'LC Waikiki', 'LC Waikiki Regular Gömlek', 'Regular kalıbı ve kolay kombinlenen renkleriyle günlük kullanıma uygun gömlektir.', 'Gömlek'),
    ('GOM-KOT-KETEN', 'Koton', 'Koton Keten Gömlek', 'Sıcak havalarda hafif ve ferah kullanım sunan keten karışımlı gömlektir.', 'Gömlek'),
    ('GOM-MAVI-DENIM', 'Mavi', 'Mavi Denim Gömlek', 'Denim kumaşı ve rahat kesimiyle casual kombinlere uygun gömlektir.', 'Gömlek'),
    ('GOM-PC-KLASIK', 'Pierre Cardin', 'Pierre Cardin Klasik Gömlek', 'Klasik görünümüyle ofis ve özel gün kombinlerine uygun gömlektir.', 'Gömlek'),

    -- Pantolon
    ('PAN-MAVI-MARCUS', 'Mavi', 'Mavi Marcus Jean Pantolon', 'Günlük kombinlere uygun, dayanıklı denim kumaştan üretilmiş jean pantolondur.', 'Pantolon'),
    ('PAN-LCW-CHINO', 'LC Waikiki', 'LC Waikiki Chino Pantolon', 'Ofis ve günlük kullanım için rahat kesimli chino pantolondur.', 'Pantolon'),
    ('PAN-DEF-SLIM', 'Defacto', 'Defacto Slim Fit Pantolon', 'Modern slim fit kalıbı ile günlük ve smart casual kombinlere uygun pantolondur.', 'Pantolon'),
    ('PAN-KOT-REG', 'Koton', 'Koton Regular Pantolon', 'Regular kalıbı ve sade renk seçenekleriyle günlük kullanıma uygun pantolondur.', 'Pantolon'),
    ('PAN-LEVIS-501', 'Levi''s', 'Levi''s 501 Jean Pantolon', 'Klasik 501 kesimiyle dayanıklı denim kumaştan üretilmiş jean pantolondur.', 'Pantolon'),

    -- Mont
    ('MONT-DEF-SISME', 'Defacto', 'Defacto Şişme Mont', 'Soğuk havalarda günlük kullanım için hafif ve sıcak tutan şişme monttur.', 'Mont'),
    ('MONT-LCW-HOOD', 'LC Waikiki', 'LC Waikiki Kapüşonlu Mont', 'Kapüşonlu yapısı ve sıcak tutan iç dolgusu ile kış kullanımına uygun monttur.', 'Mont'),
    ('MONT-MAVI-DENIM', 'Mavi', 'Mavi Denim Mont', 'Geçiş mevsimlerinde günlük kombinlere uygun denim mont modelidir.', 'Mont'),
    ('MONT-KOT-PARKA', 'Koton', 'Koton Parka Mont', 'Kapüşonlu parka formu ile serin ve yağışlı havalara uygun monttur.', 'Mont'),
    ('MONT-COL-OUT', 'Columbia', 'Columbia Outdoor Mont', 'Outdoor kullanım için rüzgara dayanıklı, sıcak tutan mont modelidir.', 'Mont'),
    ('MONT-NIKE-SW', 'Nike', 'Nike Sportswear Mont', 'Sportif kesimiyle şehir içi kullanım ve hafif antrenman sonrası için uygun monttur.', 'Mont'),

    -- Ayakkabı
    ('SHOE-ADI-RUNFALCON', 'Adidas', 'Adidas Runfalcon 3.0 Spor Ayakkabı', 'Günlük kullanım ve hafif spor aktiviteleri için rahat tabanlı spor ayakkabıdır.', 'Spor Ayakkabı'),
    ('SHOE-NIKE-COURT', 'Nike', 'Nike Court Vision Günlük Ayakkabı', 'Klasik basketbol stilinden ilham alan, günlük kullanım için uygun rahat ayakkabıdır.', 'Günlük Ayakkabı'),
    ('SHOE-NIKE-REV7', 'Nike', 'Nike Revolution 7 Koşu Ayakkabısı', 'Hafif yapısı ve yumuşak taban desteğiyle yürüyüş ve koşu için uygun ayakkabıdır.', 'Koşu Ayakkabısı'),
    ('SHOE-PUMA-SMASH', 'Puma', 'Puma Smash Günlük Ayakkabı', 'Sade tasarımı ve rahat yapısıyla günlük kombinlere uygun sneaker modelidir.', 'Günlük Ayakkabı'),
    ('SHOE-ADI-TERREX', 'Adidas', 'Adidas Terrex Outdoor Bot', 'Doğa yürüyüşü ve zorlu zeminlerde kullanım için dayanıklı outdoor bottur.', 'Bot'),
    ('SHOE-NB-574', 'New Balance', 'New Balance 574 Günlük Ayakkabı', 'Retro koşu stilini günlük konforla birleştiren rahat sneaker modelidir.', 'Günlük Ayakkabı'),
    ('SHOE-SKECH-SUM', 'Skechers', 'Skechers Summits Spor Ayakkabı', 'Hafif tabanı ve yumuşak iç yapısıyla yürüyüş ve günlük kullanım için uygundur.', 'Spor Ayakkabı'),
    ('SHOE-CONV-CHUCK', 'Converse', 'Converse Chuck Taylor Günlük Ayakkabı', 'Kanvas üst yüzeyi ve klasik siluetiyle günlük kombinlere uygun ayakkabıdır.', 'Günlük Ayakkabı'),

    -- Telefon
    ('PH-APPLE-IP11', 'Apple', 'Apple iPhone 11', 'Günlük kullanım için güçlü kamera ve uzun yazılım desteği sunan iOS telefondur.', 'Telefon'),
    ('PH-APPLE-IP12', 'Apple', 'Apple iPhone 12', 'OLED ekranı ve güçlü işlemcisiyle kompakt kullanım isteyenler için uygun iPhone modelidir.', 'Telefon'),
    ('PH-APPLE-IP13', 'Apple', 'Apple iPhone 13', 'Dengeli kamera, performans ve pil ömrü sunan popüler iPhone modelidir.', 'Telefon'),
    ('PH-APPLE-IP14', 'Apple', 'Apple iPhone 14', 'Gelişmiş kamera özellikleri ve güçlü işlemcisiyle günlük kullanım için uygun iOS telefondur.', 'Telefon'),
    ('PH-APPLE-IP15', 'Apple', 'Apple iPhone 15', 'USB-C bağlantı ve güçlü kamera sistemiyle güncel iPhone deneyimi sunar.', 'Telefon'),
    ('PH-APPLE-SE22', 'Apple', 'Apple iPhone SE 2022', 'Kompakt boyut ve iOS deneyimini uygun fiyatla sunan telefondur.', 'Telefon'),
    ('PH-SAM-A15', 'Samsung', 'Samsung Galaxy A15', 'Geniş ekranı ve yüksek batarya kapasitesiyle günlük kullanıma uygun Android telefondur.', 'Telefon'),
    ('PH-SAM-A35', 'Samsung', 'Samsung Galaxy A35', 'Dengeli performans ve kamera özellikleri sunan orta segment Android telefondur.', 'Telefon'),
    ('PH-SAM-A55', 'Samsung', 'Samsung Galaxy A55', 'Güçlü batarya ve kaliteli ekranıyla günlük kullanıma uygun Android telefondur.', 'Telefon'),
    ('PH-SAM-S21FE', 'Samsung', 'Samsung Galaxy S21 FE', 'Amiral gemisi deneyimini daha erişilebilir seviyede sunan Android telefondur.', 'Telefon'),
    ('PH-SAM-S23', 'Samsung', 'Samsung Galaxy S23', 'Kompakt boyut, güçlü işlemci ve kaliteli kamera isteyenler için uygundur.', 'Telefon'),
    ('PH-SAM-S24', 'Samsung', 'Samsung Galaxy S24', 'Güncel amiral gemisi performansı ve gelişmiş ekran teknolojisi sunar.', 'Telefon'),
    ('PH-XIA-RN12', 'Xiaomi', 'Xiaomi Redmi Note 12', 'Fiyat performans odaklı, geniş ekranlı ve uzun pil ömürlü akıllı telefondur.', 'Telefon'),
    ('PH-XIA-RN13', 'Xiaomi', 'Xiaomi Redmi Note 13', 'Geniş ekranı ve dengeli donanımıyla günlük kullanım için uygun telefondur.', 'Telefon'),
    ('PH-XIA-RN13PRO', 'Xiaomi', 'Xiaomi Redmi Note 13 Pro', 'Yüksek depolama ve güçlü kamera özellikleri sunan Redmi Note modelidir.', 'Telefon'),
    ('PH-XIA-13T', 'Xiaomi', 'Xiaomi 13T', 'Performans ve kamera tarafında güçlü özellikler sunan Android telefondur.', 'Telefon'),
    ('PH-POCO-X5PRO', 'Poco', 'Poco X5 Pro', 'Yüksek ekran yenileme hızı ve güçlü donanım sunan fiyat performans telefonudur.', 'Telefon'),
    ('PH-POCO-X6PRO', 'Poco', 'Poco X6 Pro', 'Oyun ve yoğun kullanım için güçlü işlemci ve yüksek depolama sunar.', 'Telefon'),
    ('PH-OPPO-RENO10', 'Oppo', 'Oppo Reno 10', 'Şık tasarım ve dengeli kamera deneyimi sunan Android telefondur.', 'Telefon'),
    ('PH-OPPO-A78', 'Oppo', 'Oppo A78', 'Günlük kullanım için uygun fiyatlı, uzun pil ömürlü Oppo modelidir.', 'Telefon'),
    ('PH-VIVO-V29', 'Vivo', 'Vivo V29', 'İnce tasarımı ve kamera odaklı özellikleriyle öne çıkan Android telefondur.', 'Telefon'),
    ('PH-VIVO-Y36', 'Vivo', 'Vivo Y36', 'Geniş ekran ve yüksek batarya kapasitesiyle günlük kullanım için uygundur.', 'Telefon'),
    ('PH-REALME-11PRO', 'Realme', 'Realme 11 Pro', 'Yüksek depolama ve şık tasarım isteyen kullanıcılar için uygun telefondur.', 'Telefon'),
    ('PH-REALME-C55', 'Realme', 'Realme C55', 'Uygun fiyatlı, geniş ekranlı ve günlük kullanım odaklı Realme modelidir.', 'Telefon'),
    ('PH-HONOR-90', 'Honor', 'Honor 90', 'Yüksek çözünürlüklü ekran ve güçlü kamera özellikleri sunan Android telefondur.', 'Telefon'),
    ('PH-HONOR-X9A', 'Honor', 'Honor X9a', 'İnce tasarım ve uzun pil ömrüyle günlük kullanıma uygun Honor modelidir.', 'Telefon'),

    -- Laptop
    ('LAP-LEN-IP15', 'Lenovo', 'Lenovo IdeaPad 15 Laptop', 'Ofis, okul ve günlük yazılım geliştirme işleri için uygun 15 inç laptop modelidir.', 'Laptop'),
    ('LAP-LEN-TP-E14', 'Lenovo', 'Lenovo ThinkPad E14 Laptop', 'Dayanıklı kasası ve klavyesiyle iş ve okul kullanımına uygun ThinkPad modelidir.', 'Laptop'),
    ('LAP-LEN-LEGION5', 'Lenovo', 'Lenovo Legion 5 Oyuncu Laptop', 'Oyun ve yüksek performans gerektiren işler için güçlü ekran kartlı laptop modelidir.', 'Laptop'),
    ('LAP-ASUS-TUF-A15', 'Asus', 'Asus TUF Gaming A15 Laptop', 'Güçlü işlemci ve ekran kartıyla oyun ve üretkenlik için uygun laptop modelidir.', 'Laptop'),
    ('LAP-ASUS-VIVO15', 'Asus', 'Asus Vivobook 15 Laptop', 'Okul, ofis ve günlük kullanım için dengeli donanım sunan laptop modelidir.', 'Laptop'),
    ('LAP-ASUS-ZEN14', 'Asus', 'Asus Zenbook 14 Ultrabook', 'Hafif gövdesi ve güçlü donanımıyla taşınabilir ultrabook modelidir.', 'Laptop'),
    ('LAP-HP-PAV15', 'HP', 'HP Pavilion 15 Laptop', 'Günlük kullanım ve ofis işleri için dengeli performans sunan HP laptop modelidir.', 'Laptop'),
    ('LAP-HP-VICTUS16', 'HP', 'HP Victus 16 Oyuncu Laptop', 'Oyun ve performans odaklı kullanım için tasarlanmış geniş ekranlı laptop modelidir.', 'Laptop'),
    ('LAP-HP-ENVY', 'HP', 'HP Envy x360 Laptop', 'Dokunmatik ekranlı, dönüştürülebilir yapısıyla iş ve okul kullanımına uygun laptop modelidir.', 'Laptop'),
    ('LAP-DELL-INSP15', 'Dell', 'Dell Inspiron 15 Laptop', 'Günlük kullanım ve ofis işleri için güvenilir Dell laptop modelidir.', 'Laptop'),
    ('LAP-DELL-XPS13', 'Dell', 'Dell XPS 13 Ultrabook', 'Kompakt ve hafif gövdesiyle premium ultrabook deneyimi sunar.', 'Laptop'),
    ('LAP-DELL-G15', 'Dell', 'Dell G15 Oyuncu Laptop', 'Oyuncular ve performans isteyen kullanıcılar için güçlü ekran kartlı laptop modelidir.', 'Laptop'),
    ('LAP-ACER-ASP5', 'Acer', 'Acer Aspire 5 Laptop', 'Öğrenci ve ofis kullanımı için dengeli fiyat performans laptop modelidir.', 'Laptop'),
    ('LAP-ACER-NITRO5', 'Acer', 'Acer Nitro 5 Oyuncu Laptop', 'Gaming ve yoğun işler için güçlü donanım sunan Acer laptop modelidir.', 'Laptop'),
    ('LAP-ACER-SWIFT3', 'Acer', 'Acer Swift 3 Ultrabook', 'Hafif gövdesiyle taşınabilirlik isteyen kullanıcılar için uygun ultrabook modelidir.', 'Laptop'),
    ('LAP-MSI-GF63', 'MSI', 'MSI Thin GF63 Oyuncu Laptop', 'İnce gövdede oyun performansı sunan MSI oyuncu laptop modelidir.', 'Laptop'),
    ('LAP-MSI-KATANA15', 'MSI', 'MSI Katana 15 Oyuncu Laptop', 'Yüksek performanslı oyun ve üretim işleri için tasarlanmış MSI laptop modelidir.', 'Laptop'),
    ('LAP-APPLE-AIR-M1', 'Apple', 'Apple MacBook Air M1', 'Sessiz ve hafif tasarımıyla günlük iş, okul ve yazılım geliştirme için uygun MacBook modelidir.', 'Laptop'),
    ('LAP-APPLE-AIR-M2', 'Apple', 'Apple MacBook Air M2', 'Hafif tasarım, uzun pil ömrü ve güçlü Apple Silicon performansı sunar.', 'Laptop'),
    ('LAP-APPLE-PRO14-M3', 'Apple', 'Apple MacBook Pro 14 M3', 'Profesyonel iş yükleri için güçlü işlemci, kaliteli ekran ve uzun pil ömrü sunar.', 'Laptop'),
    ('LAP-HUAWEI-D15', 'Huawei', 'Huawei MateBook D15', 'İnce gövdesi ve geniş ekranıyla ofis ve okul kullanımı için uygun laptop modelidir.', 'Laptop'),
    ('LAP-HUAWEI-14', 'Huawei', 'Huawei MateBook 14', 'Taşınabilir gövde ve dengeli performans sunan Huawei laptop modelidir.', 'Laptop'),
    ('LAP-MON-ABRAA5', 'Monster', 'Monster Abra A5 Oyuncu Laptop', 'Oyuncular için yüksek performanslı ekran kartı ve güçlü soğutma sunar.', 'Laptop'),
    ('LAP-MON-TULPART7', 'Monster', 'Monster Tulpar T7 Oyuncu Laptop', 'Üst seviye oyun ve üretim işleri için güçlü donanım sunan laptop modelidir.', 'Laptop'),

    -- Kulaklık
    ('AUD-SONY-WHCH520', 'Sony', 'Sony WH-CH520 Kablosuz Kulaklık', 'Hafif tasarım ve uzun pil ömrü sunan bluetooth kulaklıktır.', 'Kulaklık'),
    ('AUD-SAM-BUDSFE', 'Samsung', 'Samsung Galaxy Buds FE', 'Kompakt tasarım ve aktif gürültü azaltma desteği sunan kablosuz kulaklıktır.', 'Kulaklık'),
    ('AUD-JBL-T520BT', 'JBL', 'JBL Tune 520BT Kulaklık', 'Güçlü bas performansı ve katlanabilir tasarımıyla günlük kullanıma uygundur.', 'Kulaklık'),
    ('AUD-APPLE-AIRPODS2', 'Apple', 'Apple AirPods 2. Nesil', 'iPhone ve diğer bluetooth cihazlarla pratik kullanım sunan kablosuz kulaklıktır.', 'Kulaklık'),
    ('AUD-ANKER-Q30', 'Anker', 'Anker Soundcore Life Q30', 'Uzun pil ömrü ve gürültü azaltma desteği sunan bluetooth kulaklıktır.', 'Kulaklık'),
    ('AUD-RAZER-BSV2X', 'Razer', 'Razer BlackShark V2 X Oyuncu Kulaklığı', 'Mikrofonlu ve hafif yapısıyla oyun için tasarlanmış kablolu kulaklıktır.', 'Oyuncu Kulaklığı'),
    ('AUD-LOGI-G435', 'Logitech', 'Logitech G435 Oyuncu Kulaklığı', '2.4GHz kablosuz bağlantı ve hafif tasarım sunan oyuncu kulaklığıdır.', 'Oyuncu Kulaklığı'),
    ('AUD-HYPERX-STINGER', 'HyperX', 'HyperX Cloud Stinger Oyuncu Kulaklığı', 'Rahat kafa bandı ve mikrofonuyla oyun için uygun kablolu kulaklıktır.', 'Oyuncu Kulaklığı'),
    ('AUD-JBL-WAVEBEAM', 'JBL', 'JBL Wave Beam Kulaklık', 'Kompakt kulak içi tasarımı ve bluetooth bağlantısıyla günlük kullanım için uygundur.', 'Kulaklık'),
    ('AUD-XIA-BUDS4L', 'Xiaomi', 'Xiaomi Redmi Buds 4 Lite', 'Hafif yapısı ve pratik bluetooth bağlantısıyla günlük kullanım için uygun kulaklıktır.', 'Kulaklık')
)
INSERT INTO public.urunler (urun_id, marka_id, ad, aciklama, aktif_mi)
SELECT
    (
        substr(md5('extra-product-' || ps.code), 1, 8) || '-' ||
        substr(md5('extra-product-' || ps.code), 9, 4) || '-' ||
        substr(md5('extra-product-' || ps.code), 13, 4) || '-' ||
        substr(md5('extra-product-' || ps.code), 17, 4) || '-' ||
        substr(md5('extra-product-' || ps.code), 21, 12)
    )::uuid,
    m.marka_id,
    ps.product_name,
    ps.description,
    true
FROM product_seed ps
JOIN public.markalar m ON m.ad = ps.brand_name
ON CONFLICT DO NOTHING;

-- =========================================================
-- 3. ÜRÜN - KATEGORİ İLİŞKİLERİ
-- =========================================================

WITH product_seed (code, brand_name, product_name, description, category_name) AS (
    VALUES
    ('TSH-LCW-BASIC', 'LC Waikiki', 'LC Waikiki Basic Tişört', '', 'Tişört'),
    ('TSH-DEF-SLIM', 'Defacto', 'Defacto Slim Fit Tişört', '', 'Tişört'),
    ('TSH-MAVI-OVR', 'Mavi', 'Mavi Oversize Tişört', '', 'Tişört'),
    ('TSH-KOTON-CREW', 'Koton', 'Koton Bisiklet Yaka Tişört', '', 'Tişört'),
    ('TSH-NIKE-SW', 'Nike', 'Nike Sportswear Tişört', '', 'Tişört'),
    ('TSH-ADI-ESS', 'Adidas', 'Adidas Essentials Tişört', '', 'Tişört'),
    ('SWT-DEF-HOOD', 'Defacto', 'Defacto Kapüşonlu Sweatshirt', '', 'Sweatshirt'),
    ('SWT-LCW-BASIC', 'LC Waikiki', 'LC Waikiki Basic Sweatshirt', '', 'Sweatshirt'),
    ('SWT-MAVI-OVR', 'Mavi', 'Mavi Oversize Sweatshirt', '', 'Sweatshirt'),
    ('SWT-KOTON-ZIP', 'Koton', 'Koton Fermuarlı Sweatshirt', '', 'Sweatshirt'),
    ('SWT-ADI-ESS', 'Adidas', 'Adidas Essentials Sweatshirt', '', 'Sweatshirt'),
    ('SWT-NIKE-CLUB', 'Nike', 'Nike Club Fleece Sweatshirt', '', 'Sweatshirt'),
    ('GOM-DEF-OXF', 'Defacto', 'Defacto Oxford Gömlek', '', 'Gömlek'),
    ('GOM-LCW-REG', 'LC Waikiki', 'LC Waikiki Regular Gömlek', '', 'Gömlek'),
    ('GOM-KOT-KETEN', 'Koton', 'Koton Keten Gömlek', '', 'Gömlek'),
    ('GOM-MAVI-DENIM', 'Mavi', 'Mavi Denim Gömlek', '', 'Gömlek'),
    ('GOM-PC-KLASIK', 'Pierre Cardin', 'Pierre Cardin Klasik Gömlek', '', 'Gömlek'),
    ('PAN-MAVI-MARCUS', 'Mavi', 'Mavi Marcus Jean Pantolon', '', 'Pantolon'),
    ('PAN-LCW-CHINO', 'LC Waikiki', 'LC Waikiki Chino Pantolon', '', 'Pantolon'),
    ('PAN-DEF-SLIM', 'Defacto', 'Defacto Slim Fit Pantolon', '', 'Pantolon'),
    ('PAN-KOT-REG', 'Koton', 'Koton Regular Pantolon', '', 'Pantolon'),
    ('PAN-LEVIS-501', 'Levi''s', 'Levi''s 501 Jean Pantolon', '', 'Pantolon'),
    ('MONT-DEF-SISME', 'Defacto', 'Defacto Şişme Mont', '', 'Mont'),
    ('MONT-LCW-HOOD', 'LC Waikiki', 'LC Waikiki Kapüşonlu Mont', '', 'Mont'),
    ('MONT-MAVI-DENIM', 'Mavi', 'Mavi Denim Mont', '', 'Mont'),
    ('MONT-KOT-PARKA', 'Koton', 'Koton Parka Mont', '', 'Mont'),
    ('MONT-COL-OUT', 'Columbia', 'Columbia Outdoor Mont', '', 'Mont'),
    ('MONT-NIKE-SW', 'Nike', 'Nike Sportswear Mont', '', 'Mont'),
    ('SHOE-ADI-RUNFALCON', 'Adidas', 'Adidas Runfalcon 3.0 Spor Ayakkabı', '', 'Spor Ayakkabı'),
    ('SHOE-NIKE-COURT', 'Nike', 'Nike Court Vision Günlük Ayakkabı', '', 'Günlük Ayakkabı'),
    ('SHOE-NIKE-REV7', 'Nike', 'Nike Revolution 7 Koşu Ayakkabısı', '', 'Koşu Ayakkabısı'),
    ('SHOE-PUMA-SMASH', 'Puma', 'Puma Smash Günlük Ayakkabı', '', 'Günlük Ayakkabı'),
    ('SHOE-ADI-TERREX', 'Adidas', 'Adidas Terrex Outdoor Bot', '', 'Bot'),
    ('SHOE-NB-574', 'New Balance', 'New Balance 574 Günlük Ayakkabı', '', 'Günlük Ayakkabı'),
    ('SHOE-SKECH-SUM', 'Skechers', 'Skechers Summits Spor Ayakkabı', '', 'Spor Ayakkabı'),
    ('SHOE-CONV-CHUCK', 'Converse', 'Converse Chuck Taylor Günlük Ayakkabı', '', 'Günlük Ayakkabı'),
    ('PH-APPLE-IP11', 'Apple', 'Apple iPhone 11', '', 'Telefon'),
    ('PH-APPLE-IP12', 'Apple', 'Apple iPhone 12', '', 'Telefon'),
    ('PH-APPLE-IP13', 'Apple', 'Apple iPhone 13', '', 'Telefon'),
    ('PH-APPLE-IP14', 'Apple', 'Apple iPhone 14', '', 'Telefon'),
    ('PH-APPLE-IP15', 'Apple', 'Apple iPhone 15', '', 'Telefon'),
    ('PH-APPLE-SE22', 'Apple', 'Apple iPhone SE 2022', '', 'Telefon'),
    ('PH-SAM-A15', 'Samsung', 'Samsung Galaxy A15', '', 'Telefon'),
    ('PH-SAM-A35', 'Samsung', 'Samsung Galaxy A35', '', 'Telefon'),
    ('PH-SAM-A55', 'Samsung', 'Samsung Galaxy A55', '', 'Telefon'),
    ('PH-SAM-S21FE', 'Samsung', 'Samsung Galaxy S21 FE', '', 'Telefon'),
    ('PH-SAM-S23', 'Samsung', 'Samsung Galaxy S23', '', 'Telefon'),
    ('PH-SAM-S24', 'Samsung', 'Samsung Galaxy S24', '', 'Telefon'),
    ('PH-XIA-RN12', 'Xiaomi', 'Xiaomi Redmi Note 12', '', 'Telefon'),
    ('PH-XIA-RN13', 'Xiaomi', 'Xiaomi Redmi Note 13', '', 'Telefon'),
    ('PH-XIA-RN13PRO', 'Xiaomi', 'Xiaomi Redmi Note 13 Pro', '', 'Telefon'),
    ('PH-XIA-13T', 'Xiaomi', 'Xiaomi 13T', '', 'Telefon'),
    ('PH-POCO-X5PRO', 'Poco', 'Poco X5 Pro', '', 'Telefon'),
    ('PH-POCO-X6PRO', 'Poco', 'Poco X6 Pro', '', 'Telefon'),
    ('PH-OPPO-RENO10', 'Oppo', 'Oppo Reno 10', '', 'Telefon'),
    ('PH-OPPO-A78', 'Oppo', 'Oppo A78', '', 'Telefon'),
    ('PH-VIVO-V29', 'Vivo', 'Vivo V29', '', 'Telefon'),
    ('PH-VIVO-Y36', 'Vivo', 'Vivo Y36', '', 'Telefon'),
    ('PH-REALME-11PRO', 'Realme', 'Realme 11 Pro', '', 'Telefon'),
    ('PH-REALME-C55', 'Realme', 'Realme C55', '', 'Telefon'),
    ('PH-HONOR-90', 'Honor', 'Honor 90', '', 'Telefon'),
    ('PH-HONOR-X9A', 'Honor', 'Honor X9a', '', 'Telefon'),
    ('LAP-LEN-IP15', 'Lenovo', 'Lenovo IdeaPad 15 Laptop', '', 'Laptop'),
    ('LAP-LEN-TP-E14', 'Lenovo', 'Lenovo ThinkPad E14 Laptop', '', 'Laptop'),
    ('LAP-LEN-LEGION5', 'Lenovo', 'Lenovo Legion 5 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-ASUS-TUF-A15', 'Asus', 'Asus TUF Gaming A15 Laptop', '', 'Laptop'),
    ('LAP-ASUS-VIVO15', 'Asus', 'Asus Vivobook 15 Laptop', '', 'Laptop'),
    ('LAP-ASUS-ZEN14', 'Asus', 'Asus Zenbook 14 Ultrabook', '', 'Laptop'),
    ('LAP-HP-PAV15', 'HP', 'HP Pavilion 15 Laptop', '', 'Laptop'),
    ('LAP-HP-VICTUS16', 'HP', 'HP Victus 16 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-HP-ENVY', 'HP', 'HP Envy x360 Laptop', '', 'Laptop'),
    ('LAP-DELL-INSP15', 'Dell', 'Dell Inspiron 15 Laptop', '', 'Laptop'),
    ('LAP-DELL-XPS13', 'Dell', 'Dell XPS 13 Ultrabook', '', 'Laptop'),
    ('LAP-DELL-G15', 'Dell', 'Dell G15 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-ACER-ASP5', 'Acer', 'Acer Aspire 5 Laptop', '', 'Laptop'),
    ('LAP-ACER-NITRO5', 'Acer', 'Acer Nitro 5 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-ACER-SWIFT3', 'Acer', 'Acer Swift 3 Ultrabook', '', 'Laptop'),
    ('LAP-MSI-GF63', 'MSI', 'MSI Thin GF63 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-MSI-KATANA15', 'MSI', 'MSI Katana 15 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-APPLE-AIR-M1', 'Apple', 'Apple MacBook Air M1', '', 'Laptop'),
    ('LAP-APPLE-AIR-M2', 'Apple', 'Apple MacBook Air M2', '', 'Laptop'),
    ('LAP-APPLE-PRO14-M3', 'Apple', 'Apple MacBook Pro 14 M3', '', 'Laptop'),
    ('LAP-HUAWEI-D15', 'Huawei', 'Huawei MateBook D15', '', 'Laptop'),
    ('LAP-HUAWEI-14', 'Huawei', 'Huawei MateBook 14', '', 'Laptop'),
    ('LAP-MON-ABRAA5', 'Monster', 'Monster Abra A5 Oyuncu Laptop', '', 'Laptop'),
    ('LAP-MON-TULPART7', 'Monster', 'Monster Tulpar T7 Oyuncu Laptop', '', 'Laptop'),
    ('AUD-SONY-WHCH520', 'Sony', 'Sony WH-CH520 Kablosuz Kulaklık', '', 'Kulaklık'),
    ('AUD-SAM-BUDSFE', 'Samsung', 'Samsung Galaxy Buds FE', '', 'Kulaklık'),
    ('AUD-JBL-T520BT', 'JBL', 'JBL Tune 520BT Kulaklık', '', 'Kulaklık'),
    ('AUD-APPLE-AIRPODS2', 'Apple', 'Apple AirPods 2. Nesil', '', 'Kulaklık'),
    ('AUD-ANKER-Q30', 'Anker', 'Anker Soundcore Life Q30', '', 'Kulaklık'),
    ('AUD-RAZER-BSV2X', 'Razer', 'Razer BlackShark V2 X Oyuncu Kulaklığı', '', 'Oyuncu Kulaklığı'),
    ('AUD-LOGI-G435', 'Logitech', 'Logitech G435 Oyuncu Kulaklığı', '', 'Oyuncu Kulaklığı'),
    ('AUD-HYPERX-STINGER', 'HyperX', 'HyperX Cloud Stinger Oyuncu Kulaklığı', '', 'Oyuncu Kulaklığı'),
    ('AUD-JBL-WAVEBEAM', 'JBL', 'JBL Wave Beam Kulaklık', '', 'Kulaklık'),
    ('AUD-XIA-BUDS4L', 'Xiaomi', 'Xiaomi Redmi Buds 4 Lite', '', 'Kulaklık')
)
INSERT INTO public.urun_kategorileri (urun_id, kategori_id)
SELECT u.urun_id, k.kategori_id
FROM product_seed ps
JOIN public.urunler u ON u.ad = ps.product_name
JOIN public.kategoriler k ON k.ad = ps.category_name
ON CONFLICT (urun_id, kategori_id) DO NOTHING;

-- =========================================================
-- 4. VARYANTLAR VE STOK
-- =========================================================

WITH apparel_variants (product_code, sku_prefix, color, sizes, fabric, fit, has_hood, season, list_price, sale_price) AS (
    VALUES
    -- Tişört
    ('TSH-LCW-BASIC', 'LCW-BASIC-TSH', 'Siyah', ARRAY['S','M','L','XL'], 'Pamuk', 'Regular', NULL::boolean, NULL::text, 399.00, 279.00),
    ('TSH-LCW-BASIC', 'LCW-BASIC-TSH', 'Beyaz', ARRAY['S','M','L'], 'Pamuk', 'Regular', NULL, NULL, 399.00, 279.00),
    ('TSH-LCW-BASIC', 'LCW-BASIC-TSH', 'Gri', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 399.00, 279.00),
    ('TSH-DEF-SLIM', 'DEF-SLIM-TSH', 'Siyah', ARRAY['S','M','L'], 'Pamuk', 'Slim Fit', NULL, NULL, 449.00, 329.00),
    ('TSH-DEF-SLIM', 'DEF-SLIM-TSH', 'Lacivert', ARRAY['M','L','XL'], 'Pamuk', 'Slim Fit', NULL, NULL, 449.00, 329.00),
    ('TSH-DEF-SLIM', 'DEF-SLIM-TSH', 'Beyaz', ARRAY['M','L'], 'Pamuk', 'Slim Fit', NULL, NULL, 449.00, 329.00),
    ('TSH-MAVI-OVR', 'MAVI-OVR-TSH', 'Gri', ARRAY['S','M','L'], 'Pamuk', 'Oversize', NULL, NULL, 599.00, 449.00),
    ('TSH-MAVI-OVR', 'MAVI-OVR-TSH', 'Kırmızı', ARRAY['M','L'], 'Pamuk', 'Oversize', NULL, NULL, 599.00, 449.00),
    ('TSH-MAVI-OVR', 'MAVI-OVR-TSH', 'Yeşil', ARRAY['M','L'], 'Pamuk', 'Oversize', NULL, NULL, 599.00, 449.00),
    ('TSH-KOTON-CREW', 'KOTON-CREW-TSH', 'Beyaz', ARRAY['S','M','L'], 'Pamuk', 'Regular', NULL, NULL, 429.00, 299.00),
    ('TSH-KOTON-CREW', 'KOTON-CREW-TSH', 'Siyah', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 429.00, 299.00),
    ('TSH-KOTON-CREW', 'KOTON-CREW-TSH', 'Lacivert', ARRAY['S','M'], 'Pamuk', 'Regular', NULL, NULL, 429.00, 299.00),
    ('TSH-NIKE-SW', 'NIKE-SW-TSH', 'Siyah', ARRAY['S','M','L'], 'Pamuk', 'Regular', NULL, NULL, 699.00, 549.00),
    ('TSH-NIKE-SW', 'NIKE-SW-TSH', 'Beyaz', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 699.00, 549.00),
    ('TSH-NIKE-SW', 'NIKE-SW-TSH', 'Gri', ARRAY['L','XL'], 'Pamuk', 'Regular', NULL, NULL, 699.00, 549.00),
    ('TSH-ADI-ESS', 'ADI-ESS-TSH', 'Lacivert', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 649.00, 499.00),
    ('TSH-ADI-ESS', 'ADI-ESS-TSH', 'Yeşil', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 649.00, 499.00),
    ('TSH-ADI-ESS', 'ADI-ESS-TSH', 'Kırmızı', ARRAY['S','M'], 'Pamuk', 'Regular', NULL, NULL, 649.00, 499.00),

    -- Sweatshirt
    ('SWT-DEF-HOOD', 'DEF-HOOD-SWT', 'Siyah', ARRAY['S','M','L','XL'], 'Pamuk Karışımı', 'Regular', true, NULL, 999.00, 799.00),
    ('SWT-DEF-HOOD', 'DEF-HOOD-SWT', 'Gri', ARRAY['M','L','XL'], 'Pamuk Karışımı', 'Regular', true, NULL, 999.00, 799.00),
    ('SWT-DEF-HOOD', 'DEF-HOOD-SWT', 'Bordo', ARRAY['M','L'], 'Pamuk Karışımı', 'Regular', true, NULL, 999.00, 799.00),
    ('SWT-LCW-BASIC', 'LCW-BASIC-SWT', 'Gri', ARRAY['S','M','L'], 'Pamuk Karışımı', 'Regular', false, NULL, 899.00, 699.00),
    ('SWT-LCW-BASIC', 'LCW-BASIC-SWT', 'Lacivert', ARRAY['M','L','XL'], 'Pamuk Karışımı', 'Regular', false, NULL, 899.00, 699.00),
    ('SWT-LCW-BASIC', 'LCW-BASIC-SWT', 'Bej', ARRAY['S','M'], 'Pamuk Karışımı', 'Regular', false, NULL, 899.00, 699.00),
    ('SWT-MAVI-OVR', 'MAVI-OVR-SWT', 'Siyah', ARRAY['M','L','XL'], 'Pamuk Karışımı', 'Oversize', true, NULL, 1299.00, 999.00),
    ('SWT-MAVI-OVR', 'MAVI-OVR-SWT', 'Haki', ARRAY['M','L'], 'Pamuk Karışımı', 'Oversize', true, NULL, 1299.00, 999.00),
    ('SWT-MAVI-OVR', 'MAVI-OVR-SWT', 'Gri', ARRAY['S','M'], 'Pamuk Karışımı', 'Oversize', true, NULL, 1299.00, 999.00),
    ('SWT-KOTON-ZIP', 'KOTON-ZIP-SWT', 'Bej', ARRAY['S','M','L'], 'Pamuk Karışımı', 'Regular', false, NULL, 1099.00, 849.00),
    ('SWT-KOTON-ZIP', 'KOTON-ZIP-SWT', 'Siyah', ARRAY['M','L'], 'Pamuk Karışımı', 'Regular', false, NULL, 1099.00, 849.00),
    ('SWT-KOTON-ZIP', 'KOTON-ZIP-SWT', 'Lacivert', ARRAY['M','L'], 'Pamuk Karışımı', 'Regular', false, NULL, 1099.00, 849.00),
    ('SWT-ADI-ESS', 'ADI-ESS-SWT', 'Siyah', ARRAY['S','M','L'], 'Pamuk Karışımı', 'Regular', false, NULL, 1499.00, 1199.00),
    ('SWT-ADI-ESS', 'ADI-ESS-SWT', 'Gri', ARRAY['M','L','XL'], 'Pamuk Karışımı', 'Regular', false, NULL, 1499.00, 1199.00),
    ('SWT-ADI-ESS', 'ADI-ESS-SWT', 'Bordo', ARRAY['L','XL'], 'Pamuk Karışımı', 'Regular', false, NULL, 1499.00, 1199.00),
    ('SWT-NIKE-CLUB', 'NIKE-CLUB-SWT', 'Lacivert', ARRAY['S','M','L'], 'Fleece', 'Regular', false, NULL, 1499.00, 1299.00),
    ('SWT-NIKE-CLUB', 'NIKE-CLUB-SWT', 'Haki', ARRAY['M','L'], 'Fleece', 'Regular', false, NULL, 1499.00, 1299.00),
    ('SWT-NIKE-CLUB', 'NIKE-CLUB-SWT', 'Bej', ARRAY['M','XL'], 'Fleece', 'Regular', false, NULL, 1499.00, 1299.00),

    -- Gömlek
    ('GOM-DEF-OXF', 'DEF-OXF-GOM', 'Beyaz', ARRAY['S','M','L','XL'], 'Pamuk', 'Regular', NULL, NULL, 899.00, 699.00),
    ('GOM-DEF-OXF', 'DEF-OXF-GOM', 'Mavi', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 899.00, 699.00),
    ('GOM-DEF-OXF', 'DEF-OXF-GOM', 'Lacivert', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 899.00, 699.00),
    ('GOM-LCW-REG', 'LCW-REG-GOM', 'Beyaz', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 799.00, 599.00),
    ('GOM-LCW-REG', 'LCW-REG-GOM', 'Gri', ARRAY['M','L'], 'Pamuk', 'Regular', NULL, NULL, 799.00, 599.00),
    ('GOM-LCW-REG', 'LCW-REG-GOM', 'Siyah', ARRAY['L','XL'], 'Pamuk', 'Regular', NULL, NULL, 799.00, 599.00),
    ('GOM-KOT-KETEN', 'KOT-KETEN-GOM', 'Bej', ARRAY['S','M','L'], 'Keten', 'Regular', NULL, NULL, 1199.00, 899.00),
    ('GOM-KOT-KETEN', 'KOT-KETEN-GOM', 'Mavi', ARRAY['S','M'], 'Keten', 'Regular', NULL, NULL, 1199.00, 899.00),
    ('GOM-KOT-KETEN', 'KOT-KETEN-GOM', 'Beyaz', ARRAY['M','L'], 'Keten', 'Regular', NULL, NULL, 1199.00, 899.00),
    ('GOM-MAVI-DENIM', 'MAVI-DENIM-GOM', 'Mavi', ARRAY['M','L','XL'], 'Denim', 'Regular', NULL, NULL, 1499.00, 1199.00),
    ('GOM-MAVI-DENIM', 'MAVI-DENIM-GOM', 'Lacivert', ARRAY['M','L'], 'Denim', 'Regular', NULL, NULL, 1499.00, 1199.00),
    ('GOM-MAVI-DENIM', 'MAVI-DENIM-GOM', 'Siyah', ARRAY['M'], 'Denim', 'Regular', NULL, NULL, 1499.00, 1199.00),
    ('GOM-PC-KLASIK', 'PC-KLASIK-GOM', 'Beyaz', ARRAY['M','L','XL'], 'Pamuk', 'Klasik', NULL, NULL, 1499.00, 1199.00),
    ('GOM-PC-KLASIK', 'PC-KLASIK-GOM', 'Lacivert', ARRAY['L','XL'], 'Pamuk', 'Klasik', NULL, NULL, 1499.00, 1199.00),
    ('GOM-PC-KLASIK', 'PC-KLASIK-GOM', 'Gri', ARRAY['M','L'], 'Pamuk', 'Klasik', NULL, NULL, 1499.00, 1199.00),

    -- Pantolon
    ('PAN-MAVI-MARCUS', 'MAVI-MARCUS-PAN', 'Mavi', ARRAY['30','32','34','36'], 'Denim', 'Regular', NULL, NULL, 1799.00, 1399.00),
    ('PAN-MAVI-MARCUS', 'MAVI-MARCUS-PAN', 'Siyah', ARRAY['30','32','34'], 'Denim', 'Regular', NULL, NULL, 1799.00, 1399.00),
    ('PAN-LCW-CHINO', 'LCW-CHINO-PAN', 'Bej', ARRAY['30','32','34'], 'Pamuk', 'Chino', NULL, NULL, 1299.00, 999.00),
    ('PAN-LCW-CHINO', 'LCW-CHINO-PAN', 'Lacivert', ARRAY['30','32','34'], 'Pamuk', 'Chino', NULL, NULL, 1299.00, 999.00),
    ('PAN-LCW-CHINO', 'LCW-CHINO-PAN', 'Gri', ARRAY['32','34'], 'Pamuk', 'Chino', NULL, NULL, 1299.00, 999.00),
    ('PAN-DEF-SLIM', 'DEF-SLIM-PAN', 'Siyah', ARRAY['30','32','34'], 'Pamuk', 'Slim Fit', NULL, NULL, 1199.00, 899.00),
    ('PAN-DEF-SLIM', 'DEF-SLIM-PAN', 'Gri', ARRAY['32','34','36'], 'Pamuk', 'Slim Fit', NULL, NULL, 1199.00, 899.00),
    ('PAN-KOT-REG', 'KOT-REG-PAN', 'Bej', ARRAY['30','32'], 'Pamuk', 'Regular', NULL, NULL, 1199.00, 899.00),
    ('PAN-KOT-REG', 'KOT-REG-PAN', 'Siyah', ARRAY['32','34'], 'Pamuk', 'Regular', NULL, NULL, 1199.00, 899.00),
    ('PAN-KOT-REG', 'KOT-REG-PAN', 'Lacivert', ARRAY['32','34','36'], 'Pamuk', 'Regular', NULL, NULL, 1199.00, 899.00),
    ('PAN-LEVIS-501', 'LEVIS-501-PAN', 'Mavi', ARRAY['30','32','34','36'], 'Denim', 'Regular', NULL, NULL, 2499.00, 1999.00),
    ('PAN-LEVIS-501', 'LEVIS-501-PAN', 'Siyah', ARRAY['32','34'], 'Denim', 'Regular', NULL, NULL, 2499.00, 1999.00),

    -- Mont
    ('MONT-DEF-SISME', 'DEF-SISME-MONT', 'Siyah', ARRAY['M','L','XL'], NULL, 'Regular', true, 'Kış', 2999.00, 2299.00),
    ('MONT-DEF-SISME', 'DEF-SISME-MONT', 'Haki', ARRAY['M','L'], NULL, 'Regular', true, 'Kış', 2999.00, 2299.00),
    ('MONT-DEF-SISME', 'DEF-SISME-MONT', 'Lacivert', ARRAY['L','XL'], NULL, 'Regular', true, 'Kış', 2999.00, 2299.00),
    ('MONT-LCW-HOOD', 'LCW-HOOD-MONT', 'Bej', ARRAY['M','L'], NULL, 'Regular', true, 'Kış', 2499.00, 1899.00),
    ('MONT-LCW-HOOD', 'LCW-HOOD-MONT', 'Siyah', ARRAY['S','M','L'], NULL, 'Regular', true, 'Kış', 2499.00, 1899.00),
    ('MONT-LCW-HOOD', 'LCW-HOOD-MONT', 'Haki', ARRAY['L','XL'], NULL, 'Regular', true, 'Kış', 2499.00, 1899.00),
    ('MONT-MAVI-DENIM', 'MAVI-DENIM-MONT', 'Mavi', ARRAY['M','L','XL'], 'Denim', 'Regular', false, 'Mevsimlik', 2999.00, 2399.00),
    ('MONT-MAVI-DENIM', 'MAVI-DENIM-MONT', 'Siyah', ARRAY['M','L'], 'Denim', 'Regular', false, 'Mevsimlik', 2999.00, 2399.00),
    ('MONT-KOT-PARKA', 'KOT-PARKA-MONT', 'Haki', ARRAY['M','L','XL'], NULL, 'Regular', true, 'Kış', 3499.00, 2799.00),
    ('MONT-KOT-PARKA', 'KOT-PARKA-MONT', 'Bej', ARRAY['S','M','L'], NULL, 'Regular', true, 'Kış', 3499.00, 2799.00),
    ('MONT-COL-OUT', 'COL-OUT-MONT', 'Siyah', ARRAY['M','L','XL'], NULL, 'Outdoor', true, 'Kış', 5999.00, 4999.00),
    ('MONT-COL-OUT', 'COL-OUT-MONT', 'Gri', ARRAY['L','XL'], NULL, 'Outdoor', true, 'Kış', 5999.00, 4999.00),
    ('MONT-COL-OUT', 'COL-OUT-MONT', 'Haki', ARRAY['M','L'], NULL, 'Outdoor', true, 'Kış', 5999.00, 4999.00),
    ('MONT-NIKE-SW', 'NIKE-SW-MONT', 'Siyah', ARRAY['S','M','L'], NULL, 'Regular', false, 'Kış', 4999.00, 3999.00),
    ('MONT-NIKE-SW', 'NIKE-SW-MONT', 'Lacivert', ARRAY['M','L'], NULL, 'Regular', false, 'Kış', 4999.00, 3999.00),
    ('MONT-NIKE-SW', 'NIKE-SW-MONT', 'Gri', ARRAY['M','XL'], NULL, 'Regular', false, 'Kış', 4999.00, 3999.00)
),
shoe_variants (product_code, sku_prefix, color, nums, shoe_type, list_price, sale_price) AS (
    VALUES
    ('SHOE-ADI-RUNFALCON', 'ADI-RUNFALCON', 'Siyah', ARRAY['40','41','42','43'], 'Spor', 2799.00, 2199.00),
    ('SHOE-ADI-RUNFALCON', 'ADI-RUNFALCON', 'Beyaz', ARRAY['40','41','42'], 'Spor', 2799.00, 2199.00),
    ('SHOE-ADI-RUNFALCON', 'ADI-RUNFALCON', 'Lacivert', ARRAY['42','43'], 'Spor', 2799.00, 2199.00),
    ('SHOE-NIKE-COURT', 'NIKE-COURT', 'Siyah', ARRAY['40','41','42','43'], 'Günlük', 3299.00, 2699.00),
    ('SHOE-NIKE-COURT', 'NIKE-COURT', 'Beyaz', ARRAY['40','41','42','43'], 'Günlük', 3299.00, 2699.00),
    ('SHOE-NIKE-COURT', 'NIKE-COURT', 'Gri', ARRAY['42','43'], 'Günlük', 3299.00, 2699.00),
    ('SHOE-NIKE-REV7', 'NIKE-REV7', 'Siyah', ARRAY['41','42','43','44'], 'Koşu', 2999.00, 2499.00),
    ('SHOE-NIKE-REV7', 'NIKE-REV7', 'Beyaz', ARRAY['40','41','42','43'], 'Koşu', 2999.00, 2499.00),
    ('SHOE-NIKE-REV7', 'NIKE-REV7', 'Kırmızı', ARRAY['42','43'], 'Koşu', 2999.00, 2499.00),
    ('SHOE-PUMA-SMASH', 'PUMA-SMASH', 'Beyaz', ARRAY['40','41','42','43'], 'Günlük', 2499.00, 1899.00),
    ('SHOE-PUMA-SMASH', 'PUMA-SMASH', 'Siyah', ARRAY['41','42','43'], 'Günlük', 2499.00, 1899.00),
    ('SHOE-ADI-TERREX', 'ADI-TERREX', 'Siyah', ARRAY['41','42','43','44'], 'Outdoor', 4999.00, 3999.00),
    ('SHOE-ADI-TERREX', 'ADI-TERREX', 'Haki', ARRAY['42','43','44'], 'Outdoor', 4999.00, 3999.00),
    ('SHOE-NB-574', 'NB-574', 'Gri', ARRAY['40','41','42','43'], 'Günlük', 3999.00, 3299.00),
    ('SHOE-NB-574', 'NB-574', 'Lacivert', ARRAY['41','42','43'], 'Günlük', 3999.00, 3299.00),
    ('SHOE-SKECH-SUM', 'SKECH-SUM', 'Siyah', ARRAY['40','41','42','43'], 'Spor', 3499.00, 2799.00),
    ('SHOE-SKECH-SUM', 'SKECH-SUM', 'Beyaz', ARRAY['40','41','42'], 'Spor', 3499.00, 2799.00),
    ('SHOE-CONV-CHUCK', 'CONV-CHUCK', 'Siyah', ARRAY['40','41','42','43'], 'Günlük', 2999.00, 2399.00),
    ('SHOE-CONV-CHUCK', 'CONV-CHUCK', 'Kırmızı', ARRAY['40','41','42'], 'Günlük', 2999.00, 2399.00)
),
phone_variants (product_code, sku_prefix, storage, color, ram, os_name, list_price, sale_price) AS (
    VALUES
    ('PH-APPLE-IP11', 'APPLE-IP11', '64GB', 'Siyah', NULL, 'iOS', 19999.00, 16999.00),
    ('PH-APPLE-IP11', 'APPLE-IP11', '64GB', 'Beyaz', NULL, 'iOS', 19999.00, 16999.00),
    ('PH-APPLE-IP11', 'APPLE-IP11', '128GB', 'Siyah', NULL, 'iOS', 22999.00, 19999.00),
    ('PH-APPLE-IP11', 'APPLE-IP11', '128GB', 'Mor', NULL, 'iOS', 22999.00, 19999.00),
    ('PH-APPLE-IP12', 'APPLE-IP12', '64GB', 'Siyah', NULL, 'iOS', 24999.00, 21999.00),
    ('PH-APPLE-IP12', 'APPLE-IP12', '128GB', 'Siyah', NULL, 'iOS', 27999.00, 24999.00),
    ('PH-APPLE-IP12', 'APPLE-IP12', '128GB', 'Mavi', NULL, 'iOS', 27999.00, 24999.00),
    ('PH-APPLE-IP12', 'APPLE-IP12', '256GB', 'Beyaz', NULL, 'iOS', 31999.00, 28999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '64GB', 'Siyah', NULL, 'iOS', 32999.00, 29999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '128GB', 'Siyah', NULL, 'iOS', 36999.00, 32999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '256GB', 'Siyah', NULL, 'iOS', 41999.00, 37999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '64GB', 'Beyaz', NULL, 'iOS', 32999.00, 29999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '128GB', 'Beyaz', NULL, 'iOS', 36999.00, 32999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '256GB', 'Beyaz', NULL, 'iOS', 41999.00, 37999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '128GB', 'Mavi', NULL, 'iOS', 36999.00, 32999.00),
    ('PH-APPLE-IP13', 'APPLE-IP13', '256GB', 'Mavi', NULL, 'iOS', 41999.00, 37999.00),
    ('PH-APPLE-IP14', 'APPLE-IP14', '128GB', 'Siyah', NULL, 'iOS', 43999.00, 39999.00),
    ('PH-APPLE-IP14', 'APPLE-IP14', '256GB', 'Siyah', NULL, 'iOS', 48999.00, 44999.00),
    ('PH-APPLE-IP14', 'APPLE-IP14', '128GB', 'Mor', NULL, 'iOS', 43999.00, 39999.00),
    ('PH-APPLE-IP14', 'APPLE-IP14', '256GB', 'Mor', NULL, 'iOS', 48999.00, 44999.00),
    ('PH-APPLE-IP14', 'APPLE-IP14', '128GB', 'Beyaz', NULL, 'iOS', 43999.00, 39999.00),
    ('PH-APPLE-IP14', 'APPLE-IP14', '512GB', 'Siyah', NULL, 'iOS', 59999.00, 54999.00),
    ('PH-APPLE-IP15', 'APPLE-IP15', '128GB', 'Siyah', NULL, 'iOS', 49999.00, 45999.00),
    ('PH-APPLE-IP15', 'APPLE-IP15', '256GB', 'Siyah', NULL, 'iOS', 54999.00, 50999.00),
    ('PH-APPLE-IP15', 'APPLE-IP15', '128GB', 'Mavi', NULL, 'iOS', 49999.00, 45999.00),
    ('PH-APPLE-IP15', 'APPLE-IP15', '256GB', 'Mavi', NULL, 'iOS', 54999.00, 50999.00),
    ('PH-APPLE-IP15', 'APPLE-IP15', '128GB', 'Yeşil', NULL, 'iOS', 49999.00, 45999.00),
    ('PH-APPLE-IP15', 'APPLE-IP15', '512GB', 'Siyah', NULL, 'iOS', 59999.00, 54999.00),
    ('PH-APPLE-SE22', 'APPLE-SE22', '64GB', 'Siyah', NULL, 'iOS', 19999.00, 16999.00),
    ('PH-APPLE-SE22', 'APPLE-SE22', '64GB', 'Kırmızı', NULL, 'iOS', 19999.00, 16999.00),
    ('PH-APPLE-SE22', 'APPLE-SE22', '128GB', 'Beyaz', NULL, 'iOS', 22999.00, 19999.00),
    ('PH-SAM-A15', 'SAMSUNG-A15', '128GB', 'Siyah', '4GB', 'Android', 10999.00, 8999.00),
    ('PH-SAM-A15', 'SAMSUNG-A15', '128GB', 'Mavi', '4GB', 'Android', 10999.00, 8999.00),
    ('PH-SAM-A15', 'SAMSUNG-A15', '256GB', 'Siyah', '6GB', 'Android', 12999.00, 10999.00),
    ('PH-SAM-A35', 'SAMSUNG-A35', '128GB', 'Siyah', '6GB', 'Android', 18999.00, 15999.00),
    ('PH-SAM-A35', 'SAMSUNG-A35', '256GB', 'Siyah', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-SAM-A35', 'SAMSUNG-A35', '128GB', 'Mavi', '6GB', 'Android', 18999.00, 15999.00),
    ('PH-SAM-A35', 'SAMSUNG-A35', '256GB', 'Beyaz', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-SAM-A55', 'SAMSUNG-A55', '128GB', 'Siyah', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-SAM-A55', 'SAMSUNG-A55', '256GB', 'Siyah', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-SAM-A55', 'SAMSUNG-A55', '128GB', 'Beyaz', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-SAM-A55', 'SAMSUNG-A55', '256GB', 'Beyaz', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-SAM-A55', 'SAMSUNG-A55', '128GB', 'Mavi', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-SAM-A55', 'SAMSUNG-A55', '256GB', 'Mavi', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-SAM-S21FE', 'SAMSUNG-S21FE', '128GB', 'Gri', '6GB', 'Android', 23999.00, 20999.00),
    ('PH-SAM-S21FE', 'SAMSUNG-S21FE', '128GB', 'Mor', '6GB', 'Android', 23999.00, 20999.00),
    ('PH-SAM-S21FE', 'SAMSUNG-S21FE', '256GB', 'Siyah', '8GB', 'Android', 26999.00, 23999.00),
    ('PH-SAM-S23', 'SAMSUNG-S23', '128GB', 'Siyah', '8GB', 'Android', 39999.00, 35999.00),
    ('PH-SAM-S23', 'SAMSUNG-S23', '256GB', 'Siyah', '8GB', 'Android', 43999.00, 39999.00),
    ('PH-SAM-S23', 'SAMSUNG-S23', '128GB', 'Gri', '8GB', 'Android', 39999.00, 35999.00),
    ('PH-SAM-S23', 'SAMSUNG-S23', '256GB', 'Gri', '8GB', 'Android', 43999.00, 39999.00),
    ('PH-SAM-S23', 'SAMSUNG-S23', '256GB', 'Yeşil', '8GB', 'Android', 43999.00, 39999.00),
    ('PH-SAM-S24', 'SAMSUNG-S24', '128GB', 'Siyah', '8GB', 'Android', 49999.00, 45999.00),
    ('PH-SAM-S24', 'SAMSUNG-S24', '256GB', 'Siyah', '8GB', 'Android', 53999.00, 49999.00),
    ('PH-SAM-S24', 'SAMSUNG-S24', '256GB', 'Gri', '8GB', 'Android', 53999.00, 49999.00),
    ('PH-SAM-S24', 'SAMSUNG-S24', '512GB', 'Siyah', '12GB', 'Android', 59999.00, 54999.00),
    ('PH-XIA-RN12', 'XIAOMI-RN12', '128GB', 'Siyah', '6GB', 'Android', 10999.00, 8999.00),
    ('PH-XIA-RN12', 'XIAOMI-RN12', '128GB', 'Mavi', '6GB', 'Android', 10999.00, 8999.00),
    ('PH-XIA-RN12', 'XIAOMI-RN12', '256GB', 'Gri', '8GB', 'Android', 12999.00, 10999.00),
    ('PH-XIA-RN13', 'XIAOMI-RN13', '128GB', 'Siyah', '6GB', 'Android', 14999.00, 11999.00),
    ('PH-XIA-RN13', 'XIAOMI-RN13', '256GB', 'Siyah', '8GB', 'Android', 16999.00, 13999.00),
    ('PH-XIA-RN13', 'XIAOMI-RN13', '128GB', 'Mavi', '6GB', 'Android', 14999.00, 11999.00),
    ('PH-XIA-RN13', 'XIAOMI-RN13', '256GB', 'Mavi', '8GB', 'Android', 16999.00, 13999.00),
    ('PH-XIA-RN13PRO', 'XIAOMI-RN13PRO', '256GB', 'Siyah', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-XIA-RN13PRO', 'XIAOMI-RN13PRO', '256GB', 'Mor', '8GB', 'Android', 21999.00, 18999.00),
    ('PH-XIA-RN13PRO', 'XIAOMI-RN13PRO', '512GB', 'Siyah', '12GB', 'Android', 26999.00, 23999.00),
    ('PH-XIA-13T', 'XIAOMI-13T', '256GB', 'Siyah', '8GB', 'Android', 29999.00, 26999.00),
    ('PH-XIA-13T', 'XIAOMI-13T', '256GB', 'Mavi', '8GB', 'Android', 29999.00, 26999.00),
    ('PH-XIA-13T', 'XIAOMI-13T', '512GB', 'Siyah', '12GB', 'Android', 34999.00, 31999.00),
    ('PH-POCO-X5PRO', 'POCO-X5PRO', '128GB', 'Siyah', '6GB', 'Android', 16999.00, 13999.00),
    ('PH-POCO-X5PRO', 'POCO-X5PRO', '256GB', 'Siyah', '8GB', 'Android', 19999.00, 16999.00),
    ('PH-POCO-X5PRO', 'POCO-X5PRO', '256GB', 'Mavi', '8GB', 'Android', 19999.00, 16999.00),
    ('PH-POCO-X6PRO', 'POCO-X6PRO', '256GB', 'Siyah', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-POCO-X6PRO', 'POCO-X6PRO', '256GB', 'Gri', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-POCO-X6PRO', 'POCO-X6PRO', '512GB', 'Siyah', '12GB', 'Android', 29999.00, 26999.00),
    ('PH-POCO-X6PRO', 'POCO-X6PRO', '512GB', 'Sarı', '12GB', 'Android', 29999.00, 26999.00),
    ('PH-OPPO-RENO10', 'OPPO-RENO10', '128GB', 'Gri', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-OPPO-RENO10', 'OPPO-RENO10', '256GB', 'Mavi', '8GB', 'Android', 27999.00, 24999.00),
    ('PH-OPPO-RENO10', 'OPPO-RENO10', '256GB', 'Siyah', '8GB', 'Android', 27999.00, 24999.00),
    ('PH-OPPO-A78', 'OPPO-A78', '128GB', 'Siyah', '8GB', 'Android', 14999.00, 12999.00),
    ('PH-OPPO-A78', 'OPPO-A78', '128GB', 'Yeşil', '8GB', 'Android', 14999.00, 12999.00),
    ('PH-OPPO-A78', 'OPPO-A78', '256GB', 'Siyah', '8GB', 'Android', 16999.00, 14999.00),
    ('PH-VIVO-V29', 'VIVO-V29', '256GB', 'Siyah', '8GB', 'Android', 27999.00, 24999.00),
    ('PH-VIVO-V29', 'VIVO-V29', '256GB', 'Mavi', '8GB', 'Android', 27999.00, 24999.00),
    ('PH-VIVO-V29', 'VIVO-V29', '512GB', 'Mor', '12GB', 'Android', 31999.00, 28999.00),
    ('PH-VIVO-Y36', 'VIVO-Y36', '128GB', 'Siyah', '8GB', 'Android', 13999.00, 11999.00),
    ('PH-VIVO-Y36', 'VIVO-Y36', '128GB', 'Altın', '8GB', 'Android', 13999.00, 11999.00),
    ('PH-VIVO-Y36', 'VIVO-Y36', '256GB', 'Mavi', '8GB', 'Android', 15999.00, 13999.00),
    ('PH-REALME-11PRO', 'REALME-11PRO', '256GB', 'Siyah', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-REALME-11PRO', 'REALME-11PRO', '256GB', 'Bej', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-REALME-11PRO', 'REALME-11PRO', '512GB', 'Siyah', '12GB', 'Android', 29999.00, 26999.00),
    ('PH-REALME-C55', 'REALME-C55', '128GB', 'Siyah', '6GB', 'Android', 12999.00, 10999.00),
    ('PH-REALME-C55', 'REALME-C55', '128GB', 'Altın', '6GB', 'Android', 12999.00, 10999.00),
    ('PH-REALME-C55', 'REALME-C55', '256GB', 'Yeşil', '8GB', 'Android', 14999.00, 12999.00),
    ('PH-HONOR-90', 'HONOR-90', '256GB', 'Siyah', '8GB', 'Android', 24999.00, 21999.00),
    ('PH-HONOR-90', 'HONOR-90', '512GB', 'Yeşil', '12GB', 'Android', 29999.00, 26999.00),
    ('PH-HONOR-90', 'HONOR-90', '512GB', 'Mavi', '12GB', 'Android', 29999.00, 26999.00),
    ('PH-HONOR-X9A', 'HONOR-X9A', '128GB', 'Siyah', '6GB', 'Android', 16999.00, 14999.00),
    ('PH-HONOR-X9A', 'HONOR-X9A', '256GB', 'Gri', '8GB', 'Android', 19999.00, 16999.00),
    ('PH-HONOR-X9A', 'HONOR-X9A', '256GB', 'Yeşil', '8GB', 'Android', 19999.00, 16999.00)
),
laptop_variants (product_code, sku_prefix, cpu, ram, storage, gpu, screen, os_name, is_gaming, list_price, sale_price) AS (
    VALUES
    ('LAP-LEN-IP15','LEN-IP15','Intel i5','8GB','256GB SSD','Intel Iris Xe','15.6 inç','Windows',false,24999.00,21999.00),
    ('LAP-LEN-IP15','LEN-IP15','Intel i5','8GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,26999.00,23999.00),
    ('LAP-LEN-IP15','LEN-IP15','Intel i7','16GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,31999.00,28999.00),
    ('LAP-LEN-IP15','LEN-IP15','Intel i7','16GB','1TB SSD','Intel Iris Xe','15.6 inç','Windows',false,34999.00,31999.00),
    ('LAP-LEN-TP-E14','LEN-TPE14','Intel i5','8GB','512GB SSD','Intel Iris Xe','14 inç','Windows',false,32999.00,29999.00),
    ('LAP-LEN-TP-E14','LEN-TPE14','Intel i7','16GB','512GB SSD','Intel Iris Xe','14 inç','Windows',false,39999.00,35999.00),
    ('LAP-LEN-TP-E14','LEN-TPE14','Ryzen 5','16GB','512GB SSD','Dahili Grafik','14 inç','Windows',false,35999.00,32999.00),
    ('LAP-LEN-LEGION5','LEN-LEGION5','Ryzen 5','16GB','512GB SSD','RTX3050','15.6 inç','Windows',true,45999.00,41999.00),
    ('LAP-LEN-LEGION5','LEN-LEGION5','Ryzen 7','16GB','1TB SSD','RTX4060','15.6 inç','Windows',true,59999.00,54999.00),
    ('LAP-LEN-LEGION5','LEN-LEGION5','Ryzen 7','32GB','1TB SSD','RTX4070','16 inç','Windows',true,74999.00,69999.00),
    ('LAP-ASUS-TUF-A15','ASUS-TUF-A15','Ryzen 5','16GB','512GB SSD','RTX4050','15.6 inç','Windows',true,45999.00,41999.00),
    ('LAP-ASUS-TUF-A15','ASUS-TUF-A15','Ryzen 7','16GB','512GB SSD','RTX4050','15.6 inç','Windows',true,49999.00,45999.00),
    ('LAP-ASUS-TUF-A15','ASUS-TUF-A15','Ryzen 7','32GB','1TB SSD','RTX4060','15.6 inç','Windows',true,62999.00,57999.00),
    ('LAP-ASUS-VIVO15','ASUS-VIVO15','Intel i3','8GB','256GB SSD','Dahili Grafik','15.6 inç','Windows',false,19999.00,16999.00),
    ('LAP-ASUS-VIVO15','ASUS-VIVO15','Intel i5','8GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,26999.00,23999.00),
    ('LAP-ASUS-VIVO15','ASUS-VIVO15','Ryzen 5','16GB','512GB SSD','Dahili Grafik','15.6 inç','Windows',false,29999.00,26999.00),
    ('LAP-ASUS-ZEN14','ASUS-ZEN14','Intel i5','16GB','512GB SSD','Intel Iris Xe','14 inç','Windows',false,39999.00,35999.00),
    ('LAP-ASUS-ZEN14','ASUS-ZEN14','Intel i7','16GB','1TB SSD','Intel Iris Xe','14 inç','Windows',false,49999.00,45999.00),
    ('LAP-ASUS-ZEN14','ASUS-ZEN14','Ryzen 7','16GB','1TB SSD','Dahili Grafik','14 inç','Windows',false,48999.00,44999.00),
    ('LAP-HP-PAV15','HP-PAV15','Intel i5','8GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,27999.00,24999.00),
    ('LAP-HP-PAV15','HP-PAV15','Intel i7','16GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,34999.00,31999.00),
    ('LAP-HP-PAV15','HP-PAV15','Ryzen 5','16GB','512GB SSD','Dahili Grafik','15.6 inç','Windows',false,32999.00,29999.00),
    ('LAP-HP-VICTUS16','HP-VICTUS16','Ryzen 5','16GB','512GB SSD','RTX3050','16 inç','Windows',true,45999.00,41999.00),
    ('LAP-HP-VICTUS16','HP-VICTUS16','Intel i7','16GB','1TB SSD','RTX4050','16 inç','Windows',true,57999.00,52999.00),
    ('LAP-HP-VICTUS16','HP-VICTUS16','Ryzen 7','32GB','1TB SSD','RTX4060','16 inç','Windows',true,67999.00,62999.00),
    ('LAP-HP-ENVY','HP-ENVY','Ryzen 5','16GB','512GB SSD','Dahili Grafik','14 inç','Windows',false,42999.00,38999.00),
    ('LAP-HP-ENVY','HP-ENVY','Intel i7','16GB','1TB SSD','Intel Iris Xe','14 inç','Windows',false,52999.00,48999.00),
    ('LAP-DELL-INSP15','DELL-INSP15','Intel i5','8GB','256GB SSD','Intel Iris Xe','15.6 inç','Windows',false,24999.00,21999.00),
    ('LAP-DELL-INSP15','DELL-INSP15','Intel i5','16GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,31999.00,28999.00),
    ('LAP-DELL-INSP15','DELL-INSP15','Intel i7','16GB','1TB SSD','Intel Iris Xe','15.6 inç','Windows',false,39999.00,35999.00),
    ('LAP-DELL-XPS13','DELL-XPS13','Intel i5','16GB','512GB SSD','Intel Iris Xe','13.3 inç','Windows',false,54999.00,49999.00),
    ('LAP-DELL-XPS13','DELL-XPS13','Intel i7','16GB','1TB SSD','Intel Iris Xe','13.3 inç','Windows',false,64999.00,59999.00),
    ('LAP-DELL-XPS13','DELL-XPS13','Intel i7','32GB','1TB SSD','Intel Iris Xe','13.3 inç','Windows',false,74999.00,69999.00),
    ('LAP-DELL-G15','DELL-G15','Intel i5','16GB','512GB SSD','RTX3050','15.6 inç','Windows',true,45999.00,41999.00),
    ('LAP-DELL-G15','DELL-G15','Intel i7','16GB','1TB SSD','RTX4060','15.6 inç','Windows',true,62999.00,57999.00),
    ('LAP-ACER-ASP5','ACER-ASP5','Intel i3','8GB','256GB SSD','Dahili Grafik','15.6 inç','Windows',false,19999.00,16999.00),
    ('LAP-ACER-ASP5','ACER-ASP5','Intel i5','8GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,25999.00,22999.00),
    ('LAP-ACER-ASP5','ACER-ASP5','Ryzen 5','16GB','512GB SSD','Dahili Grafik','15.6 inç','Windows',false,29999.00,26999.00),
    ('LAP-ACER-NITRO5','ACER-NITRO5','Ryzen 5','16GB','512GB SSD','RTX3050','15.6 inç','Windows',true,44999.00,39999.00),
    ('LAP-ACER-NITRO5','ACER-NITRO5','Intel i7','16GB','1TB SSD','RTX4050','15.6 inç','Windows',true,55999.00,50999.00),
    ('LAP-ACER-NITRO5','ACER-NITRO5','Ryzen 7','32GB','1TB SSD','RTX4060','15.6 inç','Windows',true,64999.00,59999.00),
    ('LAP-ACER-SWIFT3','ACER-SWIFT3','Intel i5','8GB','512GB SSD','Intel Iris Xe','14 inç','Windows',false,32999.00,29999.00),
    ('LAP-ACER-SWIFT3','ACER-SWIFT3','Intel i7','16GB','512GB SSD','Intel Iris Xe','14 inç','Windows',false,39999.00,35999.00),
    ('LAP-ACER-SWIFT3','ACER-SWIFT3','Ryzen 7','16GB','1TB SSD','Dahili Grafik','14 inç','Windows',false,42999.00,38999.00),
    ('LAP-MSI-GF63','MSI-GF63','Intel i5','16GB','512GB SSD','RTX3050','15.6 inç','Windows',true,44999.00,39999.00),
    ('LAP-MSI-GF63','MSI-GF63','Intel i7','16GB','512GB SSD','RTX4050','15.6 inç','Windows',true,52999.00,48999.00),
    ('LAP-MSI-KATANA15','MSI-KATANA15','Intel i7','16GB','1TB SSD','RTX4060','15.6 inç','Windows',true,62999.00,57999.00),
    ('LAP-MSI-KATANA15','MSI-KATANA15','Intel i9','32GB','1TB SSD','RTX4070','15.6 inç','Windows',true,79999.00,74999.00),
    ('LAP-APPLE-AIR-M1','APPLE-AIR-M1','Apple M1','8GB','256GB SSD','Dahili Grafik','13.3 inç','macOS',false,29999.00,26999.00),
    ('LAP-APPLE-AIR-M1','APPLE-AIR-M1','Apple M1','8GB','512GB SSD','Dahili Grafik','13.3 inç','macOS',false,34999.00,31999.00),
    ('LAP-APPLE-AIR-M2','APPLE-AIR-M2','Apple M2','8GB','256GB SSD','Dahili Grafik','13.3 inç','macOS',false,39999.00,35999.00),
    ('LAP-APPLE-AIR-M2','APPLE-AIR-M2','Apple M2','8GB','512GB SSD','Dahili Grafik','13.3 inç','macOS',false,45999.00,41999.00),
    ('LAP-APPLE-AIR-M2','APPLE-AIR-M2','Apple M2','16GB','512GB SSD','Dahili Grafik','13.3 inç','macOS',false,52999.00,48999.00),
    ('LAP-APPLE-AIR-M2','APPLE-AIR-M2','Apple M2','16GB','1TB SSD','Dahili Grafik','13.3 inç','macOS',false,59999.00,55999.00),
    ('LAP-APPLE-PRO14-M3','APPLE-PRO14-M3','Apple M3','16GB','512GB SSD','Dahili Grafik','14 inç','macOS',false,64999.00,59999.00),
    ('LAP-APPLE-PRO14-M3','APPLE-PRO14-M3','Apple M3','16GB','1TB SSD','Dahili Grafik','14 inç','macOS',false,72999.00,67999.00),
    ('LAP-APPLE-PRO14-M3','APPLE-PRO14-M3','Apple M3','32GB','1TB SSD','Dahili Grafik','14 inç','macOS',false,79999.00,74999.00),
    ('LAP-HUAWEI-D15','HUAWEI-D15','Intel i5','8GB','512GB SSD','Intel Iris Xe','15.6 inç','Windows',false,27999.00,24999.00),
    ('LAP-HUAWEI-D15','HUAWEI-D15','Ryzen 5','16GB','512GB SSD','Dahili Grafik','15.6 inç','Windows',false,31999.00,28999.00),
    ('LAP-HUAWEI-14','HUAWEI-14','Intel i5','16GB','512GB SSD','Intel Iris Xe','14 inç','Windows',false,39999.00,35999.00),
    ('LAP-HUAWEI-14','HUAWEI-14','Intel i7','16GB','1TB SSD','Intel Iris Xe','14 inç','Windows',false,49999.00,45999.00),
    ('LAP-MON-ABRAA5','MON-ABRAA5','Intel i5','16GB','512GB SSD','RTX3050','15.6 inç','Windows',true,42999.00,38999.00),
    ('LAP-MON-ABRAA5','MON-ABRAA5','Intel i7','16GB','1TB SSD','RTX4050','15.6 inç','Windows',true,54999.00,49999.00),
    ('LAP-MON-TULPART7','MON-TULPART7','Intel i7','32GB','1TB SSD','RTX4060','17 inç','Windows',true,69999.00,64999.00),
    ('LAP-MON-TULPART7','MON-TULPART7','Intel i9','32GB','2TB SSD','RTX4070','17 inç','Windows',true,79999.00,74999.00)
),
audio_variants (product_code, sku_prefix, color, connection, battery, mic, is_gaming, list_price, sale_price) AS (
    VALUES
    ('AUD-SONY-WHCH520', 'SONY-WHCH520', 'Siyah', 'Bluetooth', '50 saat', false, false, 1299.00, 999.00),
    ('AUD-SONY-WHCH520', 'SONY-WHCH520', 'Mavi', 'Bluetooth', '50 saat', false, false, 1299.00, 1049.00),
    ('AUD-SONY-WHCH520', 'SONY-WHCH520', 'Beyaz', 'Bluetooth', '50 saat', false, false, 1299.00, 1049.00),
    ('AUD-SAM-BUDSFE', 'SAMSUNG-BUDSFE', 'Siyah', 'Bluetooth', '30 saat', true, false, 1899.00, 1549.00),
    ('AUD-SAM-BUDSFE', 'SAMSUNG-BUDSFE', 'Beyaz', 'Bluetooth', '30 saat', true, false, 1899.00, 1499.00),
    ('AUD-SAM-BUDSFE', 'SAMSUNG-BUDSFE', 'Mor', 'Bluetooth', '30 saat', true, false, 1899.00, 1599.00),
    ('AUD-JBL-T520BT', 'JBL-T520BT', 'Siyah', 'Bluetooth', '57 saat', false, false, 1399.00, 1099.00),
    ('AUD-JBL-T520BT', 'JBL-T520BT', 'Mavi', 'Bluetooth', '57 saat', false, false, 1399.00, 1099.00),
    ('AUD-JBL-T520BT', 'JBL-T520BT', 'Beyaz', 'Bluetooth', '57 saat', false, false, 1399.00, 1129.00),
    ('AUD-APPLE-AIRPODS2', 'APPLE-AIRPODS2', 'Beyaz', 'Bluetooth', '24 saat', true, false, 5999.00, 4999.00),
    ('AUD-ANKER-Q30', 'ANKER-Q30', 'Siyah', 'Bluetooth', '40 saat', true, false, 3499.00, 2799.00),
    ('AUD-ANKER-Q30', 'ANKER-Q30', 'Mavi', 'Bluetooth', '40 saat', true, false, 3499.00, 2799.00),
    ('AUD-ANKER-Q30', 'ANKER-Q30', 'Beyaz', 'Bluetooth', '40 saat', true, false, 3499.00, 2899.00),
    ('AUD-RAZER-BSV2X', 'RAZER-BSV2X', 'Siyah', 'Kablolu', NULL, true, true, 2299.00, 1799.00),
    ('AUD-RAZER-BSV2X', 'RAZER-BSV2X', 'Beyaz', 'Kablolu', NULL, true, true, 2299.00, 1899.00),
    ('AUD-LOGI-G435', 'LOGI-G435', 'Siyah', '2.4GHz Kablosuz', '18 saat', true, true, 2499.00, 1999.00),
    ('AUD-LOGI-G435', 'LOGI-G435', 'Beyaz', '2.4GHz Kablosuz', '18 saat', true, true, 2499.00, 1999.00),
    ('AUD-LOGI-G435', 'LOGI-G435', 'Mavi', '2.4GHz Kablosuz', '18 saat', true, true, 2499.00, 1999.00),
    ('AUD-HYPERX-STINGER', 'HYPERX-STINGER', 'Siyah', 'Kablolu', NULL, true, true, 1999.00, 1599.00),
    ('AUD-HYPERX-STINGER', 'HYPERX-STINGER', 'Pembe', 'Kablolu', NULL, true, true, 1999.00, 1699.00),
    ('AUD-HYPERX-STINGER', 'HYPERX-STINGER', 'Beyaz', 'Kablolu', NULL, true, true, 1999.00, 1699.00),
    ('AUD-JBL-WAVEBEAM', 'JBL-WAVEBEAM', 'Siyah', 'Bluetooth', '32 saat', true, false, 1799.00, 1399.00),
    ('AUD-JBL-WAVEBEAM', 'JBL-WAVEBEAM', 'Beyaz', 'Bluetooth', '32 saat', true, false, 1799.00, 1399.00),
    ('AUD-JBL-WAVEBEAM', 'JBL-WAVEBEAM', 'Mavi', 'Bluetooth', '32 saat', true, false, 1799.00, 1499.00),
    ('AUD-XIA-BUDS4L', 'XIAOMI-BUDS4L', 'Siyah', 'Bluetooth', '20 saat', true, false, 999.00, 799.00),
    ('AUD-XIA-BUDS4L', 'XIAOMI-BUDS4L', 'Beyaz', 'Bluetooth', '20 saat', true, false, 999.00, 799.00),
    ('AUD-XIA-BUDS4L', 'XIAOMI-BUDS4L', 'Pembe', 'Bluetooth', '20 saat', true, false, 999.00, 849.00)
),
variant_seed AS (
    SELECT
        av.product_code,
        av.sku_prefix || '-' || replace(upper(translate(av.color, 'çğıiöşüÇĞİÖŞÜéÉ', 'cgiiosuCGIOSUEE')), ' ', '') || '-' || size AS sku,
        av.color || ' ' || size AS variant_name,
        jsonb_strip_nulls(jsonb_build_object(
            'renk', av.color,
            'beden', size,
            'kumas', av.fabric,
            'kalip', av.fit,
            'kapuson', av.has_hood,
            'mevsim', av.season
        )) AS attributes,
        av.list_price,
        av.sale_price
    FROM apparel_variants av
    CROSS JOIN LATERAL unnest(av.sizes) AS size

    UNION ALL

    SELECT
        sv.product_code,
        sv.sku_prefix || '-' || replace(upper(translate(sv.color, 'çğıiöşüÇĞİÖŞÜéÉ', 'cgiiosuCGIOSUEE')), ' ', '') || '-' || num AS sku,
        sv.color || ' ' || num AS variant_name,
        jsonb_strip_nulls(jsonb_build_object(
            'tip', sv.shoe_type,
            'renk', sv.color,
            'numara', num,
            'mevsim', CASE WHEN sv.shoe_type = 'Outdoor' THEN 'Kış' END
        )) AS attributes,
        sv.list_price,
        sv.sale_price
    FROM shoe_variants sv
    CROSS JOIN LATERAL unnest(sv.nums) AS num

    UNION ALL

    SELECT
        pv.product_code,
        pv.sku_prefix || '-' || pv.storage || '-' || replace(upper(translate(pv.color, 'çğıiöşüÇĞİÖŞÜéÉ', 'cgiiosuCGIOSUEE')), ' ', '') AS sku,
        pv.storage || ' ' || pv.color AS variant_name,
        jsonb_strip_nulls(jsonb_build_object(
            'renk', pv.color,
            'depolama', pv.storage,
            'ram', pv.ram,
            'isletim_sistemi', pv.os_name
        )) AS attributes,
        pv.list_price,
        pv.sale_price
    FROM phone_variants pv

    UNION ALL

    SELECT
        lv.product_code,
        lv.sku_prefix || '-' || replace(upper(lv.cpu), ' ', '') || '-' || lv.ram || '-' || replace(lv.storage, ' ', '') || '-' || replace(lv.gpu, ' ', '') AS sku,
        lv.cpu || ' ' || lv.ram || ' RAM ' || lv.storage AS variant_name,
        jsonb_strip_nulls(jsonb_build_object(
            'ram', lv.ram,
            'islemci', lv.cpu,
            'depolama', lv.storage,
            'ekran', lv.screen,
            'ekran_karti', lv.gpu,
            'isletim_sistemi', lv.os_name,
            'oyuncu', CASE WHEN lv.is_gaming THEN true END
        )) AS attributes,
        lv.list_price,
        lv.sale_price
    FROM laptop_variants lv

    UNION ALL

    SELECT
        av.product_code,
        av.sku_prefix || '-' || replace(upper(translate(av.color, 'çğıiöşüÇĞİÖŞÜéÉ', 'cgiiosuCGIOSUEE')), ' ', '') AS sku,
        av.color || ' ' || av.connection AS variant_name,
        jsonb_strip_nulls(jsonb_build_object(
            'renk', av.color,
            'baglanti', av.connection,
            'pil_suresi', av.battery,
            'mikrofon', CASE WHEN av.mic THEN true END,
            'oyuncu', CASE WHEN av.is_gaming THEN true END
        )) AS attributes,
        av.list_price,
        av.sale_price
    FROM audio_variants av
),
inserted_variants AS (
    INSERT INTO public.urun_varyantlari
        (varyant_id, urun_id, sku, varyant_adi, ozellikler, para_birimi, liste_fiyati, satis_fiyati, kdv_orani, aktif_mi)
    SELECT
        (
            substr(md5('extra-variant-' || vs.sku), 1, 8) || '-' ||
            substr(md5('extra-variant-' || vs.sku), 9, 4) || '-' ||
            substr(md5('extra-variant-' || vs.sku), 13, 4) || '-' ||
            substr(md5('extra-variant-' || vs.sku), 17, 4) || '-' ||
            substr(md5('extra-variant-' || vs.sku), 21, 12)
        )::uuid,
        (
            substr(md5('extra-product-' || vs.product_code), 1, 8) || '-' ||
            substr(md5('extra-product-' || vs.product_code), 9, 4) || '-' ||
            substr(md5('extra-product-' || vs.product_code), 13, 4) || '-' ||
            substr(md5('extra-product-' || vs.product_code), 17, 4) || '-' ||
            substr(md5('extra-product-' || vs.product_code), 21, 12)
        )::uuid,
        vs.sku,
        vs.variant_name,
        vs.attributes,
        'TRY',
        vs.list_price,
        vs.sale_price,
        20.00,
        true
    FROM variant_seed vs
    ON CONFLICT (sku) DO NOTHING
    RETURNING varyant_id, sku
),
all_extra_variants AS (
    SELECT
        iv.varyant_id,
        iv.sku
    FROM inserted_variants iv

    UNION

    SELECT
        uv.varyant_id,
        vs.sku
    FROM variant_seed vs
    JOIN public.urun_varyantlari uv
        ON uv.sku = vs.sku
)
INSERT INTO public.stok (varyant_id, elde_adet, rezerve_adet)
SELECT
    aev.varyant_id,
    CASE
        WHEN mod(abs(hashtext(aev.sku)), 19) = 0 THEN 0
        ELSE 5 + mod(abs(hashtext(aev.sku)), 36)
    END AS elde_adet,
    CASE
        WHEN mod(abs(hashtext(aev.sku)), 19) = 0 THEN 0
        ELSE mod(abs(hashtext(aev.sku)), 4)
    END AS rezerve_adet
FROM all_extra_variants aev
ON CONFLICT (varyant_id) DO NOTHING;

COMMIT;
