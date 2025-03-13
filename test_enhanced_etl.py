"""
Test script for the enhanced ETL pipeline with data quality monitoring.

This script tests the integration of enhanced data quality monitoring with the ETL pipeline
using real data from the ProHandel API.
"""
import os
import sys
import json
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sqlalchemy.orm import Session

from etl.enhanced_orchestrator import EnhancedETLOrchestrator
from etl.utils.database import get_db_session
from etl.utils.logger import logger

# Configure output directory
OUTPUT_DIR = "test_results/enhanced_etl"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def configure_data_quality():
    """
    Configure data quality monitoring for the ETL pipeline.
    
    Returns:
        dict: Data quality configuration
    """
    return {
        "output_dir": OUTPUT_DIR,
        "sampling": {
            "enabled": True,
            "min_data_size_for_sampling": 5000,
            "default_sample_size": 2000,
            "strategy": "outlier_biased",
            "outlier_fraction": 0.3,
            "outlier_method": "zscore",
            "outlier_threshold": 3.0
        },
        "monitors": {
            "completeness": {
                "min_completeness_ratio": 0.95,
                "severity": "warning"
            },
            "outlier": {
                "method": "zscore",
                "threshold": 3.0,
                "max_outlier_ratio": 0.05,
                "severity": "warning"
            },
            "consistency": {
                "max_violation_ratio": 0.05,
                "severity": "error"
            },
            "format": {
                "max_violation_ratio": 0.05,
                "severity": "error"
            },
            "freshness": {
                "severity": "warning"
            }
        }
    }


def visualize_quality_results(entity_name, results):
    """
    Visualize data quality results for an entity.
    
    Args:
        entity_name: Name of the entity
        results: Data quality results
    """
    if not results or "metrics" not in results:
        logger.warning(f"No metrics available for {entity_name}")
        return
    
    metrics = results.get("metrics", {})
    if not metrics:
        logger.warning(f"No metrics available for {entity_name}")
        return
    
    plt.figure(figsize=(15, 10))
    plt.suptitle(f"Data Quality Metrics for {entity_name}", fontsize=16)
    
    # Plot completeness metrics
    if "completeness" in metrics:
        plt.subplot(2, 2, 1)
        completeness_data = metrics["completeness"].get("column_completeness", {})
        if completeness_data:
            columns = list(completeness_data.keys())
            values = [data.get("completeness_ratio", 0) for data in completeness_data.values()]
            sns.barplot(x=columns, y=values)
            plt.title("Completeness Ratio by Column")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, 1.05)
    
    # Plot outlier metrics
    if "outlier" in metrics:
        plt.subplot(2, 2, 2)
        outlier_data = metrics["outlier"].get("column_metrics", {})
        if outlier_data:
            columns = list(outlier_data.keys())
            values = [data.get("outlier_ratio", 0) for data in outlier_data.values()]
            sns.barplot(x=columns, y=values)
            plt.title("Outlier Ratio by Column")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(values) * 1.2 if values else 0.1)
    
    # Plot format validation metrics
    if "format" in metrics:
        plt.subplot(2, 2, 3)
        format_data = metrics["format"].get("violation_ratios", {})
        if format_data:
            rules = list(format_data.keys())
            values = list(format_data.values())
            sns.barplot(x=rules, y=values)
            plt.title("Format Violation Ratio by Rule")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(values) * 1.2 if values else 0.1)
    
    # Plot freshness metrics
    if "freshness" in metrics:
        plt.subplot(2, 2, 4)
        freshness_data = metrics["freshness"].get("stale_ratios", {})
        if freshness_data:
            rules = list(freshness_data.keys())
            values = list(freshness_data.values())
            sns.barplot(x=rules, y=values)
            plt.title("Stale Data Ratio by Rule")
            plt.xticks(rotation=45, ha="right")
            plt.ylim(0, max(values) * 1.2 if values else 0.1)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{entity_name}_quality_metrics.png"))
    plt.close()
    
    logger.info(f"Saved quality visualization for {entity_name}")


def visualize_summary(results):
    """
    Visualize summary of data quality results across all entities.
    
    Args:
        results: ETL results with data quality information
    """
    # Extract alert counts by entity and severity
    entities = []
    error_counts = []
    warning_counts = []
    info_counts = []
    
    for entity, result in results.items():
        if "quality_results" not in result:
            continue
        
        quality_results = result["quality_results"]
        alerts = quality_results.get("all_alerts", [])
        
        entities.append(entity)
        error_count = len([a for a in alerts if a.get("severity") in ["error", "critical"]])
        warning_count = len([a for a in alerts if a.get("severity") == "warning"])
        info_count = len([a for a in alerts if a.get("severity") == "info"])
        
        error_counts.append(error_count)
        warning_counts.append(warning_count)
        info_counts.append(info_count)
    
    if not entities:
        logger.warning("No entities with quality results to visualize")
        return
    
    # Create stacked bar chart
    plt.figure(figsize=(12, 8))
    
    bar_width = 0.6
    indices = range(len(entities))
    
    p1 = plt.bar(indices, info_counts, bar_width, label='Info', color='green')
    p2 = plt.bar(indices, warning_counts, bar_width, bottom=info_counts, label='Warning', color='orange')
    p3 = plt.bar(indices, error_counts, bar_width, bottom=[i+w for i, w in zip(info_counts, warning_counts)], label='Error', color='red')
    
    plt.xlabel('Entity')
    plt.ylabel('Number of Alerts')
    plt.title('Data Quality Alerts by Entity and Severity')
    plt.xticks(indices, entities, rotation=45, ha="right")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "quality_summary.png"))
    plt.close()
    
    logger.info("Saved quality summary visualization")


def main():
    """Main function to test the enhanced ETL pipeline."""
    logger.info("Starting enhanced ETL pipeline test")
    
    # Configure data quality
    dq_config = configure_data_quality()
    
    # Get database session
    db_session = get_db_session()
    
    try:
        # Initialize enhanced ETL orchestrator
        orchestrator = EnhancedETLOrchestrator(
            db_session=db_session,
            incremental=True,
            data_quality_config=dq_config
        )
        
        # Define entities to process (use a subset for testing)
        test_entities = ["article", "customer", "inventory"]
        
        # Run ETL with data quality monitoring
        logger.info(f"Running enhanced ETL for entities: {test_entities}")
        results = orchestrator.run_etl(entities=test_entities, force=True)
        
        # Save results to file
        with open(os.path.join(OUTPUT_DIR, "etl_results.json"), "w") as f:
            # Convert to serializable format
            serializable_results = {}
            for entity, result in results.items():
                serializable_results[entity] = {
                    k: v for k, v in result.items() 
                    if k != "quality_results"  # Skip quality_results as it's saved separately
                }
            json.dump(serializable_results, f, indent=2)
        
        # Visualize quality results for each entity
        for entity in test_entities:
            if entity in results and "quality_results" in results[entity]:
                visualize_quality_results(entity, results[entity]["quality_results"])
        
        # Visualize summary
        visualize_summary(results)
        
        # Get quality summary
        quality_summary = orchestrator.get_quality_summary()
        
        # Save quality summary
        with open(os.path.join(OUTPUT_DIR, "quality_summary.json"), "w") as f:
            json.dump(quality_summary, f, indent=2)
        
        # Print summary
        logger.info("Enhanced ETL test completed")
        logger.info(f"Quality status: {quality_summary.get('quality_status', 'unknown')}")
        logger.info(f"Total alerts: {quality_summary.get('total_alerts', 0)}")
        
        if "alerts_by_severity" in quality_summary:
            for severity, count in quality_summary["alerts_by_severity"].items():
                logger.info(f"  {severity.upper()}: {count} alerts")
    
    except Exception as e:
        logger.error(f"Error in enhanced ETL test: {e}")
        raise
    
    finally:
        # Close database session
        db_session.close()


if __name__ == "__main__":
    main()
