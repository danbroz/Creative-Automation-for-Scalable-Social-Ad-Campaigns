"""
Performance Monitor Module
Tracks API performance, response times, and cost metrics.
"""

import time
from typing import Dict, Optional
from datetime import datetime


class PerformanceMonitor:
    """Monitors performance metrics for the pipeline."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.api_calls = []
        self.start_time = None
        self.end_time = None
    
    def start_timer(self) -> None:
        """Start the overall pipeline timer."""
        self.start_time = time.time()
    
    def stop_timer(self) -> None:
        """Stop the overall pipeline timer."""
        self.end_time = time.time()
    
    def get_elapsed_time(self) -> float:
        """
        Get elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def track_api_call(
        self,
        endpoint: str,
        duration: float,
        success: bool,
        cost: float = 0.0,
        error: Optional[str] = None
    ) -> None:
        """
        Track an API call.
        
        Args:
            endpoint: API endpoint called
            duration: Call duration in seconds
            success: Whether call was successful
            cost: Cost of the API call in USD
            error: Error message if call failed
        """
        self.api_calls.append({
            'endpoint': endpoint,
            'duration': duration,
            'success': success,
            'cost': cost,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_api_stats(self) -> Dict[str, any]:
        """
        Get API call statistics.
        
        Returns:
            Dictionary with API statistics
        """
        if not self.api_calls:
            return {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'success_rate': 0.0,
                'average_duration': 0.0,
                'total_cost': 0.0
            }
        
        total_calls = len(self.api_calls)
        successful_calls = sum(1 for call in self.api_calls if call['success'])
        failed_calls = total_calls - successful_calls
        
        total_duration = sum(call['duration'] for call in self.api_calls)
        average_duration = total_duration / total_calls if total_calls > 0 else 0.0
        
        total_cost = sum(call['cost'] for call in self.api_calls)
        
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0.0
        
        return {
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate': round(success_rate, 2),
            'average_duration': round(average_duration, 2),
            'total_cost': round(total_cost, 4),
            'calls': self.api_calls
        }
    
    def get_performance_report(self) -> Dict[str, any]:
        """
        Get comprehensive performance report.
        
        Returns:
            Dictionary with performance metrics
        """
        api_stats = self.get_api_stats()
        elapsed_time = self.get_elapsed_time()
        
        return {
            'total_execution_time': round(elapsed_time, 2),
            'api_statistics': api_stats,
            'throughput': {
                'calls_per_minute': round((api_stats['total_calls'] / elapsed_time * 60), 2) if elapsed_time > 0 else 0.0
            }
        }

