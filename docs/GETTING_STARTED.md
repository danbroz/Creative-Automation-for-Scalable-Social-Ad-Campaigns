# Getting Started with Creative Automation Pipeline

This guide will help you get the Creative Automation Pipeline up and running in under 5 minutes.

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- 2GB+ free disk space

## Quick Setup (5 Minutes)

### Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd "Creatve Automation for Scalable Social Ad Campaigns"

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install openai python-dotenv pyyaml colorama requests Pillow numpy

# Optional: Install testing tools
pip install pytest pytest-cov pytest-mock
```

### Step 2: Configure API Key (1 minute)

```bash
# Your .env file is already set up with your API key
# If you need to change it, edit .env:
# nano .env  # or use any text editor

# IMPORTANT: Never commit the .env file to git
# It's already in .gitignore
```

### Step 3: Run Your First Campaign (2 minutes)

```bash
# Run the example campaign
python -m src.main examples/campaign_brief_1.json
```

You should see output like:
```
================================================================================
CREATIVE AUTOMATION PIPELINE
================================================================================

[1/7] Parsing campaign brief...
✓ Campaign: summer_wellness_2025
ℹ Products: 2
...
```

### Step 4: Check Your Results

Your generated assets will be in:
```
output/summer_wellness_2025/
```

## Running Different Examples

```bash
# Wellness campaign (2 products)
python -m src.main examples/campaign_brief_1.json

# Tech accessories (3 products)
python -m src.main examples/campaign_brief_2.json

# Holiday gifts (2 products)
python -m src.main examples/campaign_brief_3.json

# With verbose output
python -m src.main examples/campaign_brief_1.json --verbose
```

## Creating Your Own Campaign

1. Create a JSON file (e.g., `my_campaign.json`):

```json
{
  "campaign_name": "my_awesome_campaign",
  "products": [
    {
      "name": "My Product 1",
      "description": "Description for better image generation"
    },
    {
      "name": "My Product 2",
      "description": "Another product description"
    }
  ],
  "target_region": "North America",
  "target_audience": "Your target audience",
  "campaign_message": "Your campaign message here"
}
```

2. Run it:

```bash
python -m src.main my_campaign.json
```

## Understanding the Output

After running a campaign, you'll get:

```
output/
  └── {campaign_name}/
      ├── {product_1}/
      │   ├── 1:1/          # Instagram square (1080x1080)
      │   ├── 9:16/         # Stories format (1080x1920)
      │   └── 16:9/         # Facebook/YouTube (1920x1080)
      ├── {product_2}/
      │   └── ...
      ├── campaign_summary.json       # Campaign details
      ├── execution_report.json       # Detailed metrics
      └── execution_report.txt        # Human-readable report
```

Each product folder contains:
- Final images with text overlay
- Metadata JSON files with compliance scores

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_input_validator.py

# Run with coverage report
pytest --cov=src
```

## Customizing the Pipeline

### Brand Guidelines

Edit `config/brand_guidelines.json`:
- Change brand colors
- Adjust text positioning
- Modify fonts

### Prohibited Words

Edit `config/prohibited_words.txt`:
- Add words to flag
- Comment out unnecessary ones

### Model Settings

Edit `config/model_config.json`:
- Change image size
- Adjust quality (standard/hd)
- Modify retry settings

## Troubleshooting

### "API key not found"
Make sure your `.env` file contains:
```
OPENAI_API_KEY=your_key_here
```

### "Failed to generate image"
- Check your API key is valid
- Ensure you have API credits
- Check your internet connection

### "Module not found"
Make sure you:
1. Activated the virtual environment: `source venv/bin/activate`
2. Installed all dependencies: `pip install -r requirements.txt`

### Images look wrong
- Check `config/brand_guidelines.json` for text settings
- Adjust `text_overlay` positioning
- Modify font sizes

## Cost Management

### Typical Costs (DALL-E 3 Standard):
- Per image: $0.040
- 2 product campaign: $0.08 (if no cached images)
- 3 product campaign: $0.12 (if no cached images)

### Saving Money:
1. **Reuse existing images**: Place product images in `assets/products/`
2. **Use standard quality**: Already configured (not HD)
3. **Cache hits**: Pipeline automatically reuses generated images

### Checking Your Usage:
After each run, check `execution_report.txt`:
```
API PERFORMANCE
Total Cost: $0.0800 USD
```

## Next Steps

1. **Read the full documentation**: See [README.md](../README.md)
2. **Understand the architecture**: Check [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Create your campaigns**: Start generating assets!
4. **Record your demo**: Prepare for the interview presentation

## Tips for Demo Video

When recording your 2-3 minute demo:

1. **Show the command**: `python -m src.main examples/campaign_brief_1.json`
2. **Highlight the output**: Show the colorful progress indicators
3. **Open the results**: Navigate through the generated assets
4. **Show the reports**: Display execution_report.txt
5. **Discuss one insight**: E.g., "Notice how it cached 1 image, saving $0.04"

## Support

If you encounter issues:
1. Check this guide
2. Review [README.md](../README.md)
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. Run tests to verify setup: `pytest`

## Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] .env file configured with API key
- [ ] Ran example campaign successfully
- [ ] Checked output directory
- [ ] Reviewed execution reports
- [ ] Understood cost structure
- [ ] Ready to create custom campaigns

Congratulations! You're ready to automate creative production at scale! 🚀

