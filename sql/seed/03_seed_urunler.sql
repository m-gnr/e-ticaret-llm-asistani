BEGIN;

-- =========================================================
-- 03_seed_urunler.sql
-- E-Ticaret LLM Asistanı - Ürün, Varyant, Stok, Kategori, Resim Seed Verileri
-- =========================================================
-- Hedef:
-- 40 ürün
-- 60 varyant
-- 60 stok kaydı
-- ürün-kategori eşleşmeleri
-- ürün görsel placeholder kayıtları
-- =========================================================


-- =========================================================
-- 1. ÜRÜNLER
-- =========================================================

INSERT INTO public.urunler
(urun_id, marka_id, ad, aciklama, aktif_mi)
VALUES
-- Kulaklık / Ses
('00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000101', 'Sony WH-CH520 Kablosuz Kulaklık', 'Günlük kullanım için hafif tasarıma sahip, uzun pil ömrü sunan bluetooth kulaklıktır. Online ders, müzik dinleme ve telefon görüşmeleri için uygundur.', true),
('00000000-0000-0000-0000-000000000502', '00000000-0000-0000-0000-000000000102', 'Samsung Galaxy Buds FE', 'Aktif gürültü azaltma desteği, dengeli ses kalitesi ve kompakt tasarımıyla günlük kullanım ve yolculuklar için uygun kablosuz kulaklıktır.', true),
('00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000114', 'JBL Tune 520BT Kulaklık', 'Güçlü bas performansı, katlanabilir tasarımı ve bluetooth bağlantısı ile müzik dinleme ve günlük kullanım için uygundur.', true),
('00000000-0000-0000-0000-000000000504', '00000000-0000-0000-0000-000000000119', 'Razer BlackShark V2 X Oyuncu Kulaklığı', 'Oyun içi sesleri net duymak isteyen kullanıcılar için mikrofonlu, hafif ve konforlu oyuncu kulaklığıdır.', true),
('00000000-0000-0000-0000-000000000505', '00000000-0000-0000-0000-000000000114', 'JBL Go 3 Bluetooth Hoparlör', 'Taşınabilir tasarımı ve güçlü ses çıkışıyla dış mekan, kamp ve günlük müzik kullanımı için uygun bluetooth hoparlördür.', true),

-- Bilgisayar / çevre birimleri
('00000000-0000-0000-0000-000000000506', '00000000-0000-0000-0000-000000000105', 'Logitech K380 Bluetooth Klavye', 'Sessiz tuş yapısı, çoklu cihaz desteği ve kompakt tasarımıyla tablet, laptop ve masaüstü kullanımına uygun kablosuz klavyedir.', true),
('00000000-0000-0000-0000-000000000507', '00000000-0000-0000-0000-000000000105', 'Logitech M350 Pebble Mouse', 'Sessiz tıklama özelliği ve ince tasarımıyla ofis, okul ve günlük bilgisayar kullanımı için uygun kablosuz mouse modelidir.', true),
('00000000-0000-0000-0000-000000000508', '00000000-0000-0000-0000-000000000119', 'Razer DeathAdder Essential Mouse', 'Oyuncular için ergonomik yapıya sahip, hassas sensörlü ve kablolu gaming mouse modelidir.', true),
('00000000-0000-0000-0000-000000000509', '00000000-0000-0000-0000-000000000118', 'Corsair K55 RGB Oyuncu Klavyesi', 'RGB aydınlatmalı, makro tuş destekli ve oyun odaklı kullanım için tasarlanmış kablolu oyuncu klavyesidir.', true),
('00000000-0000-0000-0000-000000000510', '00000000-0000-0000-0000-000000000109', 'Lenovo IdeaPad 15 Laptop', 'Günlük kullanım, ofis işleri, uzaktan eğitim ve temel yazılım geliştirme işleri için uygun 15 inç dizüstü bilgisayardır.', true),
('00000000-0000-0000-0000-000000000511', '00000000-0000-0000-0000-000000000110', 'Asus TUF Gaming A15 Laptop', 'Oyun, yazılım geliştirme ve yüksek performans gerektiren işler için güçlü işlemci ve ekran kartı sunan oyuncu laptopudur.', true),
('00000000-0000-0000-0000-000000000512', '00000000-0000-0000-0000-000000000113', 'Dell 24 İnç Full HD Monitör', 'Ofis, ders ve günlük kullanım için uygun, Full HD çözünürlüklü ve ince çerçeveli monitördür.', true),
('00000000-0000-0000-0000-000000000513', '00000000-0000-0000-0000-000000000111', 'MSI 27 İnç 165Hz Gaming Monitör', 'Yüksek yenileme hızı ve düşük gecikme süresiyle rekabetçi oyunlar için uygun gaming monitördür.', true),

-- Bilgisayar parçaları
('00000000-0000-0000-0000-000000000514', '00000000-0000-0000-0000-000000000117', 'Kingston NV2 1TB NVMe SSD', 'Hızlı okuma yazma değerleriyle laptop ve masaüstü bilgisayarlar için uygun NVMe depolama birimidir.', true),
('00000000-0000-0000-0000-000000000515', '00000000-0000-0000-0000-000000000118', 'Corsair Vengeance 16GB DDR4 RAM', 'Oyun, çoklu görev ve günlük bilgisayar kullanımı için uygun 16GB DDR4 bellek modülüdür.', true),
('00000000-0000-0000-0000-000000000516', '00000000-0000-0000-0000-000000000111', 'MSI GeForce RTX 4060 Ekran Kartı', '1080p ve 1440p oyun performansı için uygun, güncel teknolojileri destekleyen ekran kartıdır.', true),

-- Telefon / aksesuar
('00000000-0000-0000-0000-000000000517', '00000000-0000-0000-0000-000000000103', 'Apple iPhone 13', 'Güçlü işlemcisi, kaliteli kamerası ve uzun yazılım desteğiyle günlük kullanım için uygun akıllı telefondur.', true),
('00000000-0000-0000-0000-000000000518', '00000000-0000-0000-0000-000000000102', 'Samsung Galaxy A55', 'Geniş ekranı, güçlü bataryası ve dengeli kamera performansıyla günlük kullanım için uygun Android telefondur.', true),
('00000000-0000-0000-0000-000000000519', '00000000-0000-0000-0000-000000000104', 'Xiaomi Redmi Note 13', 'Fiyat performans odaklı, yüksek batarya kapasitesi ve geniş ekranıyla günlük kullanım için uygun akıllı telefondur.', true),
('00000000-0000-0000-0000-000000000520', '00000000-0000-0000-0000-000000000115', 'Anker 20W USB-C Hızlı Şarj Cihazı', 'Telefon ve tabletler için kompakt yapılı, USB-C çıkışlı hızlı şarj adaptörüdür.', true),
('00000000-0000-0000-0000-000000000521', '00000000-0000-0000-0000-000000000104', 'Xiaomi 20000 mAh Powerbank', 'Yüksek kapasitesiyle telefon, kulaklık ve tabletleri gün içinde birden fazla kez şarj etmeye uygun taşınabilir bataryadır.', true),
('00000000-0000-0000-0000-000000000522', '00000000-0000-0000-0000-000000000115', 'Anker USB-C to Lightning Kablo', 'iPhone ve iPad cihazlar için hızlı şarj ve veri aktarımına uygun dayanıklı kablodur.', true),

-- Giyilebilir teknoloji
('00000000-0000-0000-0000-000000000523', '00000000-0000-0000-0000-000000000103', 'Apple Watch SE 2. Nesil', 'Spor takibi, bildirim yönetimi, kalp ritmi ölçümü ve günlük aktivite takibi için tasarlanmış akıllı saattir.', true),
('00000000-0000-0000-0000-000000000524', '00000000-0000-0000-0000-000000000116', 'Huawei Watch Fit 3', 'Hafif tasarımı, spor modları ve uzun pil ömrüyle günlük sağlık ve aktivite takibi için uygun akıllı saattir.', true),
('00000000-0000-0000-0000-000000000525', '00000000-0000-0000-0000-000000000104', 'Xiaomi Smart Band 8', 'Adım, kalori, uyku ve spor takibi için uygun fiyatlı akıllı bilekliktir.', true),

-- Ev ve yaşam
('00000000-0000-0000-0000-000000000526', '00000000-0000-0000-0000-000000000107', 'Arzum Okka Minio Türk Kahvesi Makinesi', 'Tek tuşla Türk kahvesi hazırlamaya yardımcı olan, taşma önleme sistemine sahip kompakt kahve makinesidir.', true),
('00000000-0000-0000-0000-000000000527', '00000000-0000-0000-0000-000000000106', 'Philips 3000 Serisi Buharlı Ütü', 'Kırışıklıkları hızlı açmaya yardımcı olan, güçlü buhar çıkışına sahip günlük kullanıma uygun ütüdür.', true),
('00000000-0000-0000-0000-000000000528', '00000000-0000-0000-0000-000000000120', 'Dyson V8 Kablosuz Süpürge', 'Kablosuz kullanım, güçlü çekim gücü ve pratik başlıklarıyla ev temizliği için uygun dikey süpürgedir.', true),
('00000000-0000-0000-0000-000000000529', '00000000-0000-0000-0000-000000000106', 'Philips Hava Temizleyici 800 Serisi', 'Toz, polen ve kötü kokulara karşı iç mekan hava kalitesini artırmaya yardımcı hava temizleyicidir.', true),

-- Giyim
('00000000-0000-0000-0000-000000000530', '00000000-0000-0000-0000-000000000124', 'LC Waikiki Basic Tişört', 'Günlük kullanım için pamuklu kumaştan üretilmiş, sade tasarımlı basic tişörttür.', true),
('00000000-0000-0000-0000-000000000531', '00000000-0000-0000-0000-000000000125', 'Mavi Marcus Jean Pantolon', 'Günlük kombinlere uygun, rahat kesimli ve dayanıklı denim kumaştan üretilmiş jean pantolondur.', true),
('00000000-0000-0000-0000-000000000532', '00000000-0000-0000-0000-000000000126', 'Defacto Kapüşonlu Sweatshirt', 'Serin havalarda günlük kullanım için uygun, kapüşonlu ve rahat kalıplı sweatshirt modelidir.', true),
('00000000-0000-0000-0000-000000000533', '00000000-0000-0000-0000-000000000124', 'LC Waikiki Kışlık Mont', 'Soğuk havalarda kullanım için uygun, kapüşonlu ve sıcak tutan kışlık mont modelidir.', true),
('00000000-0000-0000-0000-000000000534', '00000000-0000-0000-0000-000000000126', 'Defacto Oxford Gömlek', 'Ofis ve günlük kombinler için uygun, klasik kesimli pamuklu gömlektir.', true),

-- Ayakkabı
('00000000-0000-0000-0000-000000000535', '00000000-0000-0000-0000-000000000121', 'Nike Revolution 7 Koşu Ayakkabısı', 'Hafif yapısı ve yumuşak taban desteğiyle yürüyüş ve koşu için uygun spor ayakkabıdır.', true),
('00000000-0000-0000-0000-000000000536', '00000000-0000-0000-0000-000000000122', 'Adidas Runfalcon 3.0 Spor Ayakkabı', 'Günlük kullanım ve hafif spor aktiviteleri için uygun, rahat tabanlı spor ayakkabıdır.', true),
('00000000-0000-0000-0000-000000000537', '00000000-0000-0000-0000-000000000123', 'Puma Smash Günlük Ayakkabı', 'Sade tasarımı ve rahat yapısıyla günlük kombinlere uygun sneaker modelidir.', true),
('00000000-0000-0000-0000-000000000538', '00000000-0000-0000-0000-000000000121', 'Nike Court Vision Günlük Ayakkabı', 'Klasik basketbol stilinden ilham alan, günlük kullanım için uygun rahat ayakkabıdır.', true),
('00000000-0000-0000-0000-000000000539', '00000000-0000-0000-0000-000000000122', 'Adidas Terrex Outdoor Bot', 'Doğa yürüyüşü ve zorlu zeminlerde kullanım için uygun, dayanıklı outdoor bottur.', true),

-- Oyun aksesuarı
('00000000-0000-0000-0000-000000000540', '00000000-0000-0000-0000-000000000103', 'Apple Uyumlu Bluetooth Oyun Kolu', 'Mobil oyunlar ve tablet kullanımı için bluetooth bağlantı destekli oyun koludur.', true)
ON CONFLICT DO NOTHING;


-- =========================================================
-- 2. ÜRÜN VARYANTLARI
-- =========================================================

INSERT INTO public.urun_varyantlari
(varyant_id, urun_id, sku, varyant_adi, ozellikler, para_birimi, liste_fiyati, satis_fiyati, kdv_orani, aktif_mi)
VALUES
-- 501 Sony kulaklık
('00000000-0000-0000-0000-000000000601', '00000000-0000-0000-0000-000000000501', 'SONY-WHCH520-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Bluetooth","pil_suresi":"50 saat"}', 'TRY', 1299.00, 999.00, 20.00, true),
('00000000-0000-0000-0000-000000000602', '00000000-0000-0000-0000-000000000501', 'SONY-WHCH520-BLU', 'Mavi', '{"renk":"Mavi","baglanti":"Bluetooth","pil_suresi":"50 saat"}', 'TRY', 1299.00, 1049.00, 20.00, true),

-- 502 Samsung Buds
('00000000-0000-0000-0000-000000000603', '00000000-0000-0000-0000-000000000502', 'SAMSUNG-BUDSFE-WHT', 'Beyaz', '{"renk":"Beyaz","baglanti":"Bluetooth","gurultu_azaltma":true}', 'TRY', 1899.00, 1499.00, 20.00, true),
('00000000-0000-0000-0000-000000000604', '00000000-0000-0000-0000-000000000502', 'SAMSUNG-BUDSFE-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Bluetooth","gurultu_azaltma":true}', 'TRY', 1899.00, 1549.00, 20.00, true),

-- 503 JBL kulaklık
('00000000-0000-0000-0000-000000000605', '00000000-0000-0000-0000-000000000503', 'JBL-T520BT-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Bluetooth","katlanabilir":true}', 'TRY', 1399.00, 1099.00, 20.00, true),
('00000000-0000-0000-0000-000000000606', '00000000-0000-0000-0000-000000000503', 'JBL-T520BT-WHT', 'Beyaz', '{"renk":"Beyaz","baglanti":"Bluetooth","katlanabilir":true}', 'TRY', 1399.00, 1129.00, 20.00, true),

-- 504 Razer kulaklık
('00000000-0000-0000-0000-000000000607', '00000000-0000-0000-0000-000000000504', 'RAZER-BSV2X-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Kablolu","mikrofon":true,"oyuncu":true}', 'TRY', 2299.00, 1799.00, 20.00, true),

-- 505 JBL hoparlör
('00000000-0000-0000-0000-000000000608', '00000000-0000-0000-0000-000000000505', 'JBL-GO3-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Bluetooth","tasınabilir":true}', 'TRY', 1299.00, 949.00, 20.00, true),

-- 506 Logitech klavye
('00000000-0000-0000-0000-000000000609', '00000000-0000-0000-0000-000000000506', 'LOGI-K380-GRY-TR', 'Gri Türkçe Q', '{"renk":"Gri","baglanti":"Bluetooth","klavye_tipi":"Türkçe Q"}', 'TRY', 1199.00, 899.00, 20.00, true),
('00000000-0000-0000-0000-000000000610', '00000000-0000-0000-0000-000000000506', 'LOGI-K380-PNK-TR', 'Pembe Türkçe Q', '{"renk":"Pembe","baglanti":"Bluetooth","klavye_tipi":"Türkçe Q"}', 'TRY', 1199.00, 929.00, 20.00, true),

-- 507 Logitech mouse
('00000000-0000-0000-0000-000000000611', '00000000-0000-0000-0000-000000000507', 'LOGI-M350-PNK', 'Pembe', '{"renk":"Pembe","baglanti":"Bluetooth","sessiz_tiklama":true}', 'TRY', 799.00, 649.00, 20.00, true),
('00000000-0000-0000-0000-000000000612', '00000000-0000-0000-0000-000000000507', 'LOGI-M350-GRY', 'Gri', '{"renk":"Gri","baglanti":"Bluetooth","sessiz_tiklama":true}', 'TRY', 799.00, 629.00, 20.00, true),

-- 508 Razer mouse
('00000000-0000-0000-0000-000000000613', '00000000-0000-0000-0000-000000000508', 'RAZER-DAE-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Kablolu","oyuncu":true,"dpi":"6400"}', 'TRY', 999.00, 799.00, 20.00, true),

-- 509 Corsair klavye
('00000000-0000-0000-0000-000000000614', '00000000-0000-0000-0000-000000000509', 'CORSAIR-K55-RGB-TR', 'RGB Türkçe Q', '{"renk":"Siyah","baglanti":"Kablolu","rgb":true,"klavye_tipi":"Türkçe Q"}', 'TRY', 2499.00, 1999.00, 20.00, true),

-- 510 Lenovo laptop
('00000000-0000-0000-0000-000000000615', '00000000-0000-0000-0000-000000000510', 'LENOVO-IP15-I5-8-512', 'Intel i5 8GB RAM 512GB SSD', '{"islemci":"Intel i5","ram":"8GB","depolama":"512GB SSD","ekran":"15.6 inç"}', 'TRY', 24999.00, 21999.00, 20.00, true),
('00000000-0000-0000-0000-000000000616', '00000000-0000-0000-0000-000000000510', 'LENOVO-IP15-I7-16-512', 'Intel i7 16GB RAM 512GB SSD', '{"islemci":"Intel i7","ram":"16GB","depolama":"512GB SSD","ekran":"15.6 inç"}', 'TRY', 31999.00, 28999.00, 20.00, true),

-- 511 Asus laptop
('00000000-0000-0000-0000-000000000617', '00000000-0000-0000-0000-000000000511', 'ASUS-TUF-A15-R7-16-RTX4050', 'Ryzen 7 16GB RTX4050', '{"islemci":"Ryzen 7","ram":"16GB","ekran_karti":"RTX4050","oyuncu":true}', 'TRY', 45999.00, 41999.00, 20.00, true),

-- 512 Dell monitor
('00000000-0000-0000-0000-000000000618', '00000000-0000-0000-0000-000000000512', 'DELL-24-FHD-75HZ', '24 inç 75Hz', '{"boyut":"24 inç","cozunurluk":"Full HD","yenileme_hizi":"75Hz"}', 'TRY', 4999.00, 3999.00, 20.00, true),

-- 513 MSI monitor
('00000000-0000-0000-0000-000000000619', '00000000-0000-0000-0000-000000000513', 'MSI-27-FHD-165HZ', '27 inç 165Hz', '{"boyut":"27 inç","cozunurluk":"Full HD","yenileme_hizi":"165Hz","oyuncu":true}', 'TRY', 8999.00, 7499.00, 20.00, true),

-- 514 SSD
('00000000-0000-0000-0000-000000000620', '00000000-0000-0000-0000-000000000514', 'KINGSTON-NV2-1TB', '1TB NVMe', '{"kapasite":"1TB","tip":"NVMe","form":"M.2"}', 'TRY', 2499.00, 1999.00, 20.00, true),

-- 515 RAM
('00000000-0000-0000-0000-000000000621', '00000000-0000-0000-0000-000000000515', 'CORSAIR-16GB-DDR4-3200', '16GB DDR4 3200MHz', '{"kapasite":"16GB","tip":"DDR4","frekans":"3200MHz"}', 'TRY', 1799.00, 1399.00, 20.00, true),

-- 516 ekran kartı
('00000000-0000-0000-0000-000000000622', '00000000-0000-0000-0000-000000000516', 'MSI-RTX4060-8GB', '8GB GDDR6', '{"chipset":"RTX4060","bellek":"8GB","oyuncu":true}', 'TRY', 15999.00, 13999.00, 20.00, true),

-- Telefonlar
('00000000-0000-0000-0000-000000000623', '00000000-0000-0000-0000-000000000517', 'APPLE-IP13-128-BLK', '128GB Siyah', '{"renk":"Siyah","depolama":"128GB","isletim_sistemi":"iOS"}', 'TRY', 36999.00, 32999.00, 20.00, true),
('00000000-0000-0000-0000-000000000624', '00000000-0000-0000-0000-000000000517', 'APPLE-IP13-256-WHT', '256GB Beyaz', '{"renk":"Beyaz","depolama":"256GB","isletim_sistemi":"iOS"}', 'TRY', 41999.00, 37999.00, 20.00, true),
('00000000-0000-0000-0000-000000000625', '00000000-0000-0000-0000-000000000518', 'SAMSUNG-A55-128-BLK', '128GB Siyah', '{"renk":"Siyah","depolama":"128GB","isletim_sistemi":"Android"}', 'TRY', 21999.00, 18999.00, 20.00, true),
('00000000-0000-0000-0000-000000000626', '00000000-0000-0000-0000-000000000519', 'XIAOMI-RN13-256-BLU', '256GB Mavi', '{"renk":"Mavi","depolama":"256GB","isletim_sistemi":"Android"}', 'TRY', 14999.00, 11999.00, 20.00, true),

-- Şarj / powerbank / kablo
('00000000-0000-0000-0000-000000000627', '00000000-0000-0000-0000-000000000520', 'ANKER-20W-USBC-WHT', '20W Beyaz', '{"renk":"Beyaz","guc":"20W","baglanti":"USB-C","hizli_sarj":true}', 'TRY', 799.00, 599.00, 20.00, true),
('00000000-0000-0000-0000-000000000628', '00000000-0000-0000-0000-000000000521', 'XIAOMI-PB-20000-BLK', '20000 mAh Siyah', '{"renk":"Siyah","kapasite":"20000 mAh","hizli_sarj":true}', 'TRY', 1499.00, 1199.00, 20.00, true),
('00000000-0000-0000-0000-000000000629', '00000000-0000-0000-0000-000000000522', 'ANKER-CABLE-LTG-1M', '1 metre', '{"uzunluk":"1m","baglanti":"USB-C to Lightning","hizli_sarj":true}', 'TRY', 599.00, 449.00, 20.00, true),

-- Saat / bileklik
('00000000-0000-0000-0000-000000000630', '00000000-0000-0000-0000-000000000523', 'APPLE-WATCHSE2-40-BLK', '40mm Gece Yarısı', '{"kasa":"40mm","renk":"Gece Yarısı","gps":true}', 'TRY', 10999.00, 9999.00, 20.00, true),
('00000000-0000-0000-0000-000000000631', '00000000-0000-0000-0000-000000000523', 'APPLE-WATCHSE2-44-BLK', '44mm Gece Yarısı', '{"kasa":"44mm","renk":"Gece Yarısı","gps":true}', 'TRY', 12499.00, 11499.00, 20.00, true),
('00000000-0000-0000-0000-000000000632', '00000000-0000-0000-0000-000000000524', 'HUAWEI-WATCHFIT3-GRN', 'Yeşil', '{"renk":"Yeşil","pil_suresi":"10 gün","spor_modu":true}', 'TRY', 5999.00, 4999.00, 20.00, true),
('00000000-0000-0000-0000-000000000633', '00000000-0000-0000-0000-000000000525', 'XIAOMI-BAND8-BLK', 'Siyah', '{"renk":"Siyah","pil_suresi":"16 gün","spor_modu":true}', 'TRY', 1499.00, 1199.00, 20.00, true),

-- Ev ürünleri
('00000000-0000-0000-0000-000000000634', '00000000-0000-0000-0000-000000000526', 'ARZUM-OKKA-MINIO-BLK', 'Siyah', '{"renk":"Siyah","kapasite":"4 fincan","tasmasiz_pisirme":true}', 'TRY', 1799.00, 1399.00, 20.00, true),
('00000000-0000-0000-0000-000000000635', '00000000-0000-0000-0000-000000000527', 'PHILIPS-IRON-3000-BLU', 'Mavi', '{"renk":"Mavi","buharli":true,"guc":"2400W"}', 'TRY', 1999.00, 1599.00, 20.00, true),
('00000000-0000-0000-0000-000000000636', '00000000-0000-0000-0000-000000000528', 'DYSON-V8-SILVER', 'Gümüş', '{"renk":"Gümüş","kablosuz":true,"calisma_suresi":"40 dakika"}', 'TRY', 15999.00, 13999.00, 20.00, true),
('00000000-0000-0000-0000-000000000637', '00000000-0000-0000-0000-000000000529', 'PHILIPS-AIR-800-WHT', 'Beyaz', '{"renk":"Beyaz","filtre":"HEPA","oda_kapasitesi":"49 m2"}', 'TRY', 6999.00, 5999.00, 20.00, true),

-- Giyim varyantları
('00000000-0000-0000-0000-000000000638', '00000000-0000-0000-0000-000000000530', 'LCW-TSHIRT-BLK-M', 'Siyah M', '{"renk":"Siyah","beden":"M","kumas":"Pamuk"}', 'TRY', 299.00, 199.00, 20.00, true),
('00000000-0000-0000-0000-000000000639', '00000000-0000-0000-0000-000000000530', 'LCW-TSHIRT-WHT-L', 'Beyaz L', '{"renk":"Beyaz","beden":"L","kumas":"Pamuk"}', 'TRY', 299.00, 199.00, 20.00, true),
('00000000-0000-0000-0000-000000000640', '00000000-0000-0000-0000-000000000531', 'MAVI-MARCUS-32-32', 'Mavi 32/32', '{"renk":"Mavi","beden":"32/32","kumas":"Denim"}', 'TRY', 1499.00, 1199.00, 20.00, true),
('00000000-0000-0000-0000-000000000641', '00000000-0000-0000-0000-000000000532', 'DEFACTO-SWT-GRY-M', 'Gri M', '{"renk":"Gri","beden":"M","kapuson":true}', 'TRY', 899.00, 699.00, 20.00, true),
('00000000-0000-0000-0000-000000000642', '00000000-0000-0000-0000-000000000533', 'LCW-MONT-BLK-L', 'Siyah L', '{"renk":"Siyah","beden":"L","kapuson":true,"mevsim":"Kış"}', 'TRY', 2499.00, 1999.00, 20.00, true),
('00000000-0000-0000-0000-000000000643', '00000000-0000-0000-0000-000000000534', 'DEFACTO-GOMLEK-WHT-M', 'Beyaz M', '{"renk":"Beyaz","beden":"M","kumas":"Pamuk"}', 'TRY', 799.00, 599.00, 20.00, true),

-- Ayakkabı varyantları
('00000000-0000-0000-0000-000000000644', '00000000-0000-0000-0000-000000000535', 'NIKE-REV7-BLK-42', 'Siyah 42', '{"renk":"Siyah","numara":"42","tip":"Koşu"}', 'TRY', 2999.00, 2499.00, 20.00, true),
('00000000-0000-0000-0000-000000000645', '00000000-0000-0000-0000-000000000535', 'NIKE-REV7-WHT-43', 'Beyaz 43', '{"renk":"Beyaz","numara":"43","tip":"Koşu"}', 'TRY', 2999.00, 2499.00, 20.00, true),
('00000000-0000-0000-0000-000000000646', '00000000-0000-0000-0000-000000000536', 'ADIDAS-RUNFALCON-BLK-42', 'Siyah 42', '{"renk":"Siyah","numara":"42","tip":"Spor"}', 'TRY', 2799.00, 2199.00, 20.00, true),
('00000000-0000-0000-0000-000000000647', '00000000-0000-0000-0000-000000000537', 'PUMA-SMASH-WHT-41', 'Beyaz 41', '{"renk":"Beyaz","numara":"41","tip":"Günlük"}', 'TRY', 2499.00, 1899.00, 20.00, true),
('00000000-0000-0000-0000-000000000648', '00000000-0000-0000-0000-000000000538', 'NIKE-COURT-BLK-42', 'Siyah 42', '{"renk":"Siyah","numara":"42","tip":"Günlük"}', 'TRY', 3299.00, 2699.00, 20.00, true),
('00000000-0000-0000-0000-000000000649', '00000000-0000-0000-0000-000000000539', 'ADIDAS-TERREX-BRN-43', 'Kahverengi 43', '{"renk":"Kahverengi","numara":"43","tip":"Outdoor Bot"}', 'TRY', 4999.00, 3999.00, 20.00, true),

-- Oyun kolu
('00000000-0000-0000-0000-000000000650', '00000000-0000-0000-0000-000000000540', 'BT-GAMEPAD-IOS-BLK', 'Siyah', '{"renk":"Siyah","baglanti":"Bluetooth","uyumluluk":"iOS Android"}', 'TRY', 1299.00, 999.00, 20.00, true),

-- Ek varyantlar
('00000000-0000-0000-0000-000000000651', '00000000-0000-0000-0000-000000000526', 'ARZUM-OKKA-MINIO-RED', 'Kırmızı', '{"renk":"Kırmızı","kapasite":"4 fincan","tasmasiz_pisirme":true}', 'TRY', 1799.00, 1449.00, 20.00, true),
('00000000-0000-0000-0000-000000000652', '00000000-0000-0000-0000-000000000508', 'RAZER-DAE-WHT', 'Beyaz', '{"renk":"Beyaz","baglanti":"Kablolu","oyuncu":true,"dpi":"6400"}', 'TRY', 999.00, 849.00, 20.00, true),
('00000000-0000-0000-0000-000000000653', '00000000-0000-0000-0000-000000000516', 'MSI-RTX4060TI-8GB', 'RTX 4060 Ti 8GB', '{"chipset":"RTX4060Ti","bellek":"8GB","oyuncu":true}', 'TRY', 20999.00, 18999.00, 20.00, true),
('00000000-0000-0000-0000-000000000654', '00000000-0000-0000-0000-000000000514', 'KINGSTON-NV2-500GB', '500GB NVMe', '{"kapasite":"500GB","tip":"NVMe","form":"M.2"}', 'TRY', 1599.00, 1199.00, 20.00, true),
('00000000-0000-0000-0000-000000000655', '00000000-0000-0000-0000-000000000515', 'CORSAIR-32GB-DDR4-3200', '32GB DDR4 3200MHz', '{"kapasite":"32GB","tip":"DDR4","frekans":"3200MHz"}', 'TRY', 3499.00, 2999.00, 20.00, true),
('00000000-0000-0000-0000-000000000656', '00000000-0000-0000-0000-000000000513', 'MSI-27-QHD-170HZ', '27 inç QHD 170Hz', '{"boyut":"27 inç","cozunurluk":"QHD","yenileme_hizi":"170Hz","oyuncu":true}', 'TRY', 12999.00, 10999.00, 20.00, true),
('00000000-0000-0000-0000-000000000657', '00000000-0000-0000-0000-000000000521', 'XIAOMI-PB-10000-BLK', '10000 mAh Siyah', '{"renk":"Siyah","kapasite":"10000 mAh","hizli_sarj":true}', 'TRY', 999.00, 799.00, 20.00, true),
('00000000-0000-0000-0000-000000000658', '00000000-0000-0000-0000-000000000532', 'DEFACTO-SWT-BLK-L', 'Siyah L', '{"renk":"Siyah","beden":"L","kapuson":true}', 'TRY', 899.00, 729.00, 20.00, true),
('00000000-0000-0000-0000-000000000659', '00000000-0000-0000-0000-000000000531', 'MAVI-MARCUS-34-32', 'Mavi 34/32', '{"renk":"Mavi","beden":"34/32","kumas":"Denim"}', 'TRY', 1499.00, 1249.00, 20.00, true),
('00000000-0000-0000-0000-000000000660', '00000000-0000-0000-0000-000000000536', 'ADIDAS-RUNFALCON-WHT-41', 'Beyaz 41', '{"renk":"Beyaz","numara":"41","tip":"Spor"}', 'TRY', 2799.00, 2199.00, 20.00, true)
ON CONFLICT (sku) DO NOTHING;


-- =========================================================
-- 3. STOK
-- =========================================================

INSERT INTO public.stok
(varyant_id, elde_adet, rezerve_adet)
VALUES
('00000000-0000-0000-0000-000000000601', 32, 3),
('00000000-0000-0000-0000-000000000602', 14, 2),
('00000000-0000-0000-0000-000000000603', 18, 2),
('00000000-0000-0000-0000-000000000604', 0, 0),
('00000000-0000-0000-0000-000000000605', 24, 4),
('00000000-0000-0000-0000-000000000606', 12, 1),
('00000000-0000-0000-0000-000000000607', 9, 1),
('00000000-0000-0000-0000-000000000608', 35, 5),
('00000000-0000-0000-0000-000000000609', 45, 5),
('00000000-0000-0000-0000-000000000610', 20, 2),
('00000000-0000-0000-0000-000000000611', 0, 0),
('00000000-0000-0000-0000-000000000612', 27, 3),
('00000000-0000-0000-0000-000000000613', 16, 2),
('00000000-0000-0000-0000-000000000614', 11, 1),
('00000000-0000-0000-0000-000000000615', 6, 1),
('00000000-0000-0000-0000-000000000616', 4, 1),
('00000000-0000-0000-0000-000000000617', 3, 1),
('00000000-0000-0000-0000-000000000618', 22, 2),
('00000000-0000-0000-0000-000000000619', 8, 1),
('00000000-0000-0000-0000-000000000620', 40, 6),
('00000000-0000-0000-0000-000000000621', 38, 4),
('00000000-0000-0000-0000-000000000622', 5, 1),
('00000000-0000-0000-0000-000000000623', 7, 1),
('00000000-0000-0000-0000-000000000624', 3, 0),
('00000000-0000-0000-0000-000000000625', 13, 2),
('00000000-0000-0000-0000-000000000626', 21, 3),
('00000000-0000-0000-0000-000000000627', 60, 7),
('00000000-0000-0000-0000-000000000628', 34, 4),
('00000000-0000-0000-0000-000000000629', 50, 5),
('00000000-0000-0000-0000-000000000630', 8, 1),
('00000000-0000-0000-0000-000000000631', 5, 1),
('00000000-0000-0000-0000-000000000632', 17, 2),
('00000000-0000-0000-0000-000000000633', 28, 4),
('00000000-0000-0000-0000-000000000634', 21, 4),
('00000000-0000-0000-0000-000000000635', 19, 3),
('00000000-0000-0000-0000-000000000636', 4, 0),
('00000000-0000-0000-0000-000000000637', 10, 1),
('00000000-0000-0000-0000-000000000638', 80, 10),
('00000000-0000-0000-0000-000000000639', 75, 8),
('00000000-0000-0000-0000-000000000640', 30, 4),
('00000000-0000-0000-0000-000000000641', 41, 5),
('00000000-0000-0000-0000-000000000642', 14, 2),
('00000000-0000-0000-0000-000000000643', 26, 3),
('00000000-0000-0000-0000-000000000644', 16, 2),
('00000000-0000-0000-0000-000000000645', 12, 1),
('00000000-0000-0000-0000-000000000646', 20, 3),
('00000000-0000-0000-0000-000000000647', 18, 2),
('00000000-0000-0000-0000-000000000648', 9, 1),
('00000000-0000-0000-0000-000000000649', 6, 1),
('00000000-0000-0000-0000-000000000650', 15, 2),
('00000000-0000-0000-0000-000000000651', 11, 1),
('00000000-0000-0000-0000-000000000652', 7, 1),
('00000000-0000-0000-0000-000000000653', 3, 0),
('00000000-0000-0000-0000-000000000654', 44, 5),
('00000000-0000-0000-0000-000000000655', 15, 2),
('00000000-0000-0000-0000-000000000656', 6, 1),
('00000000-0000-0000-0000-000000000657', 37, 4),
('00000000-0000-0000-0000-000000000658', 24, 2),
('00000000-0000-0000-0000-000000000659', 17, 2),
('00000000-0000-0000-0000-000000000660', 13, 1)
ON CONFLICT (varyant_id)
DO UPDATE SET
    elde_adet = EXCLUDED.elde_adet,
    rezerve_adet = EXCLUDED.rezerve_adet,
    guncelleme_tarihi = now();


-- =========================================================
-- 4. ÜRÜN - KATEGORİ EŞLEŞMELERİ
-- =========================================================

INSERT INTO public.urun_kategorileri
(urun_id, kategori_id)
VALUES
('00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000211'),
('00000000-0000-0000-0000-000000000502', '00000000-0000-0000-0000-000000000211'),
('00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000211'),
('00000000-0000-0000-0000-000000000504', '00000000-0000-0000-0000-000000000261'),
('00000000-0000-0000-0000-000000000505', '00000000-0000-0000-0000-000000000212'),

('00000000-0000-0000-0000-000000000506', '00000000-0000-0000-0000-000000000222'),
('00000000-0000-0000-0000-000000000507', '00000000-0000-0000-0000-000000000223'),
('00000000-0000-0000-0000-000000000508', '00000000-0000-0000-0000-000000000263'),
('00000000-0000-0000-0000-000000000509', '00000000-0000-0000-0000-000000000262'),
('00000000-0000-0000-0000-000000000510', '00000000-0000-0000-0000-000000000221'),
('00000000-0000-0000-0000-000000000511', '00000000-0000-0000-0000-000000000221'),
('00000000-0000-0000-0000-000000000512', '00000000-0000-0000-0000-000000000224'),
('00000000-0000-0000-0000-000000000513', '00000000-0000-0000-0000-000000000224'),
('00000000-0000-0000-0000-000000000514', '00000000-0000-0000-0000-000000000225'),
('00000000-0000-0000-0000-000000000515', '00000000-0000-0000-0000-000000000226'),
('00000000-0000-0000-0000-000000000516', '00000000-0000-0000-0000-000000000227'),

('00000000-0000-0000-0000-000000000517', '00000000-0000-0000-0000-000000000241'),
('00000000-0000-0000-0000-000000000518', '00000000-0000-0000-0000-000000000241'),
('00000000-0000-0000-0000-000000000519', '00000000-0000-0000-0000-000000000241'),
('00000000-0000-0000-0000-000000000520', '00000000-0000-0000-0000-000000000242'),
('00000000-0000-0000-0000-000000000521', '00000000-0000-0000-0000-000000000243'),
('00000000-0000-0000-0000-000000000522', '00000000-0000-0000-0000-000000000245'),

('00000000-0000-0000-0000-000000000523', '00000000-0000-0000-0000-000000000251'),
('00000000-0000-0000-0000-000000000524', '00000000-0000-0000-0000-000000000251'),
('00000000-0000-0000-0000-000000000525', '00000000-0000-0000-0000-000000000252'),

('00000000-0000-0000-0000-000000000526', '00000000-0000-0000-0000-000000000231'),
('00000000-0000-0000-0000-000000000527', '00000000-0000-0000-0000-000000000233'),
('00000000-0000-0000-0000-000000000528', '00000000-0000-0000-0000-000000000232'),
('00000000-0000-0000-0000-000000000529', '00000000-0000-0000-0000-000000000234'),

('00000000-0000-0000-0000-000000000530', '00000000-0000-0000-0000-000000000271'),
('00000000-0000-0000-0000-000000000531', '00000000-0000-0000-0000-000000000273'),
('00000000-0000-0000-0000-000000000532', '00000000-0000-0000-0000-000000000274'),
('00000000-0000-0000-0000-000000000533', '00000000-0000-0000-0000-000000000275'),
('00000000-0000-0000-0000-000000000534', '00000000-0000-0000-0000-000000000272'),

('00000000-0000-0000-0000-000000000535', '00000000-0000-0000-0000-000000000283'),
('00000000-0000-0000-0000-000000000536', '00000000-0000-0000-0000-000000000281'),
('00000000-0000-0000-0000-000000000537', '00000000-0000-0000-0000-000000000282'),
('00000000-0000-0000-0000-000000000538', '00000000-0000-0000-0000-000000000282'),
('00000000-0000-0000-0000-000000000539', '00000000-0000-0000-0000-000000000284'),

('00000000-0000-0000-0000-000000000540', '00000000-0000-0000-0000-000000000264')
ON CONFLICT DO NOTHING;


-- =========================================================
-- 5. ÜRÜN RESİMLERİ
-- =========================================================

INSERT INTO public.urun_resimleri
(resim_id, urun_id, url, sira_no)
SELECT
    gen_random_uuid(),
    u.urun_id,
    'https://example.com/images/' || u.urun_id::text || '.jpg',
    1
FROM public.urunler u
WHERE u.urun_id BETWEEN '00000000-0000-0000-0000-000000000501'
                    AND '00000000-0000-0000-0000-000000000540'
AND NOT EXISTS (
    SELECT 1
    FROM public.urun_resimleri r
    WHERE r.urun_id = u.urun_id
);

COMMIT;