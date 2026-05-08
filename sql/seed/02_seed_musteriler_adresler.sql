BEGIN;

-- =========================================================
-- 02_seed_musteriler_adresler.sql
-- E-Ticaret LLM Asistanı - Müşteri ve Adres Seed Verileri
-- =========================================================
-- Bu dosya musteriler ve musteri_adresleri tablolarını
-- gerçekçi sentetik verilerle doldurur.
-- Hedef: 30 müşteri + 30 varsayılan adres
-- =========================================================


-- =========================================================
-- 1. MÜŞTERİLER
-- =========================================================

INSERT INTO public.musteriler
(musteri_id, eposta, telefon, ad, soyad, aktif_mi)
VALUES
('00000000-0000-0000-0000-000000000301', 'murat.guner@example.com', '05550000001', 'Murat', 'Güner', true),
('00000000-0000-0000-0000-000000000302', 'ayse.yilmaz@example.com', '05550000002', 'Ayşe', 'Yılmaz', true),
('00000000-0000-0000-0000-000000000303', 'mehmet.kaya@example.com', '05550000003', 'Mehmet', 'Kaya', true),
('00000000-0000-0000-0000-000000000304', 'zeynep.demir@example.com', '05550000004', 'Zeynep', 'Demir', true),
('00000000-0000-0000-0000-000000000305', 'emre.sahin@example.com', '05550000005', 'Emre', 'Şahin', true),
('00000000-0000-0000-0000-000000000306', 'elif.arslan@example.com', '05550000006', 'Elif', 'Arslan', true),
('00000000-0000-0000-0000-000000000307', 'burak.celik@example.com', '05550000007', 'Burak', 'Çelik', true),
('00000000-0000-0000-0000-000000000308', 'deniz.ozkan@example.com', '05550000008', 'Deniz', 'Özkan', true),
('00000000-0000-0000-0000-000000000309', 'selin.koc@example.com', '05550000009', 'Selin', 'Koç', true),
('00000000-0000-0000-0000-000000000310', 'can.aydin@example.com', '05550000010', 'Can', 'Aydın', true),
('00000000-0000-0000-0000-000000000311', 'ece.kurt@example.com', '05550000011', 'Ece', 'Kurt', true),
('00000000-0000-0000-0000-000000000312', 'kerem.yildiz@example.com', '05550000012', 'Kerem', 'Yıldız', true),
('00000000-0000-0000-0000-000000000313', 'naz.ozdemir@example.com', '05550000013', 'Naz', 'Özdemir', true),
('00000000-0000-0000-0000-000000000314', 'kaan.akar@example.com', '05550000014', 'Kaan', 'Akar', true),
('00000000-0000-0000-0000-000000000315', 'melis.tas@example.com', '05550000015', 'Melis', 'Taş', true),
('00000000-0000-0000-0000-000000000316', 'ali.demirtas@example.com', '05550000016', 'Ali', 'Demirtaş', true),
('00000000-0000-0000-0000-000000000317', 'dilara.ates@example.com', '05550000017', 'Dilara', 'Ateş', true),
('00000000-0000-0000-0000-000000000318', 'oguzhan.kilic@example.com', '05550000018', 'Oğuzhan', 'Kılıç', true),
('00000000-0000-0000-0000-000000000319', 'sude.ekinci@example.com', '05550000019', 'Sude', 'Ekinci', true),
('00000000-0000-0000-0000-000000000320', 'furkan.oz@example.com', '05550000020', 'Furkan', 'Öz', true),
('00000000-0000-0000-0000-000000000321', 'irem.gunes@example.com', '05550000021', 'İrem', 'Güneş', true),
('00000000-0000-0000-0000-000000000322', 'berk.dogan@example.com', '05550000022', 'Berk', 'Doğan', true),
('00000000-0000-0000-0000-000000000323', 'yasemin.aksoy@example.com', '05550000023', 'Yasemin', 'Aksoy', true),
('00000000-0000-0000-0000-000000000324', 'arda.erdem@example.com', '05550000024', 'Arda', 'Erdem', true),
('00000000-0000-0000-0000-000000000325', 'buse.kaplan@example.com', '05550000025', 'Buse', 'Kaplan', true),
('00000000-0000-0000-0000-000000000326', 'cemre.polat@example.com', '05550000026', 'Cemre', 'Polat', true),
('00000000-0000-0000-0000-000000000327', 'tolga.sari@example.com', '05550000027', 'Tolga', 'Sarı', true),
('00000000-0000-0000-0000-000000000328', 'gamze.unal@example.com', '05550000028', 'Gamze', 'Ünal', true),
('00000000-0000-0000-0000-000000000329', 'onur.yavuz@example.com', '05550000029', 'Onur', 'Yavuz', true),
('00000000-0000-0000-0000-000000000330', 'eda.karaca@example.com', '05550000030', 'Eda', 'Karaca', true)
ON CONFLICT (eposta) DO NOTHING;


-- =========================================================
-- 2. MÜŞTERİ ADRESLERİ
-- =========================================================

INSERT INTO public.musteri_adresleri
(adres_id, musteri_id, etiket, ad_soyad, telefon, ulke, il, ilce, mahalle, adres_satiri, posta_kodu, varsayilan_mi)
VALUES
('00000000-0000-0000-0000-000000000401', '00000000-0000-0000-0000-000000000301', 'Ev', 'Murat Güner', '05550000001', 'TR', 'Samsun', 'Atakum', 'Mimar Sinan', 'Deneme Sokak No: 12 Daire: 4', '55200', true),
('00000000-0000-0000-0000-000000000402', '00000000-0000-0000-0000-000000000302', 'Ev', 'Ayşe Yılmaz', '05550000002', 'TR', 'Ankara', 'Çankaya', 'Bahçelievler', 'Örnek Caddesi No: 8 Daire: 10', '06490', true),
('00000000-0000-0000-0000-000000000403', '00000000-0000-0000-0000-000000000303', 'İş', 'Mehmet Kaya', '05550000003', 'TR', 'İstanbul', 'Kadıköy', 'Moda', 'Teknoloji Sokak No: 5 Kat: 2', '34710', true),
('00000000-0000-0000-0000-000000000404', '00000000-0000-0000-0000-000000000304', 'Ev', 'Zeynep Demir', '05550000004', 'TR', 'İzmir', 'Bornova', 'Kazımdirik', 'Kampüs Yolu No: 3 Daire: 7', '35040', true),
('00000000-0000-0000-0000-000000000405', '00000000-0000-0000-0000-000000000305', 'Ev', 'Emre Şahin', '05550000005', 'TR', 'Bursa', 'Nilüfer', 'Görükle', 'Gençlik Caddesi No: 21', '16285', true),
('00000000-0000-0000-0000-000000000406', '00000000-0000-0000-0000-000000000306', 'Ev', 'Elif Arslan', '05550000006', 'TR', 'Antalya', 'Muratpaşa', 'Fener', 'Liman Caddesi No: 14', '07160', true),
('00000000-0000-0000-0000-000000000407', '00000000-0000-0000-0000-000000000307', 'İş', 'Burak Çelik', '05550000007', 'TR', 'İstanbul', 'Şişli', 'Mecidiyeköy', 'Ofis Plaza No: 18 Kat: 6', '34387', true),
('00000000-0000-0000-0000-000000000408', '00000000-0000-0000-0000-000000000308', 'Ev', 'Deniz Özkan', '05550000008', 'TR', 'Eskişehir', 'Tepebaşı', 'Hoşnudiye', 'Üniversite Caddesi No: 9', '26130', true),
('00000000-0000-0000-0000-000000000409', '00000000-0000-0000-0000-000000000309', 'Ev', 'Selin Koç', '05550000009', 'TR', 'Konya', 'Selçuklu', 'Bosna Hersek', 'Alışveriş Sokak No: 4', '42250', true),
('00000000-0000-0000-0000-000000000410', '00000000-0000-0000-0000-000000000310', 'Ev', 'Can Aydın', '05550000010', 'TR', 'Kocaeli', 'İzmit', 'Yahya Kaptan', 'Park Caddesi No: 11', '41050', true),

('00000000-0000-0000-0000-000000000411', '00000000-0000-0000-0000-000000000311', 'Ev', 'Ece Kurt', '05550000011', 'TR', 'Adana', 'Seyhan', 'Reşatbey', 'Atatürk Caddesi No: 19', '01120', true),
('00000000-0000-0000-0000-000000000412', '00000000-0000-0000-0000-000000000312', 'İş', 'Kerem Yıldız', '05550000012', 'TR', 'Kayseri', 'Melikgazi', 'Hunat', 'Sanayi Caddesi No: 31', '38030', true),
('00000000-0000-0000-0000-000000000413', '00000000-0000-0000-0000-000000000313', 'Ev', 'Naz Özdemir', '05550000013', 'TR', 'Trabzon', 'Ortahisar', 'Pelitli', 'Sahil Yolu No: 6', '61010', true),
('00000000-0000-0000-0000-000000000414', '00000000-0000-0000-0000-000000000314', 'Ev', 'Kaan Akar', '05550000014', 'TR', 'Gaziantep', 'Şahinbey', 'Karataş', 'Kültür Caddesi No: 25', '27470', true),
('00000000-0000-0000-0000-000000000415', '00000000-0000-0000-0000-000000000315', 'Ev', 'Melis Taş', '05550000015', 'TR', 'Muğla', 'Menteşe', 'Kötekli', 'Öğrenci Sokak No: 17', '48000', true),
('00000000-0000-0000-0000-000000000416', '00000000-0000-0000-0000-000000000316', 'Ev', 'Ali Demirtaş', '05550000016', 'TR', 'İstanbul', 'Üsküdar', 'Altunizade', 'Çamlıca Caddesi No: 44', '34662', true),
('00000000-0000-0000-0000-000000000417', '00000000-0000-0000-0000-000000000317', 'Ev', 'Dilara Ateş', '05550000017', 'TR', 'Ankara', 'Keçiören', 'Etlik', 'Sağlık Sokak No: 13', '06010', true),
('00000000-0000-0000-0000-000000000418', '00000000-0000-0000-0000-000000000318', 'İş', 'Oğuzhan Kılıç', '05550000018', 'TR', 'İzmir', 'Konak', 'Alsancak', 'Liman İş Merkezi No: 22', '35220', true),
('00000000-0000-0000-0000-000000000419', '00000000-0000-0000-0000-000000000319', 'Ev', 'Sude Ekinci', '05550000019', 'TR', 'Sakarya', 'Serdivan', 'Kemalpaşa', 'Çark Caddesi No: 7', '54050', true),
('00000000-0000-0000-0000-000000000420', '00000000-0000-0000-0000-000000000320', 'Ev', 'Furkan Öz', '05550000020', 'TR', 'Mersin', 'Yenişehir', 'Pozcu', 'Deniz Caddesi No: 16', '33140', true),

('00000000-0000-0000-0000-000000000421', '00000000-0000-0000-0000-000000000321', 'Ev', 'İrem Güneş', '05550000021', 'TR', 'Balıkesir', 'Altıeylül', 'Bahçelievler', 'Yıldız Sokak No: 2', '10100', true),
('00000000-0000-0000-0000-000000000422', '00000000-0000-0000-0000-000000000322', 'İş', 'Berk Doğan', '05550000022', 'TR', 'İstanbul', 'Beşiktaş', 'Levent', 'Büyükdere Caddesi No: 101 Kat: 8', '34330', true),
('00000000-0000-0000-0000-000000000423', '00000000-0000-0000-0000-000000000323', 'Ev', 'Yasemin Aksoy', '05550000023', 'TR', 'Diyarbakır', 'Kayapınar', 'Peyas', 'Diclekent Bulvarı No: 18', '21070', true),
('00000000-0000-0000-0000-000000000424', '00000000-0000-0000-0000-000000000324', 'Ev', 'Arda Erdem', '05550000024', 'TR', 'Tekirdağ', 'Süleymanpaşa', 'Değirmenaltı', 'Sahil Sokak No: 5', '59030', true),
('00000000-0000-0000-0000-000000000425', '00000000-0000-0000-0000-000000000325', 'Ev', 'Buse Kaplan', '05550000025', 'TR', 'Aydın', 'Efeler', 'Mimar Sinan', 'Zeybek Caddesi No: 6', '09100', true),
('00000000-0000-0000-0000-000000000426', '00000000-0000-0000-0000-000000000326', 'Ev', 'Cemre Polat', '05550000026', 'TR', 'Manisa', 'Yunusemre', 'Uncubozköy', 'Lale Sokak No: 12', '45030', true),
('00000000-0000-0000-0000-000000000427', '00000000-0000-0000-0000-000000000327', 'İş', 'Tolga Sarı', '05550000027', 'TR', 'Bursa', 'Osmangazi', 'Heykel', 'Cumhuriyet Caddesi No: 41', '16010', true),
('00000000-0000-0000-0000-000000000428', '00000000-0000-0000-0000-000000000328', 'Ev', 'Gamze Ünal', '05550000028', 'TR', 'Erzurum', 'Yakutiye', 'Lalapaşa', 'Palandöken Yolu No: 9', '25100', true),
('00000000-0000-0000-0000-000000000429', '00000000-0000-0000-0000-000000000329', 'Ev', 'Onur Yavuz', '05550000029', 'TR', 'Malatya', 'Battalgazi', 'Fırat', 'Kayısı Sokak No: 20', '44100', true),
('00000000-0000-0000-0000-000000000430', '00000000-0000-0000-0000-000000000330', 'Ev', 'Eda Karaca', '05550000030', 'TR', 'Çanakkale', 'Merkez', 'Barbaros', 'Troya Caddesi No: 3', '17100', true)
ON CONFLICT (adres_id) DO NOTHING;


COMMIT;