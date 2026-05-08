BEGIN;

-- =========================================================
-- 05_seed_yorumlar_iadeler_kuponlar.sql
-- E-Ticaret LLM Asistanı - Kupon, İade ve Yorum Seed Verileri
-- =========================================================
-- Bu dosya kampanya/indirim, iade ve ürün yorumları için
-- gerçekçi sentetik veri oluşturur.
-- =========================================================


-- =========================================================
-- 1. KUPONLAR
-- =========================================================

INSERT INTO public.kuponlar
(kupon_id, kod, indirim_turu, deger, para_birimi, baslangic_tarihi, bitis_tarihi,
 min_siparis_tutari, kullanim_limiti, kullanilan_adet, aktif_mi)
VALUES
('00000000-0000-0000-0000-000000001201', 'HOSGELDIN100', 'tutar', 100.00, 'TRY', now() - interval '60 days', now() + interval '60 days', 500.00, 500, 34, true),
('00000000-0000-0000-0000-000000001202', 'TEKNO10', 'yuzde', 10.00, 'TRY', now() - interval '30 days', now() + interval '30 days', 1000.00, 300, 75, true),
('00000000-0000-0000-0000-000000001203', 'KARGO0', 'tutar', 49.90, 'TRY', now() - interval '20 days', now() + interval '40 days', 750.00, 1000, 210, true),
('00000000-0000-0000-0000-000000001204', 'OYUNCU500', 'tutar', 500.00, 'TRY', now() - interval '15 days', now() + interval '20 days', 10000.00, 100, 18, true),
('00000000-0000-0000-0000-000000001205', 'GIYIM15', 'yuzde', 15.00, 'TRY', now() - interval '10 days', now() + interval '25 days', 600.00, 250, 41, true),
('00000000-0000-0000-0000-000000001206', 'AYAKKABI150', 'tutar', 150.00, 'TRY', now() - interval '10 days', now() + interval '25 days', 1500.00, 200, 29, true),
('00000000-0000-0000-0000-000000001207', 'EVYASAM10', 'yuzde', 10.00, 'TRY', now() - interval '5 days', now() + interval '35 days', 1000.00, 150, 12, true),
('00000000-0000-0000-0000-000000001208', 'MOBIL250', 'tutar', 250.00, 'TRY', now() - interval '5 days', now() + interval '35 days', 5000.00, 120, 23, true),
('00000000-0000-0000-0000-000000001209', 'BITENKUPON', 'yuzde', 20.00, 'TRY', now() - interval '90 days', now() - interval '10 days', 1000.00, 50, 50, false),
('00000000-0000-0000-0000-000000001210', 'YAZILIMCI300', 'tutar', 300.00, 'TRY', now() - interval '3 days', now() + interval '45 days', 7000.00, 100, 7, true)
ON CONFLICT (kod) DO NOTHING;


-- =========================================================
-- 2. SİPARİŞ İNDİRİMLERİ
-- =========================================================

INSERT INTO public.siparis_indirimleri
(siparis_id, kupon_id, kupon_kodu_anlik, indirim_turu, indirim_deger)
VALUES
('00000000-0000-0000-0000-000000000801', '00000000-0000-0000-0000-000000001201', 'HOSGELDIN100', 'tutar', 100.00),
('00000000-0000-0000-0000-000000000803', '00000000-0000-0000-0000-000000001204', 'OYUNCU500', 'tutar', 500.00),
('00000000-0000-0000-0000-000000000804', '00000000-0000-0000-0000-000000001206', 'AYAKKABI150', 'tutar', 150.00),
('00000000-0000-0000-0000-000000000807', '00000000-0000-0000-0000-000000001208', 'MOBIL250', 'tutar', 250.00)
ON CONFLICT (siparis_id) DO NOTHING;


-- =========================================================
-- 3. İADELER
-- =========================================================

INSERT INTO public.iadeler
(iade_id, siparis_id, musteri_id, neden, durum, olusturma_tarihi)
VALUES
('00000000-0000-0000-0000-000000001301',
 '00000000-0000-0000-0000-000000000808',
 '00000000-0000-0000-0000-000000000308',
 'Ayakkabının numarası küçük geldiği için müşteri iade talebi oluşturdu.',
 'tamamlandi',
 now() - interval '4 days'),

('00000000-0000-0000-0000-000000001302',
 '00000000-0000-0000-0000-000000000810',
 '00000000-0000-0000-0000-000000000310',
 'Gaming monitörün kutusu hasarlı geldiği ve panelde çizik olduğu için iade talep edildi.',
 'tamamlandi',
 now() - interval '2 days'),

('00000000-0000-0000-0000-000000001303',
 '00000000-0000-0000-0000-000000000802',
 '00000000-0000-0000-0000-000000000302',
 'Kablo yanlış model seçildiği için değişim/iade talebi açıldı.',
 'talep_edildi',
 now() - interval '1 days')
ON CONFLICT (iade_id) DO NOTHING;


-- =========================================================
-- 4. İADE ÖĞELERİ
-- =========================================================

INSERT INTO public.iade_ogeleri
(iade_oge_id, iade_id, siparis_oge_id, adet)
VALUES
('00000000-0000-0000-0000-000000001401',
 '00000000-0000-0000-0000-000000001301',
 '00000000-0000-0000-0000-000000000915',
 1),

('00000000-0000-0000-0000-000000001402',
 '00000000-0000-0000-0000-000000001302',
 '00000000-0000-0000-0000-000000000917',
 1),

('00000000-0000-0000-0000-000000001403',
 '00000000-0000-0000-0000-000000001303',
 '00000000-0000-0000-0000-000000000904',
 1)
ON CONFLICT (iade_oge_id) DO NOTHING;


-- =========================================================
-- 5. ÜRÜN YORUMLARI
-- =========================================================

INSERT INTO public.urun_yorumlari
(yorum_id, urun_id, musteri_id, puan, baslik, icerik, olusturma_tarihi)
VALUES
-- Kulaklık / ses ürünleri
('00000000-0000-0000-0000-000000001501', '00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000301', 5, 'Bataryası çok iyi', 'Sony kulaklığın şarjı uzun gidiyor. Günlük kullanım ve online ders için oldukça yeterli.', now() - interval '15 days'),
('00000000-0000-0000-0000-000000001502', '00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000311', 4, 'Fiyatına göre başarılı', 'Ses kalitesi fiyatına göre iyi. Hafif olduğu için uzun süre takınca rahatsız etmiyor.', now() - interval '9 days'),
('00000000-0000-0000-0000-000000001503', '00000000-0000-0000-0000-000000000502', '00000000-0000-0000-0000-000000000302', 5, 'ANC başarılı', 'Samsung Buds FE gürültü azaltma konusunda beklentimi karşıladı. Toplu taşımada iyi çalışıyor.', now() - interval '12 days'),
('00000000-0000-0000-0000-000000001504', '00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000312', 4, 'Basları güçlü', 'JBL kulaklık müzik için güzel. Bas sevenler için uygun ama uzun kullanımda biraz sıkabilir.', now() - interval '8 days'),
('00000000-0000-0000-0000-000000001505', '00000000-0000-0000-0000-000000000504', '00000000-0000-0000-0000-000000000310', 5, 'Oyun için ideal', 'Mikrofonu net, oyunlarda ayak seslerini rahat duyuyorum. Fiyat performans oyuncu kulaklığı.', now() - interval '6 days'),
('00000000-0000-0000-0000-000000001506', '00000000-0000-0000-0000-000000000505', '00000000-0000-0000-0000-000000000313', 4, 'Küçük ama güçlü', 'JBL Go 3 boyutuna göre yüksek ses veriyor. Dışarıda kullanmak için pratik.', now() - interval '7 days'),

-- Klavye / mouse / oyuncu ekipmanı
('00000000-0000-0000-0000-000000001507', '00000000-0000-0000-0000-000000000506', '00000000-0000-0000-0000-000000000303', 5, 'Çok sessiz klavye', 'Logitech K380 kompakt ve sessiz. Tablet ve laptop arasında hızlı geçiş yapması güzel.', now() - interval '10 days'),
('00000000-0000-0000-0000-000000001508', '00000000-0000-0000-0000-000000000507', '00000000-0000-0000-0000-000000000314', 3, 'Sessiz ama küçük', 'Mouse sessiz çalışıyor fakat eli büyük olanlar için biraz küçük kalabilir.', now() - interval '11 days'),
('00000000-0000-0000-0000-000000001509', '00000000-0000-0000-0000-000000000508', '00000000-0000-0000-0000-000000000310', 4, 'Gaming için iyi', 'Razer mouse hassasiyeti iyi. FPS oyunlarında rahat kontrol sağlıyor.', now() - interval '5 days'),
('00000000-0000-0000-0000-000000001510', '00000000-0000-0000-0000-000000000509', '00000000-0000-0000-0000-000000000315', 4, 'RGB güzel', 'Corsair klavyenin ışıklandırması iyi, tuş hissi de fiyatına göre başarılı.', now() - interval '4 days'),

-- Laptop / monitör / bilgisayar parçası
('00000000-0000-0000-0000-000000001511', '00000000-0000-0000-0000-000000000510', '00000000-0000-0000-0000-000000000303', 4, 'Ders ve yazılım için yeterli', 'Lenovo laptop günlük kullanım, ders ve temel yazılım geliştirme için yeterli performans veriyor.', now() - interval '9 days'),
('00000000-0000-0000-0000-000000001512', '00000000-0000-0000-0000-000000000511', '00000000-0000-0000-0000-000000000316', 5, 'Oyun performansı iyi', 'Asus TUF A15 oyunlarda başarılı. Fan sesi var ama performansı güçlü.', now() - interval '7 days'),
('00000000-0000-0000-0000-000000001513', '00000000-0000-0000-0000-000000000512', '00000000-0000-0000-0000-000000000317', 4, 'Ofis için ideal', 'Dell monitör görüntü kalitesiyle ofis ve ders kullanımı için iyi.', now() - interval '6 days'),
('00000000-0000-0000-0000-000000001514', '00000000-0000-0000-0000-000000000513', '00000000-0000-0000-0000-000000000310', 2, 'Kutu hasarlı geldi', 'Monitör performans olarak iyi olabilir ama kutu hasarlı geldi ve panelde çizik vardı.', now() - interval '2 days'),
('00000000-0000-0000-0000-000000001515', '00000000-0000-0000-0000-000000000514', '00000000-0000-0000-0000-000000000318', 5, 'Bilgisayarı hızlandırdı', 'Kingston NVMe SSD eski bilgisayarımı ciddi şekilde hızlandırdı. Açılış süresi kısaldı.', now() - interval '5 days'),
('00000000-0000-0000-0000-000000001516', '00000000-0000-0000-0000-000000000515', '00000000-0000-0000-0000-000000000306', 5, 'Stabil çalışıyor', 'Corsair RAM sorunsuz çalıştı. Oyun ve çoklu görevlerde fark etti.', now() - interval '6 days'),
('00000000-0000-0000-0000-000000001517', '00000000-0000-0000-0000-000000000516', '00000000-0000-0000-0000-000000000306', 5, '1080p oyun için güçlü', 'RTX 4060 ekran kartı 1080p oyunlarda yüksek ayarlarda akıcı performans veriyor.', now() - interval '6 days'),

-- Telefon / aksesuar
('00000000-0000-0000-0000-000000001518', '00000000-0000-0000-0000-000000000517', '00000000-0000-0000-0000-000000000319', 5, 'Kamera güzel', 'iPhone 13 kamerası ve yazılım desteğiyle hâlâ çok iyi bir telefon.', now() - interval '5 days'),
('00000000-0000-0000-0000-000000001519', '00000000-0000-0000-0000-000000000518', '00000000-0000-0000-0000-000000000307', 4, 'Batarya iyi', 'Samsung A55 batarya ve ekran konusunda başarılı. Günlük kullanım için yeterli.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001520', '00000000-0000-0000-0000-000000000519', '00000000-0000-0000-0000-000000000320', 4, 'Fiyat performans telefon', 'Redmi Note 13 fiyatına göre iyi ekran ve batarya sunuyor.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001521', '00000000-0000-0000-0000-000000000520', '00000000-0000-0000-0000-000000000301', 5, 'Hızlı şarj ediyor', 'Anker adaptör iPhone ve Android cihazlarda hızlı şarj için başarılı.', now() - interval '15 days'),
('00000000-0000-0000-0000-000000001522', '00000000-0000-0000-0000-000000000521', '00000000-0000-0000-0000-000000000307', 4, 'Kapasitesi yüksek', 'Xiaomi powerbank telefonumu birkaç kez şarj ediyor. Biraz ağır ama kullanışlı.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001523', '00000000-0000-0000-0000-000000000522', '00000000-0000-0000-0000-000000000302', 3, 'Yanlış model aldım', 'Kablo kaliteli ama kendi cihazıma uygun modeli seçmediğim için iade talebi açtım.', now() - interval '1 days'),

-- Saat / bileklik
('00000000-0000-0000-0000-000000001524', '00000000-0000-0000-0000-000000000523', '00000000-0000-0000-0000-000000000309', 5, 'Aktivite takibi başarılı', 'Apple Watch spor ve bildirim takibinde çok pratik. iPhone ile uyumu çok iyi.', now() - interval '3 days'),
('00000000-0000-0000-0000-000000001525', '00000000-0000-0000-0000-000000000524', '00000000-0000-0000-0000-000000000321', 4, 'Pil ömrü iyi', 'Huawei Watch Fit 3 hafif ve pil ömrü iyi. Spor modları yeterli.', now() - interval '2 days'),
('00000000-0000-0000-0000-000000001526', '00000000-0000-0000-0000-000000000525', '00000000-0000-0000-0000-000000000322', 4, 'Uygun fiyatlı bileklik', 'Xiaomi Smart Band 8 adım ve uyku takibi için fiyatına göre başarılı.', now() - interval '3 days'),

-- Ev ve yaşam
('00000000-0000-0000-0000-000000001527', '00000000-0000-0000-0000-000000000526', '00000000-0000-0000-0000-000000000305', 5, 'Kahveyi güzel yapıyor', 'Arzum Okka Minio taşırmadan kahve yapıyor. Kullanımı çok kolay.', now() - interval '8 days'),
('00000000-0000-0000-0000-000000001528', '00000000-0000-0000-0000-000000000527', '00000000-0000-0000-0000-000000000323', 4, 'Buharı güçlü', 'Philips ütü günlük kullanımda hızlı ısınıyor ve kırışıklıkları iyi açıyor.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001529', '00000000-0000-0000-0000-000000000528', '00000000-0000-0000-0000-000000000324', 5, 'Temizlikte pratik', 'Dyson kablosuz süpürge özellikle küçük evlerde çok pratik. Çekim gücü iyi.', now() - interval '3 days'),
('00000000-0000-0000-0000-000000001530', '00000000-0000-0000-0000-000000000529', '00000000-0000-0000-0000-000000000325', 4, 'Alerji için iyi', 'Hava temizleyici odadaki tozu ve kokuyu azaltıyor. Özellikle alerjim olduğu için faydasını gördüm.', now() - interval '2 days'),

-- Giyim
('00000000-0000-0000-0000-000000001531', '00000000-0000-0000-0000-000000000530', '00000000-0000-0000-0000-000000000304', 4, 'Basic tişört güzel', 'Kumaşı yumuşak ve günlük kullanım için ideal. Fiyatı da uygun.', now() - interval '8 days'),
('00000000-0000-0000-0000-000000001532', '00000000-0000-0000-0000-000000000531', '00000000-0000-0000-0000-000000000326', 5, 'Kalıbı iyi', 'Mavi jean kalıp olarak rahat. Kumaşı dayanıklı hissettiriyor.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001533', '00000000-0000-0000-0000-000000000532', '00000000-0000-0000-0000-000000000308', 4, 'Rahat sweatshirt', 'Gri sweatshirt rahat ve sıcak tutuyor. Günlük kullanım için iyi.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001534', '00000000-0000-0000-0000-000000000533', '00000000-0000-0000-0000-000000000327', 4, 'Kış için yeterli', 'Mont soğuk havalarda sıcak tutuyor. Fermuar kalitesi biraz daha iyi olabilirdi.', now() - interval '3 days'),
('00000000-0000-0000-0000-000000001535', '00000000-0000-0000-0000-000000000534', '00000000-0000-0000-0000-000000000328', 4, 'Ofis için uygun', 'Gömlek kumaşı güzel, ofis ve günlük kullanım için rahat.', now() - interval '3 days'),

-- Ayakkabı
('00000000-0000-0000-0000-000000001536', '00000000-0000-0000-0000-000000000535', '00000000-0000-0000-0000-000000000304', 5, 'Yürüyüşte rahat', 'Nike Revolution 7 hafif ve rahat. Günlük yürüyüş için çok iyi.', now() - interval '8 days'),
('00000000-0000-0000-0000-000000001537', '00000000-0000-0000-0000-000000000536', '00000000-0000-0000-0000-000000000329', 4, 'Spor için ideal', 'Adidas Runfalcon hafif spor ve günlük kullanım için rahat.', now() - interval '3 days'),
('00000000-0000-0000-0000-000000001538', '00000000-0000-0000-0000-000000000537', '00000000-0000-0000-0000-000000000308', 2, 'Numarası küçük geldi', 'Ayakkabının kalitesi iyi ama kalıbı dar geldiği için iade ettim.', now() - interval '4 days'),
('00000000-0000-0000-0000-000000001539', '00000000-0000-0000-0000-000000000538', '00000000-0000-0000-0000-000000000330', 4, 'Günlük kullanım için güzel', 'Nike Court Vision klasik tasarımıyla günlük kombinlere uyuyor.', now() - interval '2 days'),
('00000000-0000-0000-0000-000000001540', '00000000-0000-0000-0000-000000000539', '00000000-0000-0000-0000-000000000313', 5, 'Outdoor için sağlam', 'Adidas Terrex bot doğa yürüyüşünde kayma yapmadı, tabanı sağlam.', now() - interval '2 days')
ON CONFLICT (urun_id, musteri_id) DO NOTHING;


COMMIT;