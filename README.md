# e-ticaret-LLM-asistani

PostgreSQL tabanlı bir e-ticaret veritabanı üzerinde doğal dil ile semantik arama yapmayı sağlayan okul projesi/prototip seviyesinde bir LLM asistanı çalışmasıdır.

Bu proje, gerçek bir üretim sistemi değildir. Amaç; veritabanı tasarımı, pgvector ile semantik arama, SentenceTransformer tabanlı embedding üretimi, basit sorgu analizi, fine-tuning ve CLI üzerinden demo akışını akademik bir proje kapsamında göstermektir.

## 1. Proje Başlığı

**e-ticaret-LLM-asistani**

PostgreSQL, pgvector ve SentenceTransformer kullanılarak geliştirilen Türkçe doğal dil destekli e-ticaret semantik arama ve LLM asistanı prototipi.

## 2. Proje Amacı

Projenin temel amacı, kullanıcının Türkçe doğal dil ile yazdığı e-ticaret sorgularını analiz ederek PostgreSQL veritabanı üzerindeki ilgili kayıtları bulmak ve okunabilir bir cevap üretmektir.

Örnek olarak kullanıcı:

```text
1000 TL altı stokta olan kablosuz kulaklık öner
```

şeklinde bir sorgu girdiğinde sistem sorgudan intent ve filtre bilgilerini çıkarmayı, sorgu embedding'i üretmeyi, `semantic_index` tablosunda en yakın kayıtları bulmayı ve sonuçları terminalde anlaşılır bir cevap olarak göstermeyi hedefler.

## 3. Genel Mimari

Proje aşağıdaki ana bileşenlerden oluşur:

```text
Kullanıcı Sorgusu
       |
       v
Query Parser
       |
       v
SentenceTransformer Modeli
       |
       v
Embedding Üretimi
       |
       v
PostgreSQL + pgvector Semantic Search
       |
       v
Metadata Filtreleri
       |
       v
Answer Generator
       |
       v
CLI Demo Cevabı
```

Akışta hem kural tabanlı filtre çıkarma hem de embedding tabanlı semantik benzerlik araması birlikte kullanılır.

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

## 5. Veritabanı Yapısı

Proje, e-ticaret alanına uygun şekilde tasarlanmış ilişkisel bir PostgreSQL veritabanı üzerinde çalışır.

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

Veri durumu:

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
```

## 6. Semantic Search Akışı

Semantic search süreci aşağıdaki adımlarla çalışır:

1. Kullanıcı sorgusu terminalden alınır.
2. `src/search/query_parser.py` sorgudan intent, fiyat, stok, kategori, marka, puan ve durum filtrelerini çıkarmaya çalışır.
3. `src/embedding/model_loader.py` fine-tuned model varsa onu, yoksa base modeli yükler.
4. `src/search/semantic_search.py` kullanıcı sorgusu için embedding üretir.
5. PostgreSQL `semantic_index` tablosunda pgvector cosine distance ile en yakın kayıtlar bulunur.
6. Metadata filtreleri uygulanır.
7. `src/app/answer_generator.py` bulunan sonuçları doğal dile yakın bir cevaba dönüştürür.
8. `src/app/chat_cli.py` terminal üzerinden demo akışını çalıştırır.

## 7. Query Parser Mantığı

Query parser, kullanıcının Türkçe sorgusundan arama niyetini ve filtreleri çıkarmak için kural tabanlı desenler kullanır. Bu katman, semantik aramayı tamamen değiştirmez; semantik arama sonucunu daha anlamlı hale getirmek için ek filtre bilgisi sağlar.

Örnekler:

| Sorgu | Çıkarılan bilgiler |
| --- | --- |
| `1000 TL altı stokta olan kablosuz kulaklık öner` | `intent=product`, `max_price=1000`, `in_stock_only=True`, `category=Kulaklık` |
| `teslim edilen kargoları listele` | `intent=cargo`, `status=teslim_edildi` |
| `yüksek puanlı ayakkabı yorumları` | `intent=review`, `min_rating=4`, `category=Ayakkabı` |
| `Samsung marka telefonları göster` | `intent=product`, `brand=samsung`, `category=Telefon` |

Query parser ayarları `config/search.yaml` içinde tutulur. Fiyat, stok, tablo/intent, durum, marka ve kategori filtreleri config üzerinden yönetilebilir.

## 8. Tokenization ve Fine-Tuning Açıklaması

Projede base model olarak aşağıdaki SentenceTransformer modeli kullanılır:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Fine-tuned model çıktı dizini:

```text
models/ecommerce-semantic-model
```

`models/ecommerce-semantic-model` klasörü `.gitignore` içinde tutulur. Bu nedenle model dosyaları GitHub'a gönderilmez. Gerekirse training komutu yeniden çalıştırılarak model tekrar oluşturulur.

`src/training/tokenizer_demo.py` dosyası tokenization sürecini göstermek için hazırlanmıştır. Bu demo şu kavramları terminalde inceler:

- tokenization
- token
- token id
- vocabulary
- attention mask
- padding
- truncation

Bu modelde özel tokenlar örnek olarak `<s>`, `</s>` ve `<pad>` şeklinde görülür.

Fine-tuning sürecinde `data/training_pairs.jsonl` dosyasındaki query-positive pair kayıtları okunur ve SentenceTransformer modeli `MultipleNegativesRankingLoss` ile eğitilir.

## 9. Kurulum

Önce Python sanal ortamı oluşturulur ve bağımlılıklar yüklenir:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

PostgreSQL ve pgvector kurulumunun sistemde hazır olduğu varsayılır.

## 10. Config Dosyaları

Projede hard coding yapılmaması hedeflenmiştir. Veritabanı bağlantısı, model adı, fine-tuned model yolu, embedding dimension, tokenizer ayarları, training ayarları ve search ayarları YAML dosyaları ile yönetilir.

Ana config dosyaları:

```text
config/database.yaml
config/model.yaml
config/search.yaml
```

`config/database.yaml` veritabanı bağlantısını, SQL dosya yollarını ve semantic index tablo adını içerir.

`config/model.yaml` base model adını, fine-tuned model yolunu, embedding boyutunu, tokenizer ayarlarını ve training parametrelerini içerir.

`config/search.yaml` arama limitlerini, similarity ayarlarını, query parser kurallarını ve ranking ağırlıklarını içerir.

## 11. Veritabanını Hazırlama

Veritabanı şeması ve örnek veriler aşağıdaki komutlarla hazırlanabilir:

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

Veritabanı bağlantı bilgileri `config/database.yaml` dosyasından güncellenebilir.

## 12. Semantic Index Oluşturma

Semantic index tablosu ve embedding view'ları hazırlandıktan sonra semantic kayıtlar için embedding oluşturulur:

```bash
python -m src.embedding.semantic_index_builder
```

Model yükleme davranışını kontrol etmek için şu modül de çalıştırılabilir:

```bash
python -m src.embedding.model_loader
```

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

## 16. CLI Demo App Kullanımı

Terminal tabanlı demo uygulamasını çalıştırmak için:

```bash
python -m src.app.chat_cli
```

Demo sırasında kullanıcı Türkçe doğal dil sorguları girer. Sistem sorguyu analiz eder, semantik arama yapar ve bulunan sonuçları okunabilir bir cevap olarak terminalde gösterir.

## 17. Örnek Sorgular

```text
1000 TL altı stokta olan kablosuz kulaklık öner
Samsung marka telefonları göster
teslim edilen kargoları listele
yüksek puanlı ayakkabı yorumları
stokta olan laptop modellerini getir
indirim kuponlarını listele
iade edilen siparişleri göster
kahve makinesi ile ilgili yorumları bul
```

Modülleri tek tek denemek için kullanılabilecek komutlar:

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
│       └── 05_seed_yorumlar_iadeler_kuponlar.sql
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
├── requirements.txt
└── README.md
```

Önemli Python modülleri:

- `src/config_loader.py`: YAML config dosyalarını yükler.
- `src/database/db.py`: Veritabanı bağlantısı ve temel kontrol işlemleri için kullanılır.
- `src/embedding/model_loader.py`: Fine-tuned model varsa onu, yoksa base modeli yükler.
- `src/embedding/semantic_index_builder.py`: Semantic kayıtlar için embedding üretir ve veritabanına yazar.
- `src/search/query_parser.py`: Doğal dil sorgularından intent ve filtre bilgilerini çıkarmaya çalışır.
- `src/search/semantic_search.py`: pgvector üzerinden semantik arama yapar.
- `src/training/tokenizer_demo.py`: Tokenizer davranışını gösteren demo modüldür.
- `src/training/dataset_builder.py`: Training için JSONL query-positive pair dosyası üretir.
- `src/training/train_sentence_transformer.py`: SentenceTransformer fine-tuning işlemini yapar.
- `src/evaluation/evaluate_retrieval.py`: Retrieval başarısını Top-1 ve Top-5 metrikleri ile ölçer.
- `src/app/answer_generator.py`: Arama sonuçlarını kullanıcıya okunabilir cevaba dönüştürür.
- `src/app/chat_cli.py`: Terminal tabanlı demo uygulamasıdır.

## 19. Notlar ve Sınırlamalar

- Bu proje gerçek üretim sistemi değildir; okul projesi/prototip seviyesindedir.
- Veri seti sınırlıdır ve demo amaçlı oluşturulmuştur.
- Query parser kural tabanlıdır; her Türkçe sorguyu eksiksiz anlaması beklenmez.
- Evaluation sonucu küçük bir test sorgu seti üzerinden hesaplanmıştır.
- Fine-tuned model klasörü GitHub'a yüklenmez; gerektiğinde yeniden eğitilmelidir.
- Veritabanı bağlantı bilgileri yerel geliştirme ortamına göre güncellenmelidir.
- LLM asistanı cevabı, bulunan semantik kayıtlar ve basit cevap üretimi üzerine kuruludur; kapsamlı bir agent mimarisi değildir.

## 20. Gelecek Geliştirmeler

- Daha geniş ve çeşitli training dataset hazırlanabilir.
- Query parser için daha esnek NLP tabanlı yaklaşımlar eklenebilir.
- Değerlendirme seti büyütülerek daha güvenilir metrikler elde edilebilir.
- Web arayüzü veya API katmanı eklenebilir.
- Kullanıcı geri bildirimleri ile retrieval kalitesi iyileştirilebilir.
- Kategori, marka ve fiyat filtreleri için daha ayrıntılı ranking stratejileri denenebilir.
- Docker tabanlı kurulum dosyaları eklenerek ortam kurulumu kolaylaştırılabilir.
