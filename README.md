# CORDIC Hesap Makinesi (Trig, Ters Trig, Hiperbolik, Log)

Bu proje; **CORDIC (COordinate Rotation DIgital Computer)** algoritmasını kullanarak:
- Trigonometrik fonksiyonlar (`sin, cos, tan, cot, sec, csc`)
- Ters trigonometrik fonksiyonlar (`arcsin, arccos, arctan, arccot, arcsec, arccsc`)
- Hiperbolik fonksiyonlar (`sinh, cosh, tanh, coth, sech, csch`)
- Ters hiperbolikler (`arsinh, arcosh, artanh`)
- Logaritma (`ln`, `logtaban`)

hesaplayan, **komut satırı (CLI)** tabanlı bir hesap makinesi sağlar.

> Not: Hesaplamalarda global iterasyon sayısı `PREC` kullanılır. Varsayılan: `PREC = 40`.

---

## İçerik

- [Özellikler](#özellikler)
- [Kullanım](#kullanım)
  - [Açı modları](#açı-modları)
  - [Fonksiyon çağrıları ve sözdizimi](#fonksiyon-çağrıları-ve-sözdizimi)
  - [Ölçüm havuzu](#ölçüm-havuzu)
- [Fonksiyonlar ve Tanım Aralıkları](#fonksiyonlar-ve-tanım-aralıkları)
- [Notlar ve kısıtlar](#notlar-ve-kısıtlar)

---

## Özellikler

- CORDIC tabanlı **sin/cos** hesaplaması (açı indirgeme ile daha stabil sonuçlar)
- Hiperbolik CORDIC için:
  - ölçek çarpanı (`Kh`) hesaplama
  - yakınsama aralığı (`Amax`) yönetimi
  - **aralık küçültme + ikiye katlama** (doubling) ile büyük değerlerde destek
- `ln(x)` hesaplaması için hiperbolik CORDIC vektörleme yaklaşımı
- Basit “ölçüm havuzu” ile sonuçları saklama ve tekrar kullanma
- `mode deg | rad | none` ile derece/radyan yönetimi
- Kullanıcı dostu hata mesajları ve `help/yardım` çıktısı

---

## Kullanım

### Açı modları
-mode deg : trig fonksiyonları girişini derece kabul eder.
-mode rad : trig fonksiyonları girişini radyan kabul eder.
-mode none: trig fonksiyonları girişini çıplak sayı gibi alır (radyana çevrilmez).
-Ters trig fonksiyonları (arcsin, arccos, ...) çıktıyı deg modunda dereceye çevirir; rad/none modunda radyan döndürür.

### Fonksiyon çağrıları ve sözdizimi
-Üs için ^ yazabilirsiniz: otomatik olarak ** olur.
  Örn: 2^3 → 8
-Bazı fonksiyonlar için parantezsiz yazım desteklenir:
  sin30 → sin(30)
  arcsin0.5 → arcsin(0.5)
-Parantezli kullanım her zaman geçerlidir:
  tan(45), logtaban(8,2)
-Otomatik parantez ekleme yalnızca doğrudan sayı ile bitişik yazımlarda çalışır.
-sin(pi/6) gibi ifadelerde zaten parantez kullandığınız için sorun yoktur.

### Ölçüm havuzu
-Her hesaplamanın sonucu otomatik olarak havuza eklenir:
 -Listelemek: list
 -Temizlemek: clear
 -Kullanmak: ölçüm[0], ölçüm[1], ...

---

## Fonksiyonlar ve Tanım Aralıkları

### Desteklenen fonksiyonlar

**Trig:** `sin(x)`, `cos(x)`, `tan(x)`, `cot(x)`, `sec(x)`, `csc(x)`  
**Ters Trig:** `arcsin(x)`, `arccos(x)`, `arctan(x)`, `arccot(x)`, `arcsec(x)`, `arccsc(x)`  
**Hiperbolik:** `sinh(x)`, `cosh(x)`, `tanh(x)`, `coth(x)`, `sech(x)`, `csch(x)`  
**Ters Hiperbolik:** `arsinh(x)`, `arcosh(x)`, `artanh(x)`  
**Logaritma:** `ln(x)`, `logtaban(x, b)` → taban `b` logaritması  
**Sabitler:** `pi`, `e`

### Tanım aralıkları (özet)

> CLI içinde `help` / `yardım` yazarak görebilirsiniz.

**Trig**
- `sin`, `cos`: tüm reel sayılar
- `tan`, `sec`: `x ≠ π/2 + kπ`
- `cot`, `csc`: `x ≠ kπ`

**Ters trig**
- `arcsin`, `arccos`: `-1 ≤ x ≤ 1`
- `arctan`, `arccot`: tüm reel sayılar
- `arcsec`, `arccsc`: `|x| ≥ 1`

**Hiperbolik**
- `sinh`, `cosh`, `tanh`, `sech`: tüm reel sayılar
- `coth`, `csch`: `x ≠ 0`

**Ters hiperbolik**
- `arsinh`: tüm reel sayılar
- `arcosh`: `x ≥ 1`
- `artanh`: `-1 < x < 1`

**Log**
- `ln(x)`: `x > 0`
- `logtaban(x,b)`: `x > 0`, `b > 0`, `b ≠ 1`

---

## Notlar ve kısıtlar

- `PREC` iterasyon sayısı arttıkça genellikle doğruluk artar ancak performans düşebilir.
- `tan/sec/csc/cot` için sıfıra yakın payda durumlarında hata fırlatılır:
  - trig tarafında `1e-6` eşiği,
  - hiperbolik tarafında `1e-12` eşiği kullanılır.
- Hiperbolik CORDIC, teorik olarak sınırlı yakınsama aralığına sahiptir. Bu uygulama, `Amax` üstünde girişler için **aralık küçültme** ve ardından **doubling** ile sonucu genişletir.


