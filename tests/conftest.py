"""
Pytest configuration and fixtures.
"""

import pytest
import json
import tempfile
from pathlib import Path


@pytest.fixture
def sample_brief_data():
    """Sample campaign brief data for testing."""
    return {
        "campaign_name": "test_campaign",
        "products": [
            {"name": "Test Product 1", "description": "Test description 1"},
            {"name": "Test Product 2", "description": "Test description 2"}
        ],
        "target_region": "Test Region",
        "target_audience": "Test Audience",
        "campaign_message": "Test message for campaign"
    }


@pytest.fixture
def sample_brief_file(sample_brief_data, tmp_path):
    """Create a temporary brief file for testing."""
    brief_file = tmp_path / "test_brief.json"
    with open(brief_file, 'w') as f:
        json.dump(sample_brief_data, f)
    return brief_file


@pytest.fixture
def temp_assets_dir(tmp_path):
    """Create temporary assets directory."""
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    return assets_dir


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir

