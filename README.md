# e-ticaret-LLM-asistani

PostgreSQL tabanlı bir e-ticaret veritabanı üzerinde Türkçe doğal dil sorguları ile semantik arama yapılmasını sağlayan okul projesi/prototip seviyesinde bir LLM asistanı çalışmasıdır.

Bu proje gerçek bir üretim sistemi değildir. Amaç; veritabanı tasarımı, pgvector ile semantik arama, SentenceTransformer tabanlı embedding üretimi, kural tabanlı sorgu analizi, fine-tuning ve CLI/Streamlit üzerinden demo akışını akademik bir proje kapsamında göstermektir.

Not: Bu proje ChatGPT benzeri generative bir LLM eğitmez. Hazır bir SentenceTransformer embedding modeli, e-ticaret veritabanından üretilen query-positive_text çiftleriyle semantic retrieval amacı için özelleştirilir.

## 1. Proje Başlığı

**e-ticaret-LLM-asistani**

PostgreSQL, pgvector ve SentenceTransformer kullanılarak geliştirilen Türkçe doğal dil destekli e-ticaret semantik arama ve LLM asistanı prototipi.

## 2. Proje Amacı

Projenin temel amacı, kullanıcının Türkçe doğal dil ile yazdığı e-ticaret sorgularını analiz ederek PostgreSQL veritabanındaki ilgili kayıtları bulmak ve okunabilir bir cevap üretmektir.

Örnek sorgular:

```text
1000 TL altı stokta olan kablosuz kulaklık öner
iphone 15 mavi
32 beden mavi pantolon
kötü yorumlar
10000 40000 TL arası en pahalı iphone
```

Sistem bu sorgulardan intent, kategori, marka, model, fiyat aralığı, stok durumu, ürün özellikleri, puan filtresi ve sıralama niyeti gibi bilgileri çıkarmaya çalışır. Ardından sorgu embedding'i üretilir, `semantic_index` tablosunda pgvector ile benzer kayıtlar aranır ve sonuçlar kullanıcıya sade bir cevap olarak gösterilir.

## 3. Genel Mimari

```text
Kullanıcı Sorgusu
       |
       v
Query Parser
       |
       v
Filtreler ve Arama Metni
       |
       v
SentenceTransformer Embedding
       |
       v
PostgreSQL + pgvector
       |
       v
Metadata Filtreleri ve Sıralama
       |
       v
Answer Generator
       |
       v
CLI veya Streamlit Demo
```

Mimari, semantik benzerlik aramasını metadata filtreleriyle birlikte kullanır. Böylece örneğin `iphone 15 mavi` sorgusunda hem embedding benzerliği hem de kategori, marka, model ve renk filtreleri birlikte değerlendirilir.

## 4. Kullanılan Teknolojiler

- Python
- PostgreSQL
- pgvector
- psycopg
- SentenceTransformers
- Hugging Face Transformers
- PyTorch
- YAML config dosyaları
- JSONL training dataset
- CLI tabanlı demo app
- Streamlit tabanlı görsel demo app

## 5. Veritabanı Yapısı

Proje, e-ticaret alanına uygun ilişkisel bir PostgreSQL veritabanı üzerinde çalışır.

Ana tablolar:

- `musteriler`
- `musteri_adresleri`
- `markalar`
- `kategoriler`
- `kuponlar`
- `urunler`
- `urun_varyantlari`
- `stok`
- `urun_resimleri`
- `urun_kategorileri`
- `sepetler`
- `sepet_ogeleri`
- `siparisler`
- `siparis_ogeleri`
- `siparis_indirimleri`
- `odemeler`
- `kargolar`
- `iadeler`
- `iade_ogeleri`
- `urun_yorumlari`

Başlangıç veri durumu:

| Veri türü | Kayıt sayısı |
| --- | ---: |
| Müşteri | 30 |
| Adres | 30 |
| Marka | 26 |
| Kategori | 43 |
| Ürün | 40 |
| Ürün varyantı | 60 |
| Stok kaydı | 60 |
| Sipariş | 10 |
| Sipariş öğesi | 18 |
| Ödeme | 10 |
| Kargo | 10 |
| Kupon | 10 |
| İade | 3 |
| İade öğesi | 3 |
| Ürün yorumu | 40 |
| Semantic kayıt | 232 |
| Query-positive training pair | 1538 |

Ek seed dosyalarıyla demo verisi genişletilebilir. Özellikle `sql/seed/06_extra_products_and_variants.sql` ürün ve varyant çeşitliliğini artırır, `sql/seed/08_extra_product_reviews.sql` ise aktif ürünlerin tamamı için dengeli yorum verisi üretir. Bu dosyalar çalıştırıldıktan sonra kayıt sayıları yerel veritabanı durumuna göre artar.

Önemli SQL dosyaları:

```text
sql/01_schema.sql
sql/02_semantic_index.sql
sql/03_embedding_views.sql
sql/seed/01_seed_markalar_kategoriler.sql
sql/seed/02_seed_musteriler_adresler.sql
sql/seed/03_seed_urunler.sql
sql/seed/04_seed_siparisler.sql
sql/seed/05_seed_yorumlar_iadeler_kuponlar.sql
sql/seed/06_extra_products_and_variants.sql
sql/seed/07_fix_sku_ascii.sql
sql/seed/08_extra_product_reviews.sql
```

## 6. Semantic Search Akışı

Semantic search süreci şu adımlarla çalışır:

1. Kullanıcı sorgusu CLI veya Streamlit arayüzünden alınır.
2. `src/search/query_parser.py` sorgudan intent ve filtre bilgilerini çıkarmaya çalışır.
3. `src/embedding/model_loader.py` fine-tuned model varsa onu, yoksa base modeli yükler.
4. `src/search/semantic_search.py` sorgu embedding'i üretir.
5. PostgreSQL `semantic_index` tablosunda pgvector cosine distance ile yakın kayıtlar aranır.
6. Metadata filtreleri uygulanır.
7. Fiyat veya puan sıralama niyeti varsa sonuçlar buna göre sıralanır.
8. `src/app/answer_generator.py` sonuçları okunabilir cevaba dönüştürür.
9. `src/app/chat_cli.py` veya `ui/streamlit_app.py` kullanıcıya demo deneyimi sunar.

`semantic_index` kayıtları `sql/03_embedding_views.sql` içindeki view'lar üzerinden üretilir. Ürün varyantı kayıtlarında metadata içinde marka, kategori, stok, fiyat, SKU, ürün özellikleri ve temiz ürün açıklaması gibi alanlar tutulur.

Arama tarafında bazı tekil tanımlayıcılar exact metadata filtrelerine çevrilir:

- `SIP-2026-0007` gibi sipariş numaraları ilgili bağlama göre `siparisler`, `kargolar` veya `iadeler` kayıtlarında `siparis_no` filtresiyle aranır.
- `AR000002` gibi takip numaraları `kargolar.metadata.takip_no` üzerinden filtrelenir.
- `KARGO0` gibi kupon kodları `kuponlar.metadata.kod` üzerinden filtrelenir.

Strict ürün/attribute filtreleri hiç sonuç döndürmezse fallback search devreye girebilir. Fallback davranışı `config/search.yaml` içindeki ayarlarla yönetilir ve exact identifier sorgularında tekil filtreler gevşetilmez.

## 7. Query Parser Mantığı

Query parser kural tabanlı çalışır. Amaç, doğal dil sorgusundan arama motorunun kullanabileceği yapısal filtreleri çıkarmaktır.

Parser artık büyük sözlüklerini `config/query_parser.yaml` dosyasından okur. Intent, kategori, marka alias, renk, status ve sort keywordleri config-driven hale getirilmiştir. Model yakalama örüntüleri ve bazı regex tabanlı parse kuralları ise okunabilirlik ve kontrol için Python tarafında kalır.

Çıkarılan başlıca alanlar:

- `intent`: product, review, cargo, return, order, coupon, customer
- `source_tables`: aranacak semantic kaynak tabloları
- `category`: ürün kategorisi
- `brand`: marka
- `model_filter`: ürün/model ifadesi
- `attribute_filters`: renk, beden, numara, depolama, RAM, bağlantı, kapasite gibi özellikler
- `min_price`, `max_price`: fiyat aralığı
- `in_stock_only`, `out_of_stock_only`: stok durumu
- `min_rating`, `max_rating`, `rating_equals`: yorum puanı filtreleri
- `sort_by`, `sort_direction`: fiyat veya puan sıralaması
- `status`: kargo, iade veya sipariş durumu
- `order_no`, `tracking_no`, `coupon_code`: sipariş no, takip no ve kupon kodu gibi tekil tanımlayıcılar

Örnek parser çıktıları:

| Sorgu | Beklenen çıkarım |
| --- | --- |
| `1000 TL altı stokta olan kablosuz kulaklık öner` | `intent=product`, `max_price=1000`, `in_stock_only=True`, `category=Kulaklık`, `baglanti=Bluetooth` |
| `iphone 15 mavi` | `intent=product`, `brand=apple`, `category=Telefon`, `model_filter=iPhone 15`, `renk=Mavi` |
| `poco x6 pro 512 gb` | `intent=product`, `brand=poco`, `category=Telefon`, `model_filter=Poco X6 Pro`, `depolama=512GB` |
| `32 beden mavi pantolon` | `intent=product`, `category=Pantolon`, `beden=32`, `renk=Mavi` |
| `42 numara ayakkabı` | `intent=product`, `category=Ayakkabı`, `numara=42` |
| `teslim edilen kargoları listele` | `intent=cargo`, `status=teslim_edildi` |
| `yüksek puanlı ayakkabı yorumları` | `intent=review`, `category=Ayakkabı`, `min_rating=4`, `sort_by=rating`, `sort_direction=desc` |
| `kötü yorumlar` | `intent=review`, `max_rating=2`, `sort_by=rating`, `sort_direction=asc` |
| `1 yıldız yorumlar` | `intent=review`, `rating_equals=1` |
| `10000 40000 TL arası en pahalı iphone` | `intent=product`, `brand=apple`, `category=Telefon`, `min_price=10000`, `max_price=40000`, `sort_by=price`, `sort_direction=desc` |
| `SIP-2026-0002 kargo durumu` | `intent=cargo`, `order_no=SIP-2026-0002`, `source_tables=kargolar` |
| `AR000002 takip numaralı kargo` | `intent=cargo`, `tracking_no=AR000002`, `source_tables=kargolar` |
| `KARGO0 kuponu` | `intent=coupon`, `coupon_code=KARGO0`, `source_tables=kuponlar` |

Kategori filtreleri üst kategori/alt kategori uyumlu çalışacak şekilde genişletilmiştir. Örneğin `Ayakkabı` sorgusu `Spor Ayakkabı`, `Günlük Ayakkabı`, `Koşu Ayakkabısı` ve `Bot` gibi alt kategorileri de kapsayabilir.

## 8. Tokenization ve Fine-Tuning Açıklaması

Base model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Fine-tuned model çıktı dizini:

```text
models/ecommerce-semantic-model
```

`models/ecommerce-semantic-model` klasörü `.gitignore` içindedir. Model dosyaları GitHub'a gönderilmez; ihtiyaç olduğunda yeniden eğitim komutu ile oluşturulur.

Embedding dimension:

```text
384
```

Loss:

```text
MultipleNegativesRankingLoss
```

`src/embedding/tokenizer_demo.py` tokenization sürecini göstermek için hazırlanmıştır. Bu demo token, token id, vocabulary, attention mask, padding ve truncation kavramlarını terminalde gösterir:

```bash
python -m src.embedding.tokenizer_demo
```

Kısa kavram açıklamaları:

- Tokenization: Metni modelin işleyebileceği küçük parçalara ayırır.
- Vocabulary: Token -> id eşleşmelerini tutan sözlüktür.
- Token ID: Token'ın sözlükteki sayısal karşılığıdır.
- Attention mask: `1` gerçek token, `0` padding token anlamına gelir.
- Padding: Kısa metni sabit `max_length` değerine tamamlar.
- Truncation: Uzun metni `max_length` değerine göre keser.

Bu kavramlar Streamlit arayüzündeki `Tokenizer` sekmesinde de uygulamalı olarak gösterilir. Padding tokenları varsayılan olarak gizlidir; checkbox ile görünür hale getirilebilir.

Fine-tuning aşamasında `data/train_pairs.jsonl` dosyasındaki query-positive pair kayıtları okunur ve SentenceTransformer modeli `MultipleNegativesRankingLoss` ile eğitilir. Validation ve test dosyaları model karşılaştırması/evaluation için saklanır.

## 9. Kurulum

Python sanal ortamı oluşturulur ve bağımlılıklar yüklenir:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

PostgreSQL ve pgvector eklentisinin sistemde hazır olduğu varsayılır.

## 10. Config Dosyaları

Projede hard coding yapılmaması hedeflenmiştir. Veritabanı bağlantısı, model adı, fine-tuned model yolu, embedding dimension, tokenizer ayarları, training ayarları ve search ayarları YAML dosyaları ile yönetilir.

Ana config dosyaları:

```text
config/database.yaml
config/model.yaml
config/search.yaml
config/query_parser.yaml
config/demo_queries.yaml
```

- `config/database.yaml`: Veritabanı bağlantısı, SQL dosya yolları ve semantic index tablo adı.
- `config/model.yaml`: Base model adı, fine-tuned model yolu, embedding boyutu, tokenizer, dataset split, training ve evaluation parametreleri.
- `config/search.yaml`: Arama limitleri, similarity ayarları ve fallback search davranışı.
- `config/query_parser.yaml`: Intent, kategori, marka, renk, status ve sort keyword sözlükleri.
- `config/demo_queries.yaml`: Streamlit GUI'deki Search ve Tokenizer randomizer örnekleri.

`config/demo_queries.yaml` dosyasındaki örnekler GUI'de hazır sorgu havuzu olarak kullanılır. Search sayfasındaki randomizer sadece arama kutusunu doldurur; arama başlatmak için ayrıca `Ara` butonuna basılır. Tokenizer sayfasındaki randomizer sadece text area alanını doldurur; analiz için ayrıca `Tokenize Et` butonuna basılır.

## 11. Veritabanını Hazırlama

Şema ve temel seed verileri:

```bash
psql -U postgres -d ders -f sql/01_schema.sql
psql -U postgres -d ders -f sql/02_semantic_index.sql
psql -U postgres -d ders -f sql/seed/01_seed_markalar_kategoriler.sql
psql -U postgres -d ders -f sql/seed/02_seed_musteriler_adresler.sql
psql -U postgres -d ders -f sql/seed/03_seed_urunler.sql
psql -U postgres -d ders -f sql/seed/04_seed_siparisler.sql
psql -U postgres -d ders -f sql/seed/05_seed_yorumlar_iadeler_kuponlar.sql
psql -U postgres -d ders -f sql/03_embedding_views.sql
```

Genişletilmiş demo verisi için ek seed dosyaları:

```bash
psql -U postgres -d ders -f sql/seed/06_extra_products_and_variants.sql
psql -U postgres -d ders -f sql/seed/07_fix_sku_ascii.sql
psql -U postgres -d ders -f sql/seed/08_extra_product_reviews.sql
```

Ek seed dosyalarının amacı:

- `06_extra_products_and_variants.sql`: Tişört, sweatshirt, gömlek, pantolon, mont, ayakkabı, telefon, laptop ve kulaklık kategorilerinde daha gerçekçi ürün/varyant çeşitliliği ekler.
- `07_fix_sku_ascii.sql`: SKU değerlerinde Türkçe karakter kalmaması için güvenli düzeltme yapar.
- `08_extra_product_reviews.sql`: Aktif ürünlerin tamamı için 5, 4, 3, 2 ve 1 puan dağılımını içeren gerçekçi yorumlar ekler.

Veritabanı bağlantı bilgileri `config/database.yaml` dosyasından güncellenebilir.

## 12. Semantic Index Oluşturma

SQL view'ları hazırlandıktan sonra semantic kayıtlar için embedding oluşturulur:

```bash
python -m src.embedding.semantic_index_builder
```

Model yükleme davranışını kontrol etmek için:

```bash
python -m src.embedding.model_loader
```

`src/embedding/model_loader.py` içinde model cache kullanılır. Embedding modeli ilk çağrıda yüklenir; aynı Python process'i içinde sonraki çağrılarda tekrar yüklenmez. Bu davranış özellikle Streamlit GUI ve split evaluation sırasında performansı artırır.

Yeni seed dosyaları çalıştırıldıktan sonra semantic index'in tekrar oluşturulması gerekir. Aksi halde yeni ürün, varyant veya yorumlar arama sonuçlarına yansımaz.

## 13. Training Dataset Üretme

Veritabanındaki semantic kayıtları query-positive pair formatına dönüştürmek için:

```bash
python -m src.training.dataset_builder
```

Oluşan çıktı:

```text
data/training_pairs.jsonl
```

Bu dosya tüm ham query-positive_text çiftlerini içerir. Fine-tuning için ayrıca train/validation/test ayrımı yapılır:

```bash
python -m src.training.split_training_dataset
```

Oluşan split dosyaları:

| Dosya | Açıklama | Son bilinen kayıt sayısı |
| --- | --- | ---: |
| `data/training_pairs.jsonl` | Tüm dataset | 16071 |
| `data/train_pairs.jsonl` | Eğitim seti | 12866 |
| `data/val_pairs.jsonl` | Validation set | 1582 |
| `data/test_pairs.jsonl` | Test seti | 1623 |

Split işlemi group-based yapılır. Aynı `source_table + source_id` değerinden gelen örnekler train, validation ve test setleri arasında karışmayacak şekilde ayrılır. Bu yaklaşım, aynı semantic kayıttan gelen benzer query'lerin farklı splitlere düşmesini engelleyerek veri sızıntısını azaltır.

## 14. Fine-Tuning Yapma

SentenceTransformer modelini proje verisiyle fine-tune etmek için:

```bash
python -m src.training.train_sentence_transformer
```

Fine-tuning yalnızca `data/train_pairs.jsonl` üzerinden yapılır. `data/val_pairs.jsonl` ve `data/test_pairs.jsonl` dosyaları retrieval evaluation için ayrılmıştır.

Eğitim sonunda model aşağıdaki dizine kaydedilir:

```text
models/ecommerce-semantic-model
```

Bu dizin `.gitignore` içindedir. Model dosyaları repository'ye dahil edilmez.

## 15. Evaluation Çalıştırma

Manuel retrieval başarısını test sorguları ile ölçmek için:

```bash
python -m src.evaluation.evaluate_retrieval
```

Manuel evaluator metadata koşullarını dikkate alan kontrollü test sorgularını çalıştırır. Bunun yanında split dosyaları üzerinden otomatik retrieval evaluation için ayrı bir modül vardır:

```bash
python -m src.evaluation.evaluate_split_retrieval --split validation --evaluation-mode exact_id --limit 5
python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode exact_id --limit 5
python -m src.evaluation.evaluate_split_retrieval --split validation --evaluation-mode metadata --limit 5
python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode metadata --limit 5
```

Split evaluation iki modda çalışır:

- `exact_id`: Belirli bir kaydı hedefleyen sorgularda `source_table + source_id` doğru geldi mi ölçer. Örnek: `SIP-2026-0007 numaralı sipariş`.
- `metadata`: Kategori, marka, fiyat, stok, puan, renk, beden, RAM, depolama gibi koşulların sağlanıp sağlanmadığını ölçer. Generic veya attribute sorgular için daha uygundur.

Son bilinen split evaluation sonuçları:

| Split | Mode | Top-1 Accuracy | Top-5 Accuracy | MRR |
| --- | --- | ---: | ---: | ---: |
| Validation | exact_id | 0.8827 | 0.9441 | 0.9089 |
| Test | exact_id | 0.9167 | 1.0000 | 0.9568 |
| Validation | metadata | 0.9933 | 0.9933 | 0.9933 |
| Test | metadata | 0.9913 | 0.9913 | 0.9913 |

Evaluation sonuçları `reports/evaluation/` altında JSON ve CSV olarak üretilebilir. `evaluation_summary.csv` özet metrikleri içerir. Streamlit arayüzündeki `Model Report` sekmesi bu rapor dosyalarını okuyarak exact-id, metadata ve source table bazlı başarıları gösterir.

Retrieval ve evaluation akışının kısa teknik özeti için ayrıca `docs/retrieval_evaluation_notes.md` dosyası bulunur.

## 16. CLI ve Streamlit Demo Kullanımı

Terminal tabanlı demo:

```bash
python -m src.app.chat_cli
```

Semantic search test/demo modülü:

```bash
python -m src.search.semantic_search
```

Streamlit tabanlı görsel demo:

```bash
python -m streamlit run ui/streamlit_app.py
```

Alternatif:

```bash
streamlit run ui/streamlit_app.py
```

Streamlit arayüzü Windows XP nostaljik temasında üç ana sekmeden oluşur:

- `Search`: Doğal dil sorgusu, sorgu analizi, kaynak sonuçlar, teknik detaylar ve config-driven `Demo Queries` randomizer.
- `Tokenizer`: Metin girme, `Rastgele Metin Getir`, `Tokenize Et`, token tablosu, token id, attention mask ve padding göster/gizle kontrolü.
- `Model Report`: Exact-id validation/test sonuçları, metadata validation/test sonuçları, source table bazlı başarı ve CSV summary.

Rover GIF durumu arama öncesi, arama sırasında, sonuç bulunduğunda ve sonuç bulunamadığında farklı görsellerle gösterilir.

## 17. Örnek Sorgular

Genel ürün sorguları:

```text
1000 TL altı stokta olan kablosuz kulaklık öner
s beden siyah tişört
l beden lacivert tişört
bordo sweatshirt
haki mont
42 numara ayakkabı
32 beden mavi pantolon
32/32 mavi pantolon
```

Telefon ve laptop sorguları:

```text
iphone 15 mavi
samsung s23 gri
redmi note 13 pro
poco x6 pro 512 gb
macbook air m2 8 gb
hp victus 16 oyuncu laptop
32 gb ram oyuncu laptop
```

Fiyat ve sıralama sorguları:

```text
10000 40000 TL arası iphone
40000 TL altı iphone
10000 TL üstü telefon
pahalı telefon
en ucuz laptop
10000 40000 TL arası en pahalı iphone
```

Yorum, kargo ve iade sorguları:

```text
yüksek puanlı ayakkabı yorumları
düşük puanlı iphone yorumları
kötü yorumlar
1 yıldız yorumlar
samsung s23 yorumları
teslim edilen kargoları listele
hasarlı gelen ürün iadelerini göster
```

Modülleri tek tek denemek için:

```bash
python -m src.database.db
python -m src.embedding.model_loader
python -m src.embedding.tokenizer_demo
python -m src.embedding.semantic_index_builder
python -m src.search.query_parser
python -m src.search.semantic_search
python -m src.training.dataset_builder
python -m src.training.split_training_dataset
python -m src.training.train_sentence_transformer
python -m src.evaluation.evaluate_retrieval
python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode exact_id --limit 5
python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode metadata --limit 5
python -m src.app.chat_cli
python -m streamlit run ui/streamlit_app.py
```

Önerilen çalışma sırası:

1. Veritabanı şema ve seed SQL dosyalarını hazırla.
2. Semantic index/view yapılarını oluştur.
3. Dataset üret: `python -m src.training.dataset_builder`
4. Dataset split çalıştır: `python -m src.training.split_training_dataset`
5. Fine-tuning yap: `python -m src.training.train_sentence_transformer`
6. Semantic index embeddinglerini güncelle: `python -m src.embedding.semantic_index_builder`
7. Retrieval evaluation çalıştır: `python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode exact_id --limit 5`
8. Metadata evaluation çalıştır: `python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode metadata --limit 5`
9. GUI'yi aç: `streamlit run ui/streamlit_app.py`

## 18. Proje Klasör Yapısı

```text
.
├── config/
│   ├── database.yaml
│   ├── demo_queries.yaml
│   ├── model.yaml
│   ├── query_parser.yaml
│   └── search.yaml
├── data/
│   ├── training_pairs.jsonl
│   ├── train_pairs.jsonl
│   ├── val_pairs.jsonl
│   └── test_pairs.jsonl
├── docs/
│   └── retrieval_evaluation_notes.md
├── models/
│   └── ecommerce-semantic-model/        # Git'e dahil edilmez
├── reports/
│   └── evaluation/
│       ├── evaluation_summary.csv
│       ├── validation_exact_id_summary.json
│       ├── validation_metadata_summary.json
│       ├── test_exact_id_summary.json
│       └── test_metadata_summary.json
├── sql/
│   ├── 01_schema.sql
│   ├── 02_semantic_index.sql
│   ├── 03_embedding_views.sql
│   └── seed/
│       ├── 01_seed_markalar_kategoriler.sql
│       ├── 02_seed_musteriler_adresler.sql
│       ├── 03_seed_urunler.sql
│       ├── 04_seed_siparisler.sql
│       ├── 05_seed_yorumlar_iadeler_kuponlar.sql
│       ├── 06_extra_products_and_variants.sql
│       ├── 07_fix_sku_ascii.sql
│       └── 08_extra_product_reviews.sql
├── src/
│   ├── app/
│   │   ├── answer_generator.py
│   │   └── chat_cli.py
│   ├── database/
│   │   └── db.py
│   ├── embedding/
│   │   ├── model_loader.py
│   │   ├── semantic_index_builder.py
│   │   └── tokenizer_demo.py
│   ├── evaluation/
│   │   ├── evaluate_retrieval.py
│   │   └── evaluate_split_retrieval.py
│   ├── search/
│   │   ├── query_parser.py
│   │   └── semantic_search.py
│   ├── training/
│   │   ├── dataset_builder.py
│   │   ├── split_training_dataset.py
│   │   ├── tokenizer_demo.py
│   │   └── train_sentence_transformer.py
│   └── config_loader.py
├── ui/
│   ├── assets/
│   │   └── rover/
│   │       ├── rover_idle.gif
│   │       ├── rover_searching.gif
│   │       ├── rover_result.gif
│   │       └── rover_not_found.gif
│   └── streamlit_app.py
├── requirements.txt
└── README.md
```

Önemli Python modülleri:

- `src/config_loader.py`: YAML config dosyalarını yükler.
- `src/database/db.py`: Veritabanı bağlantısı ve temel kontrol işlemleri için kullanılır.
- `src/embedding/model_loader.py`: Fine-tuned model varsa onu, yoksa base modeli yükler. Model cache kullanır; aynı process içinde model tekrar tekrar yüklenmez.
- `src/embedding/semantic_index_builder.py`: Semantic kayıtlar için embedding üretir ve veritabanına yazar.
- `src/embedding/tokenizer_demo.py`: Tokenization, token id, vocabulary, attention mask, padding ve truncation kavramlarını gösterir.
- `src/search/query_parser.py`: Doğal dil sorgularından intent, kategori, marka, model, özellik, fiyat, puan ve sıralama bilgilerini çıkarmaya çalışır.
- `src/search/semantic_search.py`: pgvector üzerinden filtreli semantik arama yapar.
- `src/training/dataset_builder.py`: Training için JSONL query-positive pair dosyası üretir.
- `src/training/split_training_dataset.py`: Full dataset'i group-based train/validation/test dosyalarına ayırır.
- `src/training/train_sentence_transformer.py`: SentenceTransformer fine-tuning işlemini yapar.
- `src/evaluation/evaluate_retrieval.py`: Retrieval başarısını Top-1 ve Top-5 metrikleri ile ölçer.
- `src/evaluation/evaluate_split_retrieval.py`: Validation/test splitleri üzerinden exact-id ve metadata retrieval evaluation çalıştırır.
- `src/app/answer_generator.py`: Arama sonuçlarını kullanıcıya okunabilir cevaba dönüştürür.
- `src/app/chat_cli.py`: Terminal tabanlı demo uygulamasıdır.
- `ui/streamlit_app.py`: Windows XP Search Companion tarzında Streamlit demo arayüzüdür.

## 19. Notlar ve Sınırlamalar

- Bu proje gerçek üretim sistemi değildir; okul projesi/prototip seviyesindedir.
- Veri seti proje kapsamında sentetik olarak oluşturulmuştur. Ürün açıklamaları ve örnek kayıtlar gerçek ticari veri değildir.
- Ek seed dosyalarıyla genişletilmiş olsa da veri gerçek e-ticaret katalog ölçeğini temsil etmez.
- Query parser kural tabanlıdır; tüm Türkçe sorgu varyasyonlarını eksiksiz anlaması beklenmez.
- Attribute, model, kategori ve fiyat filtreleri demo verisinin metadata yapısına göre tasarlanmıştır.
- Semantic arama kalitesi embedding modeline, training verisine ve metadata temizliğine bağlıdır.
- Fine-tuned model klasörü GitHub'a yüklenmez; gerektiğinde yeniden eğitilmelidir.
- Exact-id evaluation generic sorgular için uygun değildir; bu nedenle generic sorgular exact-id metriğine dahil edilmez.
- Metadata evaluation koşul bazlı sorgular için daha anlamlıdır.
- Sistem generative cevap üretmekten çok veritabanı kayıtlarını semantic olarak bulmaya odaklanır.
- LLM asistanı cevabı, bulunan semantic kayıtlar ve basit cevap üretimi üzerine kuruludur; kapsamlı bir agent mimarisi değildir.
- Streamlit arayüzü sunum ve demo amaçlıdır; kullanıcı yönetimi, güvenlik, loglama ve ölçeklenebilirlik gibi üretim gereksinimlerini kapsamaz.

## 20. Gelecek Geliştirmeler

- Daha geniş ve gerçekçi training/evaluation dataset hazırlanabilir.
- Query parser için daha esnek NLP tabanlı yaklaşımlar eklenebilir.
- Attribute filtrelerinde eş anlamlı kelime ve toleranslı eşleşme desteği geliştirilebilir.
- API katmanı eklenerek arama servisi ayrı bir backend olarak sunulabilir.
- Streamlit arayüzü yerine daha kapsamlı bir web frontend geliştirilebilir.
- Kullanıcı geri bildirimleri ile retrieval ve ranking kalitesi iyileştirilebilir.
- Docker tabanlı kurulum dosyaları eklenerek ortam kurulumu kolaylaştırılabilir.
- Test kapsamı parser, semantic search ve seed veri kontrollerini daha sistematik ölçecek şekilde genişletilebilir.
