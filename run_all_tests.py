#!/usr/bin/env python
"""
Comprehensive test runner script for the ProHandel API integration.
This script will run all tests in sequence:
1. Test all API endpoints and validate data against schemas
2. Test the Lambda function locally
3. Test the Lambda function in AWS (if deployed)
"""

import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"all_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def run_command(command: List[str], cwd: Optional[str] = None) -> int:
    """
    Run a command and return the exit code.
    
    Args:
        command: Command to run as a list of strings
        cwd: Working directory for the command
        
    Returns:
        Exit code of the command
    """
    logger.info(f"Running command: {' '.join(command)}")
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line, end='')
        
        # Wait for process to complete
        exit_code = process.wait()
        
        if exit_code != 0:
            logger.error(f"Command failed with exit code {exit_code}")
            for line in process.stderr:
                logger.error(line.strip())
        
        return exit_code
    
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return 1

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run all tests for ProHandel API integration')
    parser.add_argument('--skip-endpoints', action='store_true',
                        help='Skip testing API endpoints')
    parser.add_argument('--skip-local-lambda', action='store_true',
                        help='Skip testing Lambda function locally')
    parser.add_argument('--skip-aws-lambda', action='store_true',
                        help='Skip testing Lambda function in AWS')
    parser.add_argument('--entity', type=str,
                        help='Specific entity to test (default: all)')
    parser.add_argument('--limit', type=int, default=10,
                        help='Maximum number of records to fetch per entity')
    parser.add_argument('--function-name', type=str, default="prohandel-fivetran-connector",
                        help='Name of the Lambda function in AWS')
    parser.add_argument('--region', type=str, default="eu-central-1",
                        help='AWS region')
    return parser.parse_args()

def main():
    """Main function to run all tests."""
    args = parse_args()
    
    # Check if API credentials are provided
    if not os.environ.get("PROHANDEL_API_KEY") or not os.environ.get("PROHANDEL_API_SECRET"):
        logger.error("API key and secret are required. Set them as environment variables.")
        sys.exit(1)
    
    # Create reports directory
    reports_dir = Path("test_reports")
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Track test results
    results = {
        "endpoints": None,
        "local_lambda": None,
        "aws_lambda": None
    }
    
    # Test API endpoints
    if not args.skip_endpoints:
        logger.info("=== Testing API Endpoints ===")
        
        endpoint_report = reports_dir / f"endpoint_test_results_{timestamp}.json"
        
        cmd = [
            sys.executable,
            "test_endpoints.py",
            "--output", str(endpoint_report)
        ]
        
        if args.entity:
            cmd.extend(["--entity", args.entity])
        
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        
        exit_code = run_command(cmd)
        results["endpoints"] = exit_code == 0
    else:
        logger.info("Skipping API endpoint tests")
    
    # Test Lambda function locally
    if not args.skip_local_lambda:
        logger.info("=== Testing Lambda Function Locally ===")
        
        local_lambda_report = reports_dir / f"local_lambda_test_results_{timestamp}.json"
        
        cmd = [
            sys.executable,
            "lambda_connector/local_fivetran_test.py",
            "--output", str(local_lambda_report)
        ]
        
        if args.entity:
            cmd.extend(["--entity", args.entity])
        
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        
        exit_code = run_command(cmd)
        results["local_lambda"] = exit_code == 0
    else:
        logger.info("Skipping local Lambda function tests")
    
    # Test Lambda function in AWS
    if not args.skip_aws_lambda:
        logger.info("=== Testing Lambda Function in AWS ===")
        
        # Check if AWS CLI is configured
        aws_check = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if aws_check.returncode != 0:
            logger.error("AWS CLI is not configured or credentials are invalid. Skipping AWS Lambda tests.")
            results["aws_lambda"] = False
        else:
            aws_lambda_report = reports_dir / f"aws_lambda_test_results_{timestamp}.json"
            
            cmd = [
                sys.executable,
                "lambda_connector/test_lambda_fivetran.py",
                "--function-name", args.function_name,
                "--region", args.region,
                "--output", str(aws_lambda_report)
            ]
            
            if args.entity:
                cmd.extend(["--entity", args.entity])
            
            if args.limit:
                cmd.extend(["--limit", str(args.limit)])
            
            exit_code = run_command(cmd)
            results["aws_lambda"] = exit_code == 0
    else:
        logger.info("Skipping AWS Lambda function tests")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, success in results.items():
        if success is None:
            status = "SKIPPED"
        elif success:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("=" * 80)
    
    # Determine overall success
    executed_tests = [result for result in results.values() if result is not None]
    if not executed_tests:
        logger.warning("No tests were executed")
        sys.exit(0)
    
    if all(executed_tests):
        logger.info("All tests passed successfully")
        sys.exit(0)
    else:
        logger.error("Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
