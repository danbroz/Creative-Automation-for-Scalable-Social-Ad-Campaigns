# Creative Automation Pipeline for Social Ad Campaigns

A GenAI-powered system for generating scalable social media advertising assets with brand compliance, legal filtering, and comprehensive reporting.

## 🎯 Overview

This pipeline automates the creation of social media ad campaign assets by:
- Generating or reusing product images using OpenAI DALL-E 3
- Creating variants for 3 aspect ratios (1:1, 9:16, 16:9)
- Adding brand-compliant text overlays
- Checking brand compliance (colors, dimensions)
- Filtering content for legal compliance
- Generating comprehensive execution reports

## ✨ Features

- **Intelligent Asset Management**: Reuses existing assets to save costs
- **Multi-Format Generation**: Creates assets for Instagram (1:1, 9:16), Facebook/YouTube (16:9)
- **Brand Compliance**: Validates brand colors and image quality
- **Legal Content Filtering**: Scans for prohibited words with suggestions
- **Performance Monitoring**: Tracks API costs, response times, and success rates
- **Comprehensive Reporting**: JSON and human-readable execution summaries

## 📋 Requirements

- Python 3.9 or higher
- OpenAI API key (DALL-E 3 access)
- 2GB+ free disk space

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd creative-automation-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements-dev.txt
```

### 2. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 3. Run Your First Campaign

```bash
# Run example campaign
python -m src.main examples/campaign_brief_1.json

# With verbose output
python -m src.main examples/campaign_brief_1.json --verbose
```

### 4. Check Output

Your generated assets will be in:
```
output/
  └── summer_wellness_2025/
      ├── organic_green_tea/
      │   ├── 1:1/
      │   ├── 9:16/
      │   └── 16:9/
      ├── herbal_sleep_blend/
      │   ├── 1:1/
      │   ├── 9:16/
      │   └── 16:9/
      ├── campaign_summary.json
      ├── execution_report.json
      └── execution_report.txt
```

## 📖 Usage

### Campaign Brief Format

Create a JSON file with the following structure:

```json
{
  "campaign_name": "my_campaign",
  "products": [
    {
      "name": "Product Name",
      "description": "Product description for image generation"
    }
  ],
  "target_region": "North America",
  "target_audience": "Your target audience description",
  "campaign_message": "Text to display on final assets"
}
```

**Required Fields:**
- `products`: List of at least 2 products with `name` field
- `target_region`: Target market/region
- `target_audience`: Audience description
- `campaign_message`: Campaign text (max 500 characters)

**Optional Fields:**
- `campaign_name`: Auto-generated if not provided
- `product.description`: Used for better image generation

### Command Line Options

```bash
python -m src.main [OPTIONS] BRIEF_FILE

Options:
  -v, --verbose     Enable verbose output
  --version         Show version and exit
  -h, --help        Show help message

Examples:
  python -m src.main examples/campaign_brief_1.json
  python -m src.main my_campaign.json --verbose
```

## 🔧 Configuration

### Brand Guidelines (`config/brand_guidelines.json`)

Customize your brand identity:

```json
{
  "brand_name": "YourBrand",
  "brand_colors": {
    "primary": "#FF6B35",
    "secondary": "#004E89",
    "text": "#2D3142"
  },
  "fonts": {
    "heading": "Arial Bold",
    "size_heading": 72
  },
  "text_overlay": {
    "position": "bottom",
    "padding": 40
  }
}
```

### Prohibited Words (`config/prohibited_words.txt`)

Add words to flag in campaign messages:

```
guaranteed
miracle
instant
best
```

### Model Configuration (`config/model_config.json`)

Adjust AI model settings and pricing:

```json
{
  "primary_model": "dall-e-3",
  "model_settings": {
    "dall-e-3": {
      "size": "1024x1024",
      "quality": "standard",
      "max_retries": 3
    }
  }
}
```

## 📊 Output Structure

```
output/
└── {campaign_name}/
    ├── {product_1}/
    │   ├── 1:1/
    │   │   ├── {product}_final.png
    │   │   └── {product}_final_metadata.json
    │   ├── 9:16/
    │   │   └── ...
    │   └── 16:9/
    │       └── ...
    ├── {product_2}/
    │   └── ...
    ├── campaign_summary.json
    ├── execution_report.json
    └── execution_report.txt
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_brief_parser.py
```

## 📈 Success Metrics

The pipeline tracks:
- **Campaign assets generated per minute**
- **API call success rate** (target: >95%)
- **Cache hit rate** (reused vs generated images)
- **Brand compliance pass rate**
- **Legal filter activation rate**
- **Total cost per campaign** (API usage)

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design, component interactions, and SOLID principle applications.

**Key Components:**
1. **Input Validator** - Sanitizes inputs
2. **Brief Parser** - Validates campaign briefs
3. **Content Filter** - Legal compliance checking
4. **Asset Manager** - Intelligent asset caching
5. **Image Generator** - DALL-E API integration
6. **Image Processor** - Resizing and text overlay
7. **Compliance Checker** - Brand validation
8. **Output Formatter** - Standardized outputs
9. **Performance Monitor** - Metrics tracking
10. **Logger** - Comprehensive reporting

## 🔒 Security

- **API Keys**: Never committed, stored in `.env`
- **Input Sanitization**: All inputs validated and sanitized
- **Content Filtering**: Multi-layer prohibited content detection
- **Error Handling**: Graceful degradation with comprehensive logging

## 💰 Cost Estimation

**DALL-E 3 Pricing:**
- Standard quality (1024x1024): $0.040 per image
- HD quality (1024x1024): $0.080 per image

**Example Campaign:**
- 3 products requiring new images
- Cost: ~$0.12 (standard quality)
- Assets reused from cache: $0.00

## 🚧 Known Limitations

- English text only (localization is future enhancement)
- Basic logo detection (template matching, not ML-based)
- Local storage only (cloud integration planned)
- Single campaign processing (batch mode planned)

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced ML-based logo detection
- [ ] Cloud storage integration (AWS S3, Azure Blob)
- [ ] Batch campaign processing
- [ ] Web interface
- [ ] A/B testing recommendations
- [ ] Video generation support

## 📚 Additional Resources

- [OpenAI DALL-E API Documentation](https://platform.openai.com/docs/guides/images)
- [Prompt Engineering Guide](prompts/prompt_templates.md)
- [Architecture Documentation](ARCHITECTURE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues or questions:
1. Check the [Architecture Documentation](ARCHITECTURE.md)
2. Review example campaigns in `examples/`
3. Create an issue on GitHub

## 🎓 Interview Assessment

This project was created as part of the Adobe Forward Deployed AI Engineer assessment, demonstrating:
- GenAI API integration (DALL-E 3)
- Scalable pipeline architecture
- Brand and legal compliance automation
- Performance monitoring and cost optimization
- Comprehensive testing and documentation
- SOLID principles and best practices

