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

## 💻 Platform Support

**Works on all major operating systems:**

- ✅ **Linux** (Ubuntu, Debian, Fedora, etc.)
- ✅ **macOS** (Big Sur 11.0+, Monterey, Ventura, Sonoma, Sequoia)
- ✅ **Windows** (10, 11, Server 2019+)
- ✅ **Docker** (Recommended - identical on all platforms)

See [CROSS_PLATFORM_GUIDE.md](docs/CROSS_PLATFORM_GUIDE.md) for platform-specific instructions and [DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for comprehensive Docker container usage.

## 📋 Requirements

- Python 3.9 or higher
- OpenAI API key (DALL-E 3 access)
- 2GB+ free disk space
- Docker (optional but recommended)

## 🚀 Quick Start

### 🐳 Docker Method (Recommended - Works on All Platforms)

**Prerequisites:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop) for your platform or Docker Compose

```bash
# Clone the repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns
```

```bash
# Set up environment
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

```bash
# Start the application
docker-compose up --build
```

```bash
# Access the web interface
# Open browser to: http://localhost:8000
```

**That's it!** The Docker method works identically on Ubuntu, macOS, and Windows.


## 📈 Success Metrics

The pipeline tracks:
- **Campaign assets generated per minute**
- **API call success rate** (target: >95%)
- **Cache hit rate** (reused vs generated images)
- **Brand compliance pass rate**
- **Legal filter activation rate**
- **Total cost per campaign** (API usage)

## 🏗️ Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design, component interactions, and SOLID principle applications.

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
- ✅ SQLite integration with SQLAlchemy ORM (zero setup!)
- ✅ Complete database schema (15+ tables)
- ✅ Ready for: A/B testing, Analytics, Multi-tenant, Collaboration
- ✅ Database migrations with Alembic
- ✅ Single-file portability (easy backup)

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

## 🚀 Advanced Features (v2.1 - Ready for Implementation)

All advanced enterprise features have complete foundations:

### ✅ Database Layer Complete
- Full SQLite schema with 15+ models (no server required!)
- Multi-tenant data isolation architecture
- A/B testing tables (ABTest, ABTestVariant, ABTestResult)
- Analytics event tracking (AnalyticsEvent)
- Collaboration infrastructure (Comment)
- CDN delivery tracking (CDNDelivery)
- Subscription management (Tenant, Subscription)

### ✅ Configuration Ready
- `config/ab_testing.json` - A/B test settings
- `config/collaboration.json` - Real-time collaboration config
- `config/analytics.json` - Analytics and dashboard settings
- `config/cdn.json` - CDN provider configurations
- `config/tenancy.json` - Multi-tenant and subscription tiers

### ✅ Dependencies Installed
- Statistical analysis (scipy, scikit-learn)
- WebSocket support (websockets, python-socketio)
- Analytics (pandas, plotly, reportlab)
- CDN integration (cloudflare SDK)
- Database (SQLite, SQLAlchemy, Alembic)

### 📝 Implementation Guide
See [ENTERPRISE_FEATURES_IMPLEMENTATION.md](docs/ENTERPRISE_FEATURES_IMPLEMENTATION.md) for:
- Complete implementation templates for all features
- Code examples with comprehensive comments
- API endpoint specifications
- Database usage patterns
- Frontend integration examples

**Estimated implementation time: 2-3 weeks**

## 🔮 Future Enhancements

- [ ] Machine learning-based asset generation
- [ ] Voice-controlled campaign creation
- [ ] Automated social media posting
- [ ] Real-time performance optimization
- [ ] Advanced competitor analysis

## 📚 Additional Resources

- [OpenAI DALL-E API Documentation](https://platform.openai.com/docs/guides/images)
- [Prompt Engineering Guide](prompts/prompt_templates.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)

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
