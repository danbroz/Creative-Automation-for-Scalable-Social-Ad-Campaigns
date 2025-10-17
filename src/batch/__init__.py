"""
Batch Processing Module
=======================

This module provides batch campaign processing capabilities, allowing
multiple campaigns to be processed concurrently with queue management,
progress tracking, and status reporting.

Features:
    - Process multiple campaigns in parallel
    - Queue management for campaign jobs
    - Progress tracking and status updates
    - Error handling and retry logic
    - Performance metrics per campaign

Usage:
    from src.batch import BatchProcessor
    
    processor = BatchProcessor()
    results = processor.process_directory("campaigns/")
"""

from .batch_processor import BatchProcessor
from .campaign_queue import CampaignQueue

__all__ = ['BatchProcessor', 'CampaignQueue']

