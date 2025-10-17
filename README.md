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
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

```bash
# For development (includes testing tools)
pip install -r requirements-dev.txt
```

### 2. Database Setup (Optional for Advanced Features)

For enterprise features (A/B testing, analytics, multi-tenant), setup PostgreSQL:

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb creative_automation

# Initialize database schema
python -c "from src.database import init_database; init_database()"
```

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed instructions.

### 3. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key and database URL
# OPENAI_API_KEY=your_key_here
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/creative_automation
```

### 4. Run Your First Campaign

```bash
# Run example campaign
python -m src.main examples/campaign_brief_1.json
```

```bash
# With verbose output
python -m src.main examples/campaign_brief_1.json --verbose
```

### 5. Check Output

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

### Using the Web API

Start the API server:

```bash
# Using uvicorn directly
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Or using Docker
docker-compose up
```

Access the interactive API documentation at: `http://localhost:8000`

Create a campaign via API:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/create \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {"name": "Product A", "description": "Amazing product"},
      {"name": "Product B"}
    ],
    "target_region": "North America",
    "target_audience": "Young professionals",
    "campaign_message": "Limited time offer!",
    "language": "en"
  }'
```

Check campaign status:

```bash
curl http://localhost:8000/api/v1/campaigns/{campaign_id}
```

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
```

```bash
# Run with coverage report
pytest --cov=src --cov-report=html
```

```bash
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

## ✨ Enterprise Features (v2.0 - v2.1)

### Database-Powered Features (v2.1)
- ✅ PostgreSQL integration with SQLAlchemy ORM
- ✅ Complete database schema (15+ tables)
- ✅ Ready for: A/B testing, Analytics, Multi-tenant, Collaboration
- ✅ Database migrations with Alembic
- ✅ Connection pooling and session management

### Core Features (v2.0)

### Multi-Language Support
- ✅ 9 languages supported: EN, ES, FR, DE, IT, PT, ZH, JA, KO
- ✅ OpenAI GPT-4 powered translations
- ✅ Translation caching to reduce API costs
- ✅ Context-aware marketing translations

### Cloud Storage Integration
- ✅ AWS S3 support
- ✅ Azure Blob Storage support
- ✅ Google Cloud Storage support
- ✅ Local filesystem (default)
- ✅ Easy provider switching via configuration

### Batch Processing
- ✅ Process 50+ campaigns concurrently
- ✅ Queue management system
- ✅ Progress tracking and status updates
- ✅ Automatic retry logic

### Web API Interface
- ✅ FastAPI REST API
- ✅ Campaign creation endpoints
- ✅ Real-time status tracking
- ✅ Swagger UI documentation
- ✅ Optional API key authentication

### Advanced AI Features
- ✅ OpenAI Vision API logo detection
- ✅ Video generation from static images (FFmpeg-based)
- ✅ Placeholder for OpenAI video API (when available)

### DevOps Ready
- ✅ Docker containerization
- ✅ Docker Compose for easy deployment
- ✅ Health check endpoints
- ✅ Comprehensive logging

## 🔮 Future Enhancements

- [ ] A/B testing recommendations
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] CDN integration for asset delivery
- [ ] Multi-tenant support

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

MIT License

Copyright (c) 2025 Dan Broz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🆘 Support

For issues or questions:
1. Check the [Architecture Documentation](ARCHITECTURE.md)
2. Review example campaigns in `examples/`
3. Create an issue on GitHub
