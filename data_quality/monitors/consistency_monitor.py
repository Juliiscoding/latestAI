"""
Consistency monitor for data quality monitoring.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np

from data_quality.base_monitor import BaseDataQualityMonitor


class ConsistencyMonitor(BaseDataQualityMonitor):
    """
    Monitor for checking data consistency.
    
    This monitor checks for consistency issues in the data, such as:
    - Duplicate records
    - Inconsistent values in related columns
    - Constraint violations
    """
    
    def __init__(self, name: str = "Consistency Monitor", 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the consistency monitor.
        
        Args:
            name (str): Name of the monitor
            config (Dict[str, Any], optional): Configuration parameters for the monitor
                - duplicate_columns (List[str]): Columns to check for duplicates
                - unique_columns (List[str]): Columns that should have unique values
                - related_columns (Dict[str, List[str]]): Columns that should be consistent
                - constraints (List[Dict]): List of constraints to check
                - max_duplicate_ratio (float): Maximum allowed ratio of duplicates (default: 0.01)
                - severity (str): Alert severity (default: 'warning')
        """
        super().__init__(name, config)
        self.duplicate_columns = self.config.get('duplicate_columns', [])
        self.unique_columns = self.config.get('unique_columns', [])
        self.related_columns = self.config.get('related_columns', {})
        self.constraints = self.config.get('constraints', [])
        self.max_duplicate_ratio = self.config.get('max_duplicate_ratio', 0.01)
        self.severity = self.config.get('severity', 'warning')
    
    def check_duplicates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for duplicate records in the data.
        
        Args:
            data (pd.DataFrame): Data to check
            
        Returns:
            Dict[str, Any]: Duplicate check results
        """
        results = {}
        
        # Check for duplicates in specified columns
        if self.duplicate_columns:
            duplicates = data.duplicated(subset=self.duplicate_columns, keep=False)
            duplicate_count = duplicates.sum()
            duplicate_ratio = duplicate_count / len(data) if len(data) > 0 else 0.0
            
            results['duplicate_records'] = {
                'columns': self.duplicate_columns,
                'duplicate_count': int(duplicate_count),
                'total_count': int(len(data)),
                'duplicate_ratio': float(duplicate_ratio),
                'duplicate_indices': duplicates[duplicates].index.tolist()
            }
            
            # Check threshold
            self.check_threshold(
                "duplicate_ratio", 
                duplicate_ratio, 
                self.max_duplicate_ratio, 
                'gt',  # Alert if duplicate ratio is greater than threshold
                self.severity
            )
        
        # Check for uniqueness in specified columns
        for column in self.unique_columns:
            if column in data.columns:
                value_counts = data[column].value_counts()
                duplicates = value_counts[value_counts > 1]
                duplicate_count = (value_counts[value_counts > 1] - 1).sum()
                duplicate_ratio = duplicate_count / len(data) if len(data) > 0 else 0.0
                
                results[f"{column}_uniqueness"] = {
                    'duplicate_count': int(duplicate_count),
                    'total_count': int(len(data)),
                    'duplicate_ratio': float(duplicate_ratio),
                    'duplicate_values': duplicates.index.tolist()
                }
                
                # Check threshold
                self.check_threshold(
                    f"{column}_duplicate_ratio", 
                    duplicate_ratio, 
                    self.max_duplicate_ratio, 
                    'gt',
                    self.severity
                )
        
        return results
    
    def check_related_columns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for consistency in related columns.
        
        Args:
            data (pd.DataFrame): Data to check
            
        Returns:
            Dict[str, Any]: Consistency check results
        """
        results = {}
        
        for primary_column, related_columns in self.related_columns.items():
            if primary_column in data.columns:
                for related_column in related_columns:
                    if related_column in data.columns:
                        # Group by primary column and check if related column has consistent values
                        grouped = data.groupby(primary_column)[related_column]
                        inconsistent_groups = grouped.nunique()[grouped.nunique() > 1]
                        
                        inconsistent_count = len(inconsistent_groups)
                        inconsistent_ratio = inconsistent_count / len(grouped) if len(grouped) > 0 else 0.0
                        
                        results[f"{primary_column}_{related_column}_consistency"] = {
                            'inconsistent_count': int(inconsistent_count),
                            'total_count': int(len(grouped)),
                            'inconsistent_ratio': float(inconsistent_ratio),
                            'inconsistent_values': inconsistent_groups.index.tolist()
                        }
                        
                        # Check threshold
                        self.check_threshold(
                            f"{primary_column}_{related_column}_inconsistent_ratio", 
                            inconsistent_ratio, 
                            0.0,  # No inconsistencies allowed
                            'gt',
                            self.severity
                        )
        
        return results
    
    def check_constraints(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for constraint violations in the data.
        
        Args:
            data (pd.DataFrame): Data to check
            
        Returns:
            Dict[str, Any]: Constraint check results
        """
        results = {}
        
        for constraint in self.constraints:
            constraint_name = constraint.get('name', 'unnamed_constraint')
            constraint_type = constraint.get('type', '')
            columns = constraint.get('columns', [])
            
            if constraint_type == 'range':
                # Range constraint
                column = columns[0] if columns else ''
                min_value = constraint.get('min_value', float('-inf'))
                max_value = constraint.get('max_value', float('inf'))
                
                if column in data.columns:
                    violations = (data[column] < min_value) | (data[column] > max_value)
                    violation_count = violations.sum()
                    violation_ratio = violation_count / len(data) if len(data) > 0 else 0.0
                    
                    results[f"{constraint_name}_violations"] = {
                        'constraint_type': 'range',
                        'column': column,
                        'min_value': min_value,
                        'max_value': max_value,
                        'violation_count': int(violation_count),
                        'total_count': int(len(data)),
                        'violation_ratio': float(violation_ratio),
                        'violation_indices': violations[violations].index.tolist()
                    }
                    
                    # Check threshold
                    self.check_threshold(
                        f"{constraint_name}_violation_ratio", 
                        violation_ratio, 
                        0.0,  # No violations allowed
                        'gt',
                        self.severity
                    )
            
            elif constraint_type == 'comparison':
                # Comparison constraint
                if len(columns) >= 2:
                    column1 = columns[0]
                    column2 = columns[1]
                    operator = constraint.get('operator', '==')
                    
                    if column1 in data.columns and column2 in data.columns:
                        if operator == '==':
                            violations = data[column1] != data[column2]
                        elif operator == '!=':
                            violations = data[column1] == data[column2]
                        elif operator == '<':
                            violations = data[column1] >= data[column2]
                        elif operator == '<=':
                            violations = data[column1] > data[column2]
                        elif operator == '>':
                            violations = data[column1] <= data[column2]
                        elif operator == '>=':
                            violations = data[column1] < data[column2]
                        else:
                            violations = pd.Series(False, index=data.index)
                        
                        violation_count = violations.sum()
                        violation_ratio = violation_count / len(data) if len(data) > 0 else 0.0
                        
                        results[f"{constraint_name}_violations"] = {
                            'constraint_type': 'comparison',
                            'column1': column1,
                            'column2': column2,
                            'operator': operator,
                            'violation_count': int(violation_count),
                            'total_count': int(len(data)),
                            'violation_ratio': float(violation_ratio),
                            'violation_indices': violations[violations].index.tolist()
                        }
                        
                        # Check threshold
                        self.check_threshold(
                            f"{constraint_name}_violation_ratio", 
                            violation_ratio, 
                            0.0,  # No violations allowed
                            'gt',
                            self.severity
                        )
        
        return results
    
    def run(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Run the consistency monitor on the provided data.
        
        Args:
            data (pd.DataFrame): Data to monitor
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        # Check for duplicates
        duplicate_results = self.check_duplicates(data)
        
        # Check for consistency in related columns
        related_results = self.check_related_columns(data)
        
        # Check for constraint violations
        constraint_results = self.check_constraints(data)
        
        # Store metrics
        self.metrics = {
            'duplicates': duplicate_results,
            'related_columns': related_results,
            'constraints': constraint_results
        }
        
        self.last_run = pd.Timestamp.now()
        
        return self.metrics
