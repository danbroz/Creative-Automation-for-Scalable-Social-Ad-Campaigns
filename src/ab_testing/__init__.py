"""
A/B Testing Module
==================

Complete A/B testing system with automatic variant generation, statistical analysis,
and ML-based recommendations for optimal campaign performance.

Features:
    - Automatic variant generation (colors, text, layouts)
    - Statistical significance testing (Chi-square, t-tests)
    - Confidence interval calculations
    - ML-based recommendations using scikit-learn
    - Performance tracking and winner determination
    - Integration with campaign pipeline

Usage:
    from src.ab_testing import ABTestManager
    
    # Create A/B test
    manager = ABTestManager()
    test_id = manager.create_test(
        campaign_id=123,
        name="Color Variation Test",
        variants=["red", "blue", "green"]
    )
    
    # Record results
    manager.record_result(test_id, variant_id, impressions=1000, clicks=50)
    
    # Get recommendations
    recommendations = manager.get_recommendations(test_id)
"""

from .ab_test_manager import ABTestManager
from .variant_generator import VariantGenerator
from .performance_analyzer import PerformanceAnalyzer
from .recommendation_engine import RecommendationEngine

__all__ = [
    'ABTestManager',
    'VariantGenerator',
    'PerformanceAnalyzer',
    'RecommendationEngine'
]

