# Translation Feature Guide

## Overview

The Creative Automation Pipeline now supports **automatic multi-language translation** for campaign messages. This feature allows you to generate localized ad variants for global campaigns with minimal effort.

## Features

- ✅ **9 Supported Languages**: English, Spanish, French, German, Italian, Portuguese, Chinese (Simplified & Traditional), Japanese, and Korean
- ✅ **AI-Powered Translation**: Uses OpenAI GPT-4 for context-aware, marketing-optimized translations
- ✅ **Smart Caching**: Translations are cached to reduce API costs and improve performance
- ✅ **Automatic Variant Generation**: Creates separate image variants for each language
- ✅ **Easy Integration**: Just add one field to your campaign brief JSON

## Quick Start

### 1. Add Languages to Your Campaign Brief

Simply add a `target_languages` field to your campaign brief JSON:

```json
{
  "campaign_name": "summer_wellness_2025",
  "products": [...],
  "target_region": "North America",
  "target_audience": "Health-conscious millennials",
  "campaign_message": "Discover natural wellness with our premium organic tea collection",
  "target_languages": ["en", "es", "fr"]
}
```

### 2. Run the Pipeline

The pipeline automatically detects target languages and generates multilingual variants:

```bash
python -m src.main examples/campaign_brief_1.json
```

### 3. Output Structure

The pipeline creates separate directories for each language:

```
output/
└── summer_wellness_2025/
    ├── Organic Green Tea/
    │   ├── en/
    │   │   ├── 1:1/
    │   │   │   └── Organic_Green_Tea_final.png
    │   │   ├── 9:16/
    │   │   │   └── Organic_Green_Tea_final.png
    │   │   └── 16:9/
    │   │       └── Organic_Green_Tea_final.png
    │   ├── es/
    │   │   ├── 1:1/
    │   │   ├── 9:16/
    │   │   └── 16:9/
    │   └── fr/
    │       ├── 1:1/
    │       ├── 9:16/
    │       └── 16:9/
    └── Herbal Sleep Blend/
        └── ... (same structure)
```

## Supported Languages

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `es` | Spanish | Español |
| `fr` | French | Français |
| `de` | German | Deutsch |
| `it` | Italian | Italiano |
| `pt` | Portuguese | Português |
| `zh` | Chinese (Simplified) | 简体中文 |
| `zh-TW` | Chinese (Traditional) | 繁體中文 |
| `ja` | Japanese | 日本語 |
| `ko` | Korean | 한국어 |

## Configuration

### Prerequisites

The translation feature requires:
- **OpenAI API Key**: Set `OPENAI_API_KEY` in your `.env` file
- **Python Packages**: `openai`, `python-dotenv` (already in requirements.txt)

### Translation Settings

Translation behavior is configured in `config/languages.json`:

```json
{
  "translation_settings": {
    "cache_translations": true,
    "cache_directory": ".translation_cache/",
    "use_openai_gpt4": true,
    "openai_model": "gpt-4",
    "max_retries": 3,
    "timeout": 30
  }
}
```

### Model Settings

Translation quality is controlled in `config/model_config.json`:

```json
{
  "translation_model": "gpt-4",
  "translation_settings": {
    "temperature": 0.3,
    "max_tokens": 1000
  }
}
```

## Examples

### Example 1: North American Campaign (English, Spanish, French)

```json
{
  "campaign_name": "summer_wellness_2025",
  "campaign_message": "Discover natural wellness with our premium organic tea collection",
  "target_languages": ["en", "es", "fr"]
}
```

**Generated Translations:**
- 🇺🇸 EN: "Discover natural wellness with our premium organic tea collection"
- 🇪🇸 ES: "Descubre el bienestar natural con nuestra colección premium de té orgánico"
- 🇫🇷 FR: "Découvrez le bien-être naturel avec notre collection de thé biologique premium"

### Example 2: European Campaign (Multiple Languages)

```json
{
  "campaign_name": "tech_accessories_fall",
  "campaign_message": "Elevate your tech experience with premium accessories designed for modern life",
  "target_languages": ["en", "fr", "de", "it"]
}
```

**Generated Translations:**
- 🇬🇧 EN: "Elevate your tech experience with premium accessories designed for modern life"
- 🇫🇷 FR: "Élevez votre expérience technologique avec des accessoires premium conçus pour la vie moderne"
- 🇩🇪 DE: "Verbessern Sie Ihr Tech-Erlebnis mit Premium-Zubehör für das moderne Leben"
- 🇮🇹 IT: "Eleva la tua esperienza tecnologica con accessori premium progettati per la vita moderna"

### Example 3: Global Campaign (Including Asian Languages)

```json
{
  "campaign_name": "holiday_gift_guide",
  "campaign_message": "Give the gift of thoughtful luxury this holiday season",
  "target_languages": ["en", "es", "fr", "de", "ja"]
}
```

**Generated Translations:**
- 🇺🇸 EN: "Give the gift of thoughtful luxury this holiday season"
- 🇪🇸 ES: "Regala lujo con atención esta temporada navideña"
- 🇫🇷 FR: "Offrez le cadeau du luxe réfléchi cette saison des fêtes"
- 🇩🇪 DE: "Schenken Sie durchdachten Luxus in dieser Feiertage"
- 🇯🇵 JA: "この休暇シーズンに、心のこもった贅沢な贈り物を"

## Performance & Costs

### Translation Caching

Translations are cached both in memory and on disk to minimize costs:

- **Memory Cache**: Fast lookups during pipeline execution
- **Disk Cache**: Persistent storage in `.translation_cache/` directory
- **Cache Hit**: No API call, instant translation
- **Cache Miss**: API call to OpenAI, result cached for future use

### API Costs

Using GPT-4 for translation:
- ~$0.01 per short message translation
- Cached translations: $0.00
- Example: 10 products × 4 languages = ~$0.40 (first run), $0.00 (subsequent runs)

### Performance Tips

1. **Use Caching**: Keep `.translation_cache/` directory to reuse translations
2. **Batch Similar Campaigns**: Translations are reused across campaigns
3. **Clear Cache**: Run `translator.clear_cache()` only when needed

## Troubleshooting

### Translation Not Working

**Issue**: No translations generated, only English variants created

**Solutions**:
1. Check that `OPENAI_API_KEY` is set in `.env` file
2. Verify `target_languages` is in your campaign brief JSON
3. Check console for warning messages
4. Ensure you have internet connectivity for OpenAI API

### Invalid Language Code Error

**Issue**: `ValueError: Unsupported language code: XX`

**Solution**: Use one of the supported language codes:
`en`, `es`, `fr`, `de`, `it`, `pt`, `zh`, `zh-TW`, `ja`, `ko`

### Translation Quality Issues

**Issue**: Translations don't sound natural or marketing-appropriate

**Solutions**:
1. Adjust `temperature` in `config/model_config.json` (0.3 = conservative, 0.7 = creative)
2. Ensure your original English message is clear and well-written
3. Consider using GPT-4 Turbo: set `"translation_model": "gpt-4-turbo"` in config

### API Rate Limit Errors

**Issue**: `RateLimitError` from OpenAI

**Solutions**:
1. Add retry logic (already configured in `languages.json`)
2. Process fewer languages per campaign
3. Upgrade your OpenAI API plan

## Advanced Usage

### Programmatic Access

```python
from src.translation.translator import Translator

# Initialize translator
translator = Translator()

# Translate single message
spanish = translator.translate(
    text="Buy now and save 20%!",
    target_language="es",
    source_language="en",
    context="marketing advertisement"
)
# Returns: "¡Compra ahora y ahorra 20%!"

# Translate to multiple languages
translations = translator.translate_batch(
    text="Limited time offer",
    target_languages=["es", "fr", "de"],
    source_language="en"
)
# Returns: {
#     "es": "Oferta por tiempo limitado",
#     "fr": "Offre à durée limitée", 
#     "de": "Zeitlich begrenztes Angebot"
# }

# Get cache statistics
stats = translator.get_cache_stats()
print(f"Cached translations: {stats['memory_cache_size']}")

# Clear cache
translator.clear_cache()
```

### Custom Language Fonts

For languages requiring special fonts (Chinese, Japanese, Korean), configure in `config/languages.json`:

```json
{
  "ja": {
    "name": "Japanese",
    "font_family": "Noto Sans CJK JP",
    "requires_special_font": true,
    "font_fallbacks": ["Arial Unicode MS", "MS Gothic"]
  }
}
```

## Best Practices

1. **Start with English**: Always provide your original campaign message in English
2. **Keep Messages Concise**: Shorter messages translate better and fit better on images
3. **Test Translations**: Review generated translations before publishing campaigns
4. **Regional Variants**: Consider using `es-MX` vs `es-ES` for regional Spanish variations (future feature)
5. **Cultural Sensitivity**: GPT-4 understands cultural nuances, but always review for sensitive campaigns

## Metrics & Reporting

The pipeline tracks translation usage:

```json
{
  "translation_stats": {
    "languages_generated": 4,
    "cache_hits": 12,
    "api_calls": 3,
    "total_cost": 0.03
  }
}
```

## Future Enhancements

Planned features:
- [ ] Regional language variants (es-MX, es-ES, pt-BR, pt-PT)
- [ ] Right-to-left language support (Arabic, Hebrew)
- [ ] Translation quality scoring
- [ ] A/B testing for translation variants
- [ ] Custom translation glossaries for brand terms

## Support

For issues or questions:
1. Check this guide
2. Review `/docs/TROUBLESHOOTING.md`
3. Check translation cache: `.translation_cache/`
4. Enable verbose logging: `python -m src.main brief.json --verbose`

---

**Translation Feature Status**: ✅ Production Ready

Last Updated: October 2025

