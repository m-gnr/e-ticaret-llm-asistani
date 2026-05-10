# Retrieval ve Evaluation Notları

## 1. Semantic Index Yapısı

`semantic_index` tablosu, farklı e-ticaret kayıtlarını tek bir semantik arama yapısında toplar. Temel alanlar şunlardır:

- `kaynak_tablo`: Kaydın geldiği tabloyu belirtir. Örneğin `urun_varyantlari`, `urun_yorumlari`, `siparisler`.
- `kaynak_id`: Kaynak tablodaki gerçek kayıt kimliğidir.
- `baslik`: Sonuç listesinde gösterilecek kısa başlıktır.
- `icerik`: Embedding üretiminde kullanılan açıklayıcı metindir.
- `metadata`: Marka, kategori, fiyat, stok, puan, durum ve özellik gibi filtrelenebilir alanları JSON formatında tutar.
- `embedding`: Metnin vektör karşılığıdır.

Embedding alanı `vector(384)` tipindedir. Bu, kullanılan SentenceTransformer modelinin her metni 384 boyutlu bir sayısal vektöre dönüştürdüğü anlamına gelir. `ivfflat` index ise pgvector üzerinde benzer vektörleri daha hızlı bulmak için kullanılır.

## 2. Embedding View’ları

`vw_semantic_all`, ürün, yorum, sipariş, kargo, iade, kupon gibi kayıtları ortak bir formata dönüştürür. Bu view sayesinde her kaynak tablo için ayrı ayrı embedding üretmek yerine, tüm kayıtlar `kaynak_tablo`, `kaynak_id`, `baslik`, `icerik` ve `metadata` yapısında okunabilir.

Bu view’lar embedding üretimi için kaynak görevi görür. `semantic_index_builder.py`, view’dan gelen kayıtların metnini modele verir ve oluşan vektörleri `semantic_index` tablosuna yazar.

## 3. Dataset Builder

`dataset_builder.py`, `training_pairs.jsonl` dosyasını üretir. Her satır bir `query-positive_text` çiftidir:

- `query`: Kullanıcı sorgusuna benzeyen doğal dil ifadesi.
- `positive_text`: Bu sorguyla eşleşmesi beklenen veritabanı metni.

Dataset içinde ayrıca `query_type` ve `evaluation_mode` alanları bulunur. Bunlar evaluation’ın daha adil yapılması için eklendi:

- `specific`: Belirli bir ürüne veya kayda yakın sorgular.
- `navigational`: Sipariş no, takip no, kupon kodu gibi tekil tanımlayıcı içeren sorgular.
- `generic`: Birden fazla doğru cevabı olabilecek sorgular.
- `attribute`: Fiyat, stok, renk, beden, RAM, puan gibi metadata koşullarıyla değerlendirilebilen sorgular.

## 4. Train / Validation / Test Split

Dataset tek dosya olarak bırakılmadı; `train_pairs.jsonl`, `val_pairs.jsonl` ve `test_pairs.jsonl` olarak ayrıldı. Bu yapı model eğitimi ve ölçümü daha düzenli hale getirir.

Split işlemi satır bazlı rastgele yapılmaz. `source_table + source_id` bazlı group-based split uygulanır. Böylece aynı ürüne veya aynı yoruma ait query’lerin bir kısmı train, bir kısmı test setine düşmez. Bu da veri sızıntısını azaltır.

## 5. Fine-tuning

Projede hazır `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` modeli temel alınır. Fine-tuning sırasında `MultipleNegativesRankingLoss` kullanılır.

Amaç, kullanıcı sorgusu ile doğru veritabanı metnini embedding uzayında birbirine yaklaştırmaktır. Böylece benzer anlam taşıyan sorgu ve kayıtlar pgvector aramasında daha yakın bulunur.

## 6. Semantic Search Akışı

Arama akışı özetle şöyledir:

1. Kullanıcı sorgusu `query_parser.py` ile analiz edilir.
2. Fiyat, stok, marka, kategori, puan, model ve attribute filtreleri çıkarılır.
3. Sorgu embedding’e çevrilir.
4. `semantic_index` üzerinde vector similarity ile en yakın kayıtlar aranır.
5. Metadata filtreleri SQL seviyesinde uygulanır.
6. Sonuçlarda `distance` ve `similarity_score` hesaplanır.

## 7. Metadata Filter ve Parser

Parser fiyat, stok, marka, kategori, renk, beden, RAM, depolama, puan gibi alanları structured filtrelere dönüştürür. Örneğin:

- `s beden siyah tişört` → kategori `Tişört`, attribute `beden=S`, `renk=Siyah`
- `32 gb ram oyuncu laptop` → attribute `ram=32GB`, `oyuncu=true`
- `yüksek puanlı ayakkabı yorumları` → min puan `4`, kategori `Ayakkabı`

Tekil tanımlayıcılar exact metadata filtre olarak kullanılır:

- `SIP-2026-0007` → `metadata.siparis_no`
- `AR000002` → `metadata.takip_no`
- `KARGO0` → `metadata.kod`

SIP numarası kargo veya iade bağlamında geçerse, arama ilgili tabloya yönlendirilir.

## 8. Fallback Search

Strict metadata filtreleri bazen hiç sonuç döndürmeyebilir. Bu durumda fallback semantic search devreye girer. İlk fallback seviyesinde attribute filtreleri gevşetilir; ikinci seviyede daha minimal filtrelerle arama yapılır.

Exact identifier sorgularında fallback filtreleri gevşetmez. Örneğin sipariş no, takip no veya kupon kodu varsa yanlış kayda gitmemek için exact filtre korunur.

## 9. Evaluation Türleri

Projede üç evaluation yaklaşımı vardır:

- Manuel evaluation: `evaluate_retrieval.py` içinde elle tanımlanmış test sorguları metadata koşullarıyla kontrol edilir.
- Exact-id split evaluation: `specific` ve `navigational` sorgularda `source_table + source_id` eşleşmesi aranır.
- Metadata evaluation: `attribute` sorgularda sonuçların beklenen metadata koşullarını sağlayıp sağlamadığı ölçülür.

Generic sorgular exact-id metriğine dahil edilmez. Çünkü `Laptop yorumları` veya `Samsung ürünleri` gibi sorgularda birden fazla kabul edilebilir doğru cevap olabilir.

## 10. Kullanılan Metrikler

- Top-1 Accuracy: İlk sonucun doğru olup olmadığını ölçer.
- Top-5 Accuracy: İlk 5 sonuç içinde doğru eşleşme olup olmadığını ölçer.
- MRR: Doğru sonucun kaçıncı sırada geldiğini dikkate alır.
- Source table bazlı başarı: Hangi kaynak tablolarda başarının yüksek veya düşük olduğunu gösterir.

## 11. Sonuçların Yorumu

Son çalıştırmaya göre exact-id split evaluation değerleri:

- Validation exact-id Top-1: 0.8547
- Validation exact-id Top-5: 0.9162
- Validation exact-id MRR: 0.8810
- Test exact-id Top-1: 0.9167
- Test exact-id Top-5: 1.0000
- Test exact-id MRR: 0.9568

Bu değerler model, veri seti, split ve semantic index yeniden üretildiğinde değişebilir.

## 12. Komutlar

```bash
python -m src.training.dataset_builder
python -m src.training.split_training_dataset
python -m src.training.train_sentence_transformer
python -m src.embedding.semantic_index_builder
python -m src.evaluation.evaluate_retrieval
python -m src.evaluation.evaluate_split_retrieval --split validation --evaluation-mode exact_id --limit 5
python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode exact_id --limit 5
python -m src.evaluation.evaluate_split_retrieval --split validation --evaluation-mode metadata --limit 5
python -m src.evaluation.evaluate_split_retrieval --split test --evaluation-mode metadata --limit 5
```
