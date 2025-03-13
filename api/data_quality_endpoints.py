"""
API endpoints for data quality monitoring.

This module provides API endpoints for accessing data quality metrics and alerts
from the Mercurios.ai dashboard.
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from etl.utils.database import get_db_session
from etl.enhanced_orchestrator import EnhancedETLOrchestrator

# Create router
router = APIRouter(
    prefix="/api/data-quality",
    tags=["data-quality"],
    responses={404: {"description": "Not found"}},
)


@router.get("/summary")
async def get_data_quality_summary(
    db: Session = Depends(get_db_session),
    days: int = Query(7, description="Number of days to include in the summary")
):
    """
    Get a summary of data quality metrics across all entities.
    
    Args:
        db: Database session
        days: Number of days to include in the summary
        
    Returns:
        dict: Data quality summary
    """
    try:
        # Initialize orchestrator
        orchestrator = EnhancedETLOrchestrator(db_session=db)
        
        # Get quality summary
        summary = orchestrator.get_quality_summary(days=days)
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data quality summary: {str(e)}")


@router.get("/entities/{entity_name}")
async def get_entity_quality_metrics(
    entity_name: str,
    db: Session = Depends(get_db_session),
    days: int = Query(7, description="Number of days to include in the metrics")
):
    """
    Get data quality metrics for a specific entity.
    
    Args:
        entity_name: Name of the entity
        db: Database session
        days: Number of days to include in the metrics
        
    Returns:
        dict: Entity data quality metrics
    """
    try:
        # Initialize orchestrator
        orchestrator = EnhancedETLOrchestrator(db_session=db)
        
        # Get entity quality metrics
        metrics = orchestrator.get_entity_quality_metrics(entity_name, days=days)
        
        if not metrics:
            raise HTTPException(status_code=404, detail=f"No data quality metrics found for entity: {entity_name}")
        
        return metrics
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data quality metrics for entity {entity_name}: {str(e)}")


@router.get("/alerts")
async def get_data_quality_alerts(
    db: Session = Depends(get_db_session),
    entity: Optional[str] = None,
    severity: Optional[str] = None,
    days: int = Query(7, description="Number of days to include in the alerts"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    Get data quality alerts.
    
    Args:
        db: Database session
        entity: Optional entity name to filter alerts
        severity: Optional severity level to filter alerts (info, warning, error, critical)
        days: Number of days to include in the alerts
        limit: Maximum number of alerts to return
        offset: Offset for pagination
        
    Returns:
        dict: Data quality alerts
    """
    try:
        # Initialize orchestrator
        orchestrator = EnhancedETLOrchestrator(db_session=db)
        
        # Get alerts
        alerts = orchestrator.get_quality_alerts(
            entity=entity,
            severity=severity,
            days=days,
            limit=limit,
            offset=offset
        )
        
        return {
            "total": alerts.get("total", 0),
            "alerts": alerts.get("alerts", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data quality alerts: {str(e)}")


@router.get("/trends")
async def get_data_quality_trends(
    db: Session = Depends(get_db_session),
    entity: Optional[str] = None,
    days: int = Query(30, description="Number of days to include in the trends")
):
    """
    Get data quality trends over time.
    
    Args:
        db: Database session
        entity: Optional entity name to filter trends
        days: Number of days to include in the trends
        
    Returns:
        dict: Data quality trends
    """
    try:
        # Initialize orchestrator
        orchestrator = EnhancedETLOrchestrator(db_session=db)
        
        # Get trends
        trends = orchestrator.get_quality_trends(entity=entity, days=days)
        
        return trends
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data quality trends: {str(e)}")


@router.post("/run-check/{entity_name}")
async def run_data_quality_check(
    entity_name: str,
    db: Session = Depends(get_db_session),
    force: bool = Query(False, description="Force data extraction even if not incremental")
):
    """
    Run a data quality check for a specific entity.
    
    Args:
        entity_name: Name of the entity
        db: Database session
        force: Force data extraction even if not incremental
        
    Returns:
        dict: Data quality check results
    """
    try:
        # Initialize orchestrator
        orchestrator = EnhancedETLOrchestrator(db_session=db)
        
        # Run ETL with data quality check for the entity
        results = orchestrator.run_etl(entities=[entity_name], force=force)
        
        if entity_name not in results:
            raise HTTPException(status_code=404, detail=f"No results found for entity: {entity_name}")
        
        entity_results = results[entity_name]
        
        # Extract quality results
        quality_results = entity_results.get("quality_results", {})
        
        return {
            "entity": entity_name,
            "quality_status": quality_results.get("quality_status", "unknown"),
            "total_alerts": len(quality_results.get("all_alerts", [])),
            "metrics": quality_results.get("metrics", {}),
            "alerts": quality_results.get("all_alerts", [])
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running data quality check for entity {entity_name}: {str(e)}")
