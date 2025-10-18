# Architecture Documentation

## System Overview

The Creative Automation Pipeline is designed as a modular, scalable system for generating social media advertising assets using GenAI. The architecture follows SOLID principles and emphasizes security, performance, and maintainability.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                │
│                  (Campaign Brief JSON)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INPUT VALIDATION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Input         │  │Brief         │  │Content       │          │
│  │Validator     │→ │Parser        │→ │Filter        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ASSET MANAGEMENT LAYER                        │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │Asset         │  Cache  │Image         │                      │
│  │Manager       │◄────────┤Generator     │                      │
│  │              │  Hit/   │(DALL-E API)  │                      │
│  └──────┬───────┘  Miss   └──────────────┘                      │
└─────────┼──────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   IMAGE PROCESSING LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Image         │→ │Compliance    │→ │Output        │          │
│  │Processor     │  │Checker       │  │Formatter     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MONITORING & LOGGING LAYER                     │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │Performance   │  │Logger &      │                             │
│  │Monitor       │  │Reporter      │                             │
│  └──────────────┘  └──────────────┘                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT                                    │
│    (Campaign Assets + Reports + Metadata)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Input Validator (`input_validator.py`)
**Purpose**: First line of defense against malicious inputs and data integrity issues.

**Responsibilities:**
- Sanitize filenames to prevent path traversal attacks
- Validate text inputs for injection patterns
- Check JSON structure and required fields
- Enforce length limits to prevent DOS attacks

**Security Measures:**
- Pattern matching for suspicious content (script tags, eval calls)
- Whitelist-based character validation
- Maximum length enforcement
- Path component stripping

**SOLID Principles:**
- **Single Responsibility**: Only handles input validation
- **Open/Closed**: Extensible for new validation rules without modification

### 2. Brief Parser (`brief_parser.py`)
**Purpose**: Parse and validate campaign briefs with type safety.

**Responsibilities:**
- Load JSON campaign briefs from files
- Validate required fields and data types
- Create typed `CampaignBrief` objects
- Integrate with `InputValidator`

**Type Safety:**
- Strong typing with Python type hints
- Structured data models
- Validation at parse time

**SOLID Principles:**
- **Single Responsibility**: Only handles brief parsing
- **Dependency Inversion**: Depends on `InputValidator` abstraction

### 3. Content Filter (`content_filter.py`)
**Purpose**: Legal compliance and brand safety filtering.

**Responsibilities:**
- Load prohibited words from configuration
- Scan content for violations
- Provide alternative suggestions
- Generate compliance reports

**Features:**
- Regex-based pattern matching
- Context extraction for violations
- Suggestion mapping for common issues
- Case-insensitive matching

**SOLID Principles:**
- **Single Responsibility**: Only handles content filtering
- **Open/Closed**: New prohibited words added via configuration

### 4. Asset Manager (`asset_manager.py`)
**Purpose**: Intelligent asset caching and management.

**Responsibilities:**
- Check for existing product assets
- Track asset metadata (usage, cost, source)
- Register new and existing assets
- Generate asset summaries

**Caching Strategy:**
- Metadata stored in JSON format
- Usage tracking for analytics
- Cost attribution for generated assets
- Normalized naming conventions

**Benefits:**
- Reduces API costs (reuse existing images)
- Faster execution (no regeneration)
- Historical tracking

**SOLID Principles:**
- **Single Responsibility**: Only manages assets
- **Interface Segregation**: Clear methods for specific operations

### 5. Image Generator (`image_generator.py`)
**Purpose**: Generate product images via OpenAI DALL-E API.

**Responsibilities:**
- Load and manage prompt templates
- Build prompts from templates
- Call DALL-E API with retry logic
- Download and save generated images
- Calculate generation costs

**Features:**
- Exponential backoff for retries
- Template-based prompt generation
- Configurable model settings
- Cost tracking per image

**Prompt Management:**
- Templates stored in separate JSON files
- Version controlled iterations
- Parameterized with product details
- Quality modifiers for consistency

**SOLID Principles:**
- **Single Responsibility**: Only handles image generation
- **Dependency Inversion**: Configurable via external files

### 6. Image Processor (`image_processor.py`)
**Purpose**: Resize images and add brand-compliant text overlays.

**Responsibilities:**
- Resize to three aspect ratios (1:1, 9:16, 16:9)
- Add text overlays with brand styling
- Apply shadows and effects
- Manage image memory efficiently

**Processing Pipeline:**
1. Open source image
2. Calculate optimal scaling
3. Resize with high-quality sampling
4. Center crop to target dimensions
5. Add text overlay with brand fonts/colors
6. Save final asset

**Brand Compliance:**
- Load brand guidelines from config
- Apply brand colors to text
- Position text per brand standards
- Add shadows for readability

**SOLID Principles:**
- **Single Responsibility**: Only handles image processing
- **Open/Closed**: New aspect ratios added via configuration

### 7. Compliance Checker (`compliance_checker.py`)
**Purpose**: Validate brand compliance of generated assets.

**Responsibilities:**
- Check image dimensions
- Validate brand color presence
- Verify logo presence (basic)
- Generate compliance scores
- Provide recommendations

**Scoring System:**
- Dimensions: 30% weight
- Colors: 40% weight
- Logo: 30% weight
- Pass threshold: 70%

**Limitations:**
- Basic template matching for logos
- Dominant color extraction (not ML-based)
- Future: ML-based logo detection

**SOLID Principles:**
- **Single Responsibility**: Only checks compliance
- **Open/Closed**: New checks added without modifying core logic

### 8. Output Formatter (`output_formatter.py`)
**Purpose**: Standardize output structure and metadata.

**Responsibilities:**
- Create standardized directory structure
- Generate asset metadata files
- Create campaign summaries
- Organize outputs consistently

**Directory Structure:**
```
output/
  {campaign}/
    {product}/
      1:1/
      9:16/
      16:9/
    campaign_summary.json
    execution_report.json
```

**SOLID Principles:**
- **Single Responsibility**: Only handles output formatting
- **Interface Segregation**: Specific methods for each output type

### 9. Performance Monitor (`performance_monitor.py`)
**Purpose**: Track performance metrics and API usage.

**Responsibilities:**
- Track API call duration and success
- Calculate throughput metrics
- Monitor costs
- Generate performance reports

**Metrics:**
- Total execution time
- API calls (success/failure rates)
- Average response times
- Cost per campaign
- Calls per minute

**SOLID Principles:**
- **Single Responsibility**: Only monitors performance
- **Open/Closed**: New metrics added via extension

### 10. Logger (`logger.py`)
**Purpose**: Comprehensive logging and reporting.

**Responsibilities:**
- Structured logging (file + console)
- Colored console output
- Track pipeline metrics
- Generate summary reports (JSON + text)

**Features:**
- Timestamped log files
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Metrics tracking throughout execution
- Beautiful console output with colorama
- JSON and human-readable reports

**SOLID Principles:**
- **Single Responsibility**: Only handles logging
- **Dependency Inversion**: Injectable into other components

## SOLID Principles Application

### Single Responsibility Principle (SRP)
Each module has one clear responsibility:
- InputValidator → Validation only
- BriefParser → Parsing only
- ImageGenerator → Generation only
- etc.

### Open/Closed Principle (OCP)
- Components open for extension via configuration
- Closed for modification of core logic
- New prompt templates without code changes
- New prohibited words via text file
- New brand colors via JSON config

### Liskov Substitution Principle (LSP)
- All components use consistent interfaces
- Subcomponents are interchangeable
- Dependency injection enables testing with mocks

### Interface Segregation Principle (ISP)
- Modules expose only necessary methods
- No fat interfaces with unused methods
- Clear, focused APIs for each component

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions
- Configuration-driven dependencies
- Easy to swap implementations (e.g., different image models)

## Data Flow

1. **Input**: User provides campaign brief JSON
2. **Validation**: Brief validated and sanitized
3. **Legal Check**: Campaign message scanned for prohibited content
4. **Asset Check**: System checks for existing product images
5. **Generation**: Missing images generated via DALL-E
6. **Processing**: Images resized to 3 aspect ratios + text overlay
7. **Compliance**: Assets checked for brand compliance
8. **Output**: Organized assets + metadata + reports saved
9. **Reporting**: Execution summary and performance metrics generated

## Security Architecture

### API Key Management
- Stored in `.env` file (never committed)
- Loaded via python-dotenv
- No hardcoded credentials
- Clear documentation in `.env.example`

### Input Sanitization
- All user inputs validated
- Path traversal prevention
- Injection attack detection
- Length limit enforcement

### Content Filtering
- Multi-layer prohibited content detection
- Configurable word lists
- Suggestion system for alternatives

### Error Handling
- Graceful degradation on failures
- Comprehensive error logging
- User-friendly error messages
- No sensitive data in logs

## Performance Optimization

### Caching Strategy
- Asset metadata cached locally
- Existing images reused
- Avoids redundant API calls
- Significant cost savings

### API Optimization
- Retry logic with exponential backoff
- Concurrent processing potential (future)
- Rate limiting respect
- Timeout handling

### Memory Management
- Image streaming for large files
- Temporary file cleanup
- Efficient image processing
- Resource cleanup on errors

## Alternative Models

### Current: OpenAI DALL-E 3
- **Pros**: High quality, good API, reliable
- **Cons**: Higher cost, API rate limits
- **Cost**: $0.040 per standard image

### Alternatives:
1. **DALL-E 2**: Lower cost ($0.020), good quality
2. **Stability AI**: Cost-effective, more control
3. **Adobe Firefly**: Adobe integration, commercial use rights
4. **Midjourney**: Artistic quality, requires different integration

### Extensibility:
- Model selection via `config/model_config.json`
- Template-based prompts portable across models
- Clean abstraction in ImageGenerator class

## Testing Strategy

### Unit Tests
- Each module tested independently
- Mocked external dependencies (API calls)
- Edge cases and error conditions
- Input validation scenarios

### Integration Tests
- Full pipeline execution
- Component interactions
- Real API calls (optional, with test key)
- End-to-end workflows

### Coverage Target
- Minimum 80% code coverage
- Focus on critical paths
- Document test results

## Future Architecture Enhancements

### Phase 2: Scalability
- Batch campaign processing
- Parallel image generation
- Queue-based architecture
- Cloud storage integration

### Phase 3: Advanced Features
- ML-based logo detection
- Advanced color matching
- Multi-language support
- Video generation

### Phase 4: Enterprise
- Web interface (React + API)
- User authentication
- Team collaboration
- Version control for campaigns
- A/B testing framework

## Cost Analysis

### Per Campaign (3 products, all new images):
- **Image Generation**: 3 × $0.040 = $0.120
- **API Calls**: 3 calls
- **Processing**: ~30 seconds
- **Storage**: ~15MB

### With Caching (2 existing, 1 new):
- **Image Generation**: 1 × $0.040 = $0.040
- **Savings**: 67% cost reduction
- **Processing**: ~15 seconds (50% faster)

### Scalability:
- **100 campaigns/month**: ~$12 (all new images)
- **100 campaigns/month**: ~$4 (with 67% cache hit)
- **Storage**: ~1.5GB/month

## Monitoring & Observability

### Metrics Tracked:
- Execution time per campaign
- API success/failure rates
- Cache hit rates
- Compliance pass rates
- Cost per campaign
- Legal filter activations

### Reports Generated:
- Execution summary (JSON + text)
- Campaign metadata
- Asset metadata
- Performance benchmarks

### Logs:
- Timestamped execution logs
- Error stack traces
- API call tracking
- User actions audit trail

## Deployment Considerations

### Local Development:
- Python virtual environment
- Local file storage
- Environment variables for config

### Production Deployment:
- Docker containerization (future)
- Cloud storage (S3, Azure Blob)
- Secrets management (AWS Secrets Manager)
- Monitoring (CloudWatch, DataDog)
- CI/CD pipeline (GitHub Actions)

## Maintenance

### Regular Tasks:
- Update prompt templates based on results
- Review prohibited words list
- Monitor API costs
- Update dependencies
- Review and act on compliance failures

### Documentation:
- Keep README updated
- Document prompt iterations
- Update architecture diagrams
- Maintain changelog

## Conclusion

This architecture provides a solid foundation for scalable creative automation while maintaining security, performance, and code quality. The modular design enables easy extension and maintenance, and the comprehensive monitoring ensures operational visibility.

