### 🐍 Native Python Method

#### Linux & macOS

```bash
# Clone the repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Create virtual environment
python3 -m venv venv  # Use python3 on macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env file and add your OpenAI API key

# Run example campaign
./run.sh examples/campaign_brief_1.json --verbose
```

#### Windows (Command Prompt)

```cmd
REM Clone the repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

REM Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Set up environment
copy .env.example .env
REM Edit .env file and add your OpenAI API key

REM Run example campaign
run.bat examples\campaign_brief_1.json --verbose
```

#### Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/danbroz/Creatve-Automation-for-Scalable-Social-Ad-Campaigns.git
cd Creatve-Automation-for-Scalable-Social-Ad-Campaigns

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment
Copy-Item .env.example .env
# Edit .env file and add your OpenAI API key

# Run example campaign
.\run.ps1 examples\campaign_brief_1.json --verbose
```

### Configuration

Edit the `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your-api-key-here
```

### Web Interface

The web interface is automatically available when using Docker:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

For native Python installation, start the web interface with:
```bash
python -m src.api.app
```

#### Using Python Directly (All Platforms)

```bash
# Run example campaign
python -m src.main examples/campaign_brief_1.json

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
