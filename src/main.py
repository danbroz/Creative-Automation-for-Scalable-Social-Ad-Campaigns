"""
Main Pipeline Orchestrator
CLI application that coordinates all pipeline components.
"""

import argparse
import sys
import time
from pathlib import Path
from colorama import Fore, Style, init

from .logger import PipelineLogger
from .brief_parser import BriefParser
from .content_filter import ContentFilter
from .asset_manager import AssetManager
from .image_generator import ImageGenerator
from .image_processor import ImageProcessor
from .compliance_checker import ComplianceChecker
from .output_formatter import OutputFormatter
from .performance_monitor import PerformanceMonitor

# Initialize colorama
init(autoreset=True)


class CreativeAutomationPipeline:
    """Main pipeline orchestrator for creative automation."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize pipeline.
        
        Args:
            verbose: Enable verbose logging
        """
        self.logger = PipelineLogger()
        self.verbose = verbose
        
        # Initialize components
        try:
            self.content_filter = ContentFilter()
            self.asset_manager = AssetManager()
            self.image_generator = ImageGenerator()
            self.image_processor = ImageProcessor()
            self.compliance_checker = ComplianceChecker()
            self.output_formatter = OutputFormatter()
            self.performance_monitor = PerformanceMonitor()
            
        except Exception as e:
            self.logger.error("Failed to initialize pipeline components", e)
            raise
    
    def run(self, brief_path: str) -> bool:
        """
        Run the creative automation pipeline.
        
        Args:
            brief_path: Path to campaign brief JSON file
            
        Returns:
            True if pipeline completed successfully
        """
        self.logger.info("=" * 80)
        self.logger.info("CREATIVE AUTOMATION PIPELINE")
        self.logger.info("=" * 80)
        
        self.performance_monitor.start_timer()
        
        try:
            # Step 1: Parse and validate campaign brief
            self.logger.info("\n[1/7] Parsing campaign brief...")
            brief = self._parse_brief(brief_path)
            if not brief:
                return False
            
            # Step 2: Filter campaign message for legal compliance
            self.logger.info("\n[2/7] Checking legal compliance...")
            if not self._check_legal_compliance(brief):
                self.logger.warning("Legal compliance issues found (continuing with warnings)")
            
            # Step 3: Setup output structure
            self.logger.info("\n[3/7] Setting up output structure...")
            campaign_dir = self.output_formatter.create_campaign_directory(brief.campaign_name)
            self.logger.success(f"Output directory: {campaign_dir}")
            
            # Step 4: Process each product
            self.logger.info(f"\n[4/7] Processing {len(brief.products)} products...")
            self.logger.metrics['total_products'] = len(brief.products)
            
            for idx, product in enumerate(brief.products, 1):
                self.logger.info(f"\n  Processing product {idx}/{len(brief.products)}: {product['name']}")
                self._process_product(product, brief, campaign_dir)
            
            # Step 5: Generate reports
            self.logger.info("\n[5/7] Generating reports...")
            self._generate_reports(campaign_dir, brief)
            
            # Step 6: Save execution summary
            self.logger.info("\n[6/7] Saving execution summary...")
            self.performance_monitor.stop_timer()
            self.logger.save_report(campaign_dir)
            
            # Step 7: Display summary
            self.logger.info("\n[7/7] Pipeline execution complete!")
            self.logger.success(f"All outputs saved to: {campaign_dir}")
            
            return True
            
        except Exception as e:
            self.logger.error("Pipeline execution failed", e)
            self.performance_monitor.stop_timer()
            return False
    
    def _parse_brief(self, brief_path: str):
        """Parse and validate campaign brief."""
        try:
            brief = BriefParser.parse_file(brief_path)
            self.logger.success(f"Campaign: {brief.campaign_name}")
            self.logger.info(f"Products: {len(brief.products)}")
            self.logger.info(f"Target: {brief.target_region} - {brief.target_audience}")
            return brief
        except Exception as e:
            self.logger.error(f"Failed to parse brief: {brief_path}", e)
            return None
    
    def _check_legal_compliance(self, brief) -> bool:
        """Check campaign message for legal compliance."""
        # Check campaign message
        message_result = self.content_filter.filter_and_suggest(brief.campaign_message)
        
        # Check product names and descriptions
        product_violations = []
        for product in brief.products:
            name_result = self.content_filter.filter_and_suggest(product.get('name', ''))
            desc_result = self.content_filter.filter_and_suggest(product.get('description', ''))
            
            if not name_result['is_compliant']:
                product_violations.extend(name_result['violations'])
            if not desc_result['is_compliant']:
                product_violations.extend(desc_result['violations'])
        
        # Combine all violations
        all_violations = message_result['violations'] + product_violations
        total_violations = len(all_violations)
        
        if total_violations == 0:
            self.logger.success("Campaign content passed legal compliance check")
            return True
        else:
            self.logger.warning(f"Found {total_violations} compliance issue(s)")
            
            for violation in all_violations:
                self.logger.track_legal_flag(violation['word'], brief.campaign_message)
                self.logger.warning(f"  - '{violation['word']}' detected in context: '{violation['context']}'")
                self.logger.info(f"    Suggestions: {', '.join(violation['suggestions'])}")
            
            # For now, continue with warnings but log the issues
            self.logger.warning("Continuing with campaign generation but compliance issues noted")
            return True  # Changed to True to allow generation but with warnings
    
    def _process_product(self, product: dict, brief, campaign_dir: Path) -> None:
        """Process a single product through the pipeline."""
        product_name = product['name']
        product_desc = product.get('description', '')
        
        # Create product directory
        product_dir = self.output_formatter.create_product_directory(campaign_dir, product_name)
        
        try:
            # Check if asset exists
            asset_path = self.asset_manager.get_asset_path(product_name)
            
            if asset_path:
                self.logger.track_image_reused(product_name)
                self.asset_manager.register_asset(product_name, asset_path, source='existing')
            else:
                # Generate new image
                self.logger.info(f"    Generating image for {product_name}...")
                
                start_time = time.time()
                asset_path, gen_time, cost = self.image_generator.generate_image(
                    product_name,
                    product_desc
                )
                api_duration = time.time() - start_time
                
                # Track performance
                self.performance_monitor.track_api_call(
                    endpoint='dall-e-3',
                    duration=api_duration,
                    success=True,
                    cost=cost
                )
                
                self.logger.track_image_generated(product_name, cost)
                self.asset_manager.register_asset(product_name, asset_path, source='generated', cost=cost)
            
            # Process image for all aspect ratios
            self.logger.info(f"    Creating variants for 3 aspect ratios...")
            processed_images = self.image_processor.process_image(
                asset_path,
                brief.campaign_message,
                product_dir,
                product_name
            )
            
            self.logger.success(f"    Created {len(processed_images)} variants")
            
            # Run compliance checks on first variant
            self.logger.info(f"    Running compliance checks...")
            compliance_result = self.compliance_checker.check_compliance(processed_images[0])
            
            self.logger.track_compliance_check(
                compliance_result['compliant'],
                product_name
            )
            
            if compliance_result['compliant']:
                self.logger.success(f"    Compliance score: {compliance_result['score']}")
            else:
                self.logger.warning(f"    Compliance score: {compliance_result['score']}")
                for rec in compliance_result['recommendations']:
                    self.logger.info(f"      - {rec}")
            
            # Save metadata
            for img_path in processed_images:
                metadata = {
                    'product_name': product_name,
                    'campaign_name': brief.campaign_name,
                    'aspect_ratio': img_path.parent.name,
                    'compliance': compliance_result,
                    'source_asset': str(asset_path)
                }
                self.output_formatter.save_asset_metadata(img_path, metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to process product: {product_name}", e)
            self.performance_monitor.track_api_call(
                endpoint='product_processing',
                duration=0,
                success=False,
                error=str(e)
            )
    
    def _generate_reports(self, campaign_dir: Path, brief) -> None:
        """Generate campaign reports."""
        try:
            # Asset summary
            asset_summary = self.asset_manager.get_assets_summary()
            
            # Performance stats
            perf_report = self.performance_monitor.get_performance_report()
            
            campaign_data = {
                'campaign_name': brief.campaign_name,
                'products': [p['name'] for p in brief.products],
                'target_region': brief.target_region,
                'target_audience': brief.target_audience,
                'campaign_message': brief.campaign_message,
                'assets_generated': asset_summary['generated'],
                'compliance_checks': {
                    'total': self.logger.metrics['compliance_checks'],
                    'passed': self.logger.metrics['compliance_passes']
                },
                'legal_checks': {
                    'flags': self.logger.metrics['legal_flags']
                },
                'performance': perf_report
            }
            
            self.output_formatter.generate_campaign_summary(campaign_dir, campaign_data)
            self.logger.success("Campaign summary generated")
            
        except Exception as e:
            self.logger.error("Failed to generate reports", e)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Creative Automation Pipeline - Generate social media ad assets at scale',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s examples/campaign_brief_1.json
  %(prog)s my_campaign.json --verbose

For more information, see README.md
        """
    )
    
    parser.add_argument(
        'brief',
        help='Path to campaign brief JSON file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Creative Automation Pipeline v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Check if brief file exists
    if not Path(args.brief).exists():
        print(f"{Fore.RED}Error: Brief file not found: {args.brief}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Run pipeline
    pipeline = CreativeAutomationPipeline(verbose=args.verbose)
    success = pipeline.run(args.brief)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

