"""
Logger Module
Provides structured logging and reporting functionality.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class PipelineLogger:
    """Handles logging and reporting for the creative automation pipeline."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"pipeline_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Metrics tracking
        self.metrics = {
            'start_time': datetime.now(),
            'end_time': None,
            'total_products': 0,
            'images_generated': 0,
            'images_reused': 0,
            'api_calls': 0,
            'api_failures': 0,
            'compliance_checks': 0,
            'compliance_passes': 0,
            'legal_flags': 0,
            'total_cost': 0.0,
            'errors': []
        }
    
    def info(self, message: str, color: bool = True) -> None:
        """Log info message."""
        self.logger.info(message)
        if color:
            print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
    
    def success(self, message: str) -> None:
        """Log success message."""
        self.logger.info(f"SUCCESS: {message}")
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
            self.metrics['errors'].append({
                'message': message,
                'exception': str(exception),
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.logger.error(message)
            self.metrics['errors'].append({
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def track_image_generated(self, product_name: str, cost: float = 0.0) -> None:
        """Track generated image."""
        self.metrics['images_generated'] += 1
        self.metrics['api_calls'] += 1
        self.metrics['total_cost'] += cost
        self.success(f"Generated image for {product_name} (cost: ${cost:.4f})")
    
    def track_image_reused(self, product_name: str) -> None:
        """Track reused image."""
        self.metrics['images_reused'] += 1
        self.info(f"Reused existing image for {product_name}")
    
    def track_api_failure(self) -> None:
        """Track API failure."""
        self.metrics['api_failures'] += 1
    
    def track_compliance_check(self, passed: bool, product_name: str) -> None:
        """Track compliance check."""
        self.metrics['compliance_checks'] += 1
        if passed:
            self.metrics['compliance_passes'] += 1
            self.success(f"Compliance check passed for {product_name}")
        else:
            self.warning(f"Compliance check failed for {product_name}")
    
    def track_legal_flag(self, word: str, message: str) -> None:
        """Track legal content flag."""
        self.metrics['legal_flags'] += 1
        self.warning(f"Legal filter flagged word '{word}' in message: {message}")
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate summary report of pipeline execution.
        
        Returns:
            Dictionary containing execution summary
        """
        self.metrics['end_time'] = datetime.now()
        duration = (self.metrics['end_time'] - self.metrics['start_time']).total_seconds()
        
        # Calculate derived metrics
        total_images = self.metrics['images_generated'] + self.metrics['images_reused']
        cache_hit_rate = (
            (self.metrics['images_reused'] / total_images * 100)
            if total_images > 0 else 0
        )
        
        api_success_rate = (
            ((self.metrics['api_calls'] - self.metrics['api_failures']) / 
             self.metrics['api_calls'] * 100)
            if self.metrics['api_calls'] > 0 else 100
        )
        
        compliance_pass_rate = (
            (self.metrics['compliance_passes'] / self.metrics['compliance_checks'] * 100)
            if self.metrics['compliance_checks'] > 0 else 0
        )
        
        report = {
            'execution_summary': {
                'start_time': self.metrics['start_time'].isoformat(),
                'end_time': self.metrics['end_time'].isoformat(),
                'duration_seconds': round(duration, 2),
                'total_products': self.metrics['total_products']
            },
            'image_generation': {
                'total_images': total_images,
                'images_generated': self.metrics['images_generated'],
                'images_reused': self.metrics['images_reused'],
                'cache_hit_rate_percent': round(cache_hit_rate, 2)
            },
            'api_performance': {
                'total_api_calls': self.metrics['api_calls'],
                'failed_calls': self.metrics['api_failures'],
                'success_rate_percent': round(api_success_rate, 2),
                'total_cost_usd': round(self.metrics['total_cost'], 4)
            },
            'compliance': {
                'total_checks': self.metrics['compliance_checks'],
                'passed': self.metrics['compliance_passes'],
                'pass_rate_percent': round(compliance_pass_rate, 2)
            },
            'legal_filtering': {
                'flags_raised': self.metrics['legal_flags']
            },
            'errors': self.metrics['errors']
        }
        
        return report
    
    def save_report(self, output_dir: Path) -> None:
        """
        Save detailed report to files.
        
        Args:
            output_dir: Directory to save reports
        """
        report = self.generate_summary_report()
        
        # Save JSON report
        json_report_path = output_dir / "execution_report.json"
        with open(json_report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save human-readable report
        text_report_path = output_dir / "execution_report.txt"
        with open(text_report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("CREATIVE AUTOMATION PIPELINE - EXECUTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("EXECUTION SUMMARY\n")
            f.write("-" * 80 + "\n")
            for key, value in report['execution_summary'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\nIMAGE GENERATION\n")
            f.write("-" * 80 + "\n")
            for key, value in report['image_generation'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\nAPI PERFORMANCE\n")
            f.write("-" * 80 + "\n")
            for key, value in report['api_performance'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\nCOMPLIANCE CHECKS\n")
            f.write("-" * 80 + "\n")
            for key, value in report['compliance'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\nLEGAL FILTERING\n")
            f.write("-" * 80 + "\n")
            f.write(f"Flags Raised: {report['legal_filtering']['flags_raised']}\n")
            
            if report['errors']:
                f.write("\nERRORS\n")
                f.write("-" * 80 + "\n")
                for error in report['errors']:
                    f.write(f"[{error['timestamp']}] {error['message']}\n")
                    if 'exception' in error:
                        f.write(f"  Exception: {error['exception']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        self.success(f"Reports saved to {output_dir}")
        
        # Print summary to console
        self._print_summary(report)
    
    def _print_summary(self, report: Dict[str, Any]) -> None:
        """Print summary report to console."""
        print("\n" + "=" * 80)
        print(f"{Fore.CYAN}EXECUTION SUMMARY{Style.RESET_ALL}")
        print("=" * 80)
        
        exec_summary = report['execution_summary']
        print(f"Duration: {exec_summary['duration_seconds']}s")
        print(f"Products Processed: {exec_summary['total_products']}")
        
        img_gen = report['image_generation']
        print(f"\nImages Generated: {img_gen['images_generated']}")
        print(f"Images Reused: {img_gen['images_reused']}")
        print(f"Cache Hit Rate: {img_gen['cache_hit_rate_percent']}%")
        
        api_perf = report['api_performance']
        print(f"\nAPI Calls: {api_perf['total_api_calls']}")
        print(f"Success Rate: {api_perf['success_rate_percent']}%")
        print(f"Total Cost: ${api_perf['total_cost_usd']:.4f}")
        
        compliance = report['compliance']
        print(f"\nCompliance Checks: {compliance['total_checks']}")
        print(f"Pass Rate: {compliance['pass_rate_percent']}%")
        
        print(f"\nLegal Flags: {report['legal_filtering']['flags_raised']}")
        
        if report['errors']:
            print(f"\n{Fore.RED}Errors: {len(report['errors'])}{Style.RESET_ALL}")
        
        print("=" * 80 + "\n")

