#!/bin/bash

# Creative Automation Pipeline Runner
# Convenience script for running the pipeline

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Creative Automation Pipeline${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import openai" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not found. Installing...${NC}"
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Check if brief file is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: ./run.sh <brief_file.json> [--verbose]${NC}"
    echo -e "\nExamples:"
    echo -e "  ./run.sh examples/campaign_brief_1.json"
    echo -e "  ./run.sh examples/campaign_brief_2.json --verbose"
    echo -e "\nAvailable examples:"
    echo -e "  - examples/campaign_brief_1.json (Wellness products)"
    echo -e "  - examples/campaign_brief_2.json (Tech accessories)"
    echo -e "  - examples/campaign_brief_3.json (Holiday gifts)"
    exit 1
fi

# Run the pipeline
echo -e "\n${GREEN}Running pipeline...${NC}\n"
python -m src.main "$@"

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Pipeline completed successfully!${NC}"
    echo -e "${BLUE}Check the output/ directory for your generated assets.${NC}"
else
    echo -e "\n${YELLOW}⚠ Pipeline encountered errors. Check logs for details.${NC}"
fi

