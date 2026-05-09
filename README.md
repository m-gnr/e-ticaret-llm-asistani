# e-ticaret-LLM-asistani

PostgreSQL tabanlı bir e-ticaret veritabanı üzerinde Türkçe doğal dil sorguları ile semantik arama yapılmasını sağlayan okul projesi/prototip seviyesinde bir LLM asistanı çalışmasıdır.

Bu proje gerçek bir üretim sistemi değildir. Amaç; veritabanı tasarımı, pgvector ile semantik arama, SentenceTransformer tabanlı embedding üretimi, kural tabanlı sorgu analizi, fine-tuning ve CLI/Streamlit üzerinden demo akışını akademik bir proje kapsamında göstermektir.

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

## 7. Query Parser Mantığı

Query parser kural tabanlı çalışır. Amaç, doğal dil sorgusundan arama motorunun kullanabileceği yapısal filtreleri çıkarmaktır.

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

`src/training/tokenizer_demo.py` tokenization sürecini göstermek için hazırlanmıştır. Bu demo token, token id, vocabulary, attention mask, padding ve truncation kavramlarını terminalde gösterir. Bu modelde özel tokenlar örnek olarak `<s>`, `</s>` ve `<pad>` şeklinde görülür.

Fine-tuning aşamasında `data/training_pairs.jsonl` dosyasındaki query-positive pair kayıtları okunur ve SentenceTransformer modeli `MultipleNegativesRankingLoss` ile eğitilir.

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
```

- `config/database.yaml`: Veritabanı bağlantısı, SQL dosya yolları ve semantic index tablo adı.
- `config/model.yaml`: Base model adı, fine-tuned model yolu, embedding boyutu, tokenizer ve training parametreleri.
- `config/search.yaml`: Arama limitleri, similarity ayarları, query parser kuralları ve ranking ayarları.

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

Bu dosya fine-tuning aşamasında eğitim verisi olarak kullanılır.

## 14. Fine-Tuning Yapma

SentenceTransformer modelini proje verisiyle fine-tune etmek için:

```bash
python -m src.training.train_sentence_transformer
```

Eğitim sonunda model aşağıdaki dizine kaydedilir:

```text
models/ecommerce-semantic-model
```

Bu dizin `.gitignore` içindedir. Model dosyaları repository'ye dahil edilmez.

## 15. Evaluation Çalıştırma

Retrieval başarısını test sorguları ile ölçmek için:

```bash
python -m src.evaluation.evaluate_retrieval
```

Son ölçüm:

| Metrik | Sonuç |
| --- | ---: |
| Test sorgusu sayısı | 8 |
| Top-1 doğru | 8/8 |
| Top-5 doğru | 8/8 |
| Top-1 Accuracy | 1.0000 |
| Top-5 Accuracy | 1.0000 |

Bu sonuç proje içindeki sınırlı test sorguları üzerinden elde edilmiştir. Daha geniş ve çeşitli test setleri ile farklı sonuçlar alınabilir.

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

Streamlit arayüzünde Windows XP Search Companion stilinde bir sol arama paneli ve sağ tarafta Search Results alanı bulunur. Kullanıcı sorgusu, sonuç sayısı ve teknik detay görünümü buradan kontrol edilebilir. Rover GIF durumu arama öncesi, arama sırasında, sonuç bulunduğunda ve sonuç bulunamadığında farklı görsellerle gösterilir.

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
python -m src.embedding.semantic_index_builder
python -m src.search.query_parser
python -m src.search.semantic_search
python -m src.training.tokenizer_demo
python -m src.training.dataset_builder
python -m src.training.train_sentence_transformer
python -m src.evaluation.evaluate_retrieval
python -m src.app.chat_cli
python -m streamlit run ui/streamlit_app.py
```

## 18. Proje Klasör Yapısı

```text
.
├── config/
│   ├── database.yaml
│   ├── model.yaml
│   └── search.yaml
├── data/
│   └── training_pairs.jsonl
├── models/
│   └── ecommerce-semantic-model/        # Git'e dahil edilmez
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
│   │   └── semantic_index_builder.py
│   ├── evaluation/
│   │   └── evaluate_retrieval.py
│   ├── search/
│   │   ├── query_parser.py
│   │   └── semantic_search.py
│   ├── training/
│   │   ├── dataset_builder.py
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
- `src/embedding/model_loader.py`: Fine-tuned model varsa onu, yoksa base modeli yükler.
- `src/embedding/semantic_index_builder.py`: Semantic kayıtlar için embedding üretir ve veritabanına yazar.
- `src/search/query_parser.py`: Doğal dil sorgularından intent, kategori, marka, model, özellik, fiyat, puan ve sıralama bilgilerini çıkarmaya çalışır.
- `src/search/semantic_search.py`: pgvector üzerinden filtreli semantik arama yapar.
- `src/training/tokenizer_demo.py`: Tokenizer davranışını gösteren demo modüldür.
- `src/training/dataset_builder.py`: Training için JSONL query-positive pair dosyası üretir.
- `src/training/train_sentence_transformer.py`: SentenceTransformer fine-tuning işlemini yapar.
- `src/evaluation/evaluate_retrieval.py`: Retrieval başarısını Top-1 ve Top-5 metrikleri ile ölçer.
- `src/app/answer_generator.py`: Arama sonuçlarını kullanıcıya okunabilir cevaba dönüştürür.
- `src/app/chat_cli.py`: Terminal tabanlı demo uygulamasıdır.
- `ui/streamlit_app.py`: Windows XP Search Companion tarzında Streamlit demo arayüzüdür.

## 19. Notlar ve Sınırlamalar

- Bu proje gerçek üretim sistemi değildir; okul projesi/prototip seviyesindedir.
- Veri seti demo amaçlıdır. Ek seed dosyalarıyla genişletilmiş olsa da gerçek e-ticaret katalog ölçeğini temsil etmez.
- Query parser kural tabanlıdır; tüm Türkçe sorgu varyasyonlarını eksiksiz anlaması beklenmez.
- Attribute, model, kategori ve fiyat filtreleri demo verisinin metadata yapısına göre tasarlanmıştır.
- Semantic arama kalitesi embedding modeline, training verisine ve metadata temizliğine bağlıdır.
- Fine-tuned model klasörü GitHub'a yüklenmez; gerektiğinde yeniden eğitilmelidir.
- Evaluation sonucu küçük ve kontrollü bir test sorgu seti üzerinden hesaplanmıştır.
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
