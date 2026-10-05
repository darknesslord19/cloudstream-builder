# CloudStream Builder AutoPilot

Bu paket mevcut CloudStream Builder deposuna GitHub Actions tabanlı otomasyon katmanı ekler.

## Akış

1. `site_url` workflow input olarak alınır.
2. Site GitHub runner üzerinde taranır.
3. `output/site/scan.json` oluşturulur.
4. `output/site/builder-manifest.json` oluşturulur.
5. Repository içinde gerçek CloudStream Gradle projesi varsa `./gradlew make` çalıştırılır.
6. `.cs3`, `plugins.json`, `repo.json` ve raporlar artifact olarak yüklenir.

GitHub Actions artifact sistemi build çıktılarının workflow tamamlandıktan sonra saklanmasına izin verir.

## Önemli

Bu workflow sahte veya boş `.cs3` üretmez. Repository'de gerçek CloudStream provider Kotlin kaynakları ve Gradle projesi yoksa yalnızca analiz raporu üretir.

Gerçek `URL -> provider Kotlin -> .cs3` üretiminin tamamen otomatik olması için provider üretim motorunun da Actions ortamına taşınması gerekir. Mevcut `SKILL.md` içindeki Windows `TurkStreamStudio` yolu GitHub runner'da bulunmaz.

## Kurulum

Bu ZIP'in içeriğini repo köküne birleştir:

- `.github/workflows/cloudstream-builder.yml`
- `builder/site_scan.py`
- `builder/prepare_manifest.py`
- `cloudstream-builder/agents/openai.yaml`

Sonra GitHub Actions ekranından **CloudStream Builder AutoPilot** workflow'unu çalıştır.

Workflow dispatch input'ları GitHub Actions tarafından desteklenir ve build çıktıları artifact olarak saklanabilir.
