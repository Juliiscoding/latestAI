"""
Data sampling strategies for data quality monitoring.

This module provides sampling strategies to optimize performance
for data quality monitoring on large datasets.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataSampler:
    """
    Provides sampling strategies for data quality monitoring.
    
    This class implements various sampling strategies to optimize
    performance for data quality monitoring on large datasets.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DataSampler.
        
        Args:
            config: Configuration dictionary with sampling parameters
        """
        self.config = config or {}
        self.default_sample_size = self.config.get("default_sample_size", 100000)
        self.default_random_state = self.config.get("random_state", 42)
        self.min_data_size_for_sampling = self.config.get("min_data_size_for_sampling", 10000)
        self.stratify_columns = self.config.get("stratify_columns", None)
    
    def should_sample(self, data: pd.DataFrame) -> bool:
        """
        Determine if sampling should be applied based on data size.
        
        Args:
            data: Input DataFrame
            
        Returns:
            bool: True if sampling should be applied
        """
        return len(data) >= self.min_data_size_for_sampling
    
    def random_sample(
        self, 
        data: pd.DataFrame, 
        sample_size: Optional[int] = None,
        random_state: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Take a random sample of the data.
        
        Args:
            data: Input DataFrame
            sample_size: Number of rows to sample (default: self.default_sample_size)
            random_state: Random state for reproducibility
            
        Returns:
            pd.DataFrame: Sampled DataFrame
        """
        if not self.should_sample(data):
            logger.info(f"Data size ({len(data)} rows) below sampling threshold, using full dataset")
            return data
        
        sample_size = sample_size or self.default_sample_size
        random_state = random_state or self.default_random_state
        
        # Ensure sample size is not larger than data size
        sample_size = min(sample_size, len(data))
        
        logger.info(f"Taking random sample of {sample_size} rows from {len(data)} total rows")
        return data.sample(sample_size, random_state=random_state)
    
    def stratified_sample(
        self, 
        data: pd.DataFrame, 
        stratify_columns: Optional[List[str]] = None,
        sample_size: Optional[int] = None,
        random_state: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Take a stratified sample of the data based on specified columns.
        
        Args:
            data: Input DataFrame
            stratify_columns: Columns to stratify by
            sample_size: Number of rows to sample (default: self.default_sample_size)
            random_state: Random state for reproducibility
            
        Returns:
            pd.DataFrame: Sampled DataFrame
        """
        if not self.should_sample(data):
            logger.info(f"Data size ({len(data)} rows) below sampling threshold, using full dataset")
            return data
        
        stratify_columns = stratify_columns or self.stratify_columns
        if not stratify_columns:
            logger.info("No stratify columns specified, falling back to random sampling")
            return self.random_sample(data, sample_size, random_state)
        
        # Ensure all stratify columns exist in the data
        valid_columns = [col for col in stratify_columns if col in data.columns]
        if not valid_columns:
            logger.warning("None of the specified stratify columns exist in the data, falling back to random sampling")
            return self.random_sample(data, sample_size, random_state)
        
        sample_size = sample_size or self.default_sample_size
        random_state = random_state or self.default_random_state
        
        # Ensure sample size is not larger than data size
        sample_size = min(sample_size, len(data))
        
        # Create stratification key
        if len(valid_columns) == 1:
            strata = data[valid_columns[0]]
        else:
            # Combine multiple columns into a single stratification key
            strata = data[valid_columns].apply(lambda x: '_'.join(x.astype(str)), axis=1)
        
        # Count occurrences of each stratum
        strata_counts = strata.value_counts()
        
        # Calculate sampling fraction for each stratum
        total_rows = len(data)
        sampling_fraction = sample_size / total_rows
        
        # Initialize empty DataFrame for the sample
        sampled_data = pd.DataFrame()
        
        # Sample from each stratum
        for stratum, count in strata_counts.items():
            # Calculate number of rows to sample from this stratum
            stratum_sample_size = max(1, int(count * sampling_fraction))
            
            # Get rows for this stratum
            if len(valid_columns) == 1:
                stratum_data = data[data[valid_columns[0]] == stratum]
            else:
                stratum_data = data[strata == stratum]
            
            # Sample from this stratum
            stratum_sample = stratum_data.sample(
                min(stratum_sample_size, len(stratum_data)),
                random_state=random_state
            )
            
            # Add to the sample
            sampled_data = pd.concat([sampled_data, stratum_sample])
        
        logger.info(f"Taking stratified sample of {len(sampled_data)} rows from {len(data)} total rows")
        return sampled_data
    
    def outlier_biased_sample(
        self, 
        data: pd.DataFrame, 
        numerical_columns: Optional[List[str]] = None,
        outlier_fraction: float = 0.5,
        sample_size: Optional[int] = None,
        random_state: Optional[int] = None,
        method: str = "zscore",
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Take a sample biased towards outliers in numerical columns.
        
        This sampling strategy ensures that outliers are well-represented
        in the sample, which is useful for data quality monitoring.
        
        Args:
            data: Input DataFrame
            numerical_columns: Numerical columns to check for outliers
            outlier_fraction: Fraction of the sample to allocate to outliers
            sample_size: Number of rows to sample (default: self.default_sample_size)
            random_state: Random state for reproducibility
            method: Outlier detection method ('zscore', 'iqr')
            threshold: Threshold for outlier detection
            
        Returns:
            pd.DataFrame: Sampled DataFrame
        """
        if not self.should_sample(data):
            logger.info(f"Data size ({len(data)} rows) below sampling threshold, using full dataset")
            return data
        
        sample_size = sample_size or self.default_sample_size
        random_state = random_state or self.default_random_state
        
        # Ensure sample size is not larger than data size
        sample_size = min(sample_size, len(data))
        
        # Identify numerical columns if not specified
        if numerical_columns is None:
            numerical_columns = data.select_dtypes(include=np.number).columns.tolist()
        
        if not numerical_columns:
            logger.warning("No numerical columns found for outlier detection, falling back to random sampling")
            return self.random_sample(data, sample_size, random_state)
        
        # Detect outliers
        outlier_mask = pd.Series(False, index=data.index)
        
        for column in numerical_columns:
            if column not in data.columns:
                continue
                
            # Skip columns with all missing values
            if data[column].isna().all():
                continue
            
            column_data = data[column].dropna()
            
            if method == "zscore":
                # Z-score method
                mean = column_data.mean()
                std = column_data.std()
                
                if std == 0:
                    continue
                    
                z_scores = (column_data - mean) / std
                column_outliers = data.index[data[column].notna() & (z_scores.abs() > threshold)]
                
            elif method == "iqr":
                # IQR method
                q1 = column_data.quantile(0.25)
                q3 = column_data.quantile(0.75)
                iqr = q3 - q1
                
                if iqr == 0:
                    continue
                    
                lower_bound = q1 - threshold * iqr
                upper_bound = q3 + threshold * iqr
                
                column_outliers = data.index[
                    data[column].notna() & 
                    ((data[column] < lower_bound) | (data[column] > upper_bound))
                ]
            
            else:
                logger.warning(f"Unknown outlier detection method: {method}, falling back to random sampling")
                return self.random_sample(data, sample_size, random_state)
            
            outlier_mask = outlier_mask | data.index.isin(column_outliers)
        
        # Split data into outliers and non-outliers
        outliers = data[outlier_mask]
        non_outliers = data[~outlier_mask]
        
        logger.info(f"Detected {len(outliers)} outliers out of {len(data)} total rows")
        
        # Calculate sample sizes for outliers and non-outliers
        outlier_sample_size = min(int(sample_size * outlier_fraction), len(outliers))
        non_outlier_sample_size = sample_size - outlier_sample_size
        
        # Adjust if we don't have enough outliers
        if outlier_sample_size < len(outliers):
            # Sample from outliers
            outlier_sample = outliers.sample(outlier_sample_size, random_state=random_state)
        else:
            # Take all outliers
            outlier_sample = outliers
            # Adjust non-outlier sample size
            non_outlier_sample_size = sample_size - len(outlier_sample)
        
        # Adjust if we don't have enough non-outliers
        non_outlier_sample_size = min(non_outlier_sample_size, len(non_outliers))
        
        # Sample from non-outliers
        if non_outlier_sample_size > 0:
            non_outlier_sample = non_outliers.sample(non_outlier_sample_size, random_state=random_state)
        else:
            non_outlier_sample = pd.DataFrame()
        
        # Combine samples
        sampled_data = pd.concat([outlier_sample, non_outlier_sample])
        
        logger.info(
            f"Taking outlier-biased sample of {len(sampled_data)} rows "
            f"({len(outlier_sample)} outliers, {len(non_outlier_sample)} non-outliers) "
            f"from {len(data)} total rows"
        )
        
        return sampled_data
    
    def sample_data(
        self, 
        data: pd.DataFrame, 
        strategy: str = "random",
        **kwargs
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Sample data using the specified strategy.
        
        Args:
            data: Input DataFrame
            strategy: Sampling strategy ('random', 'stratified', 'outlier_biased')
            **kwargs: Additional arguments for the specific sampling strategy
            
        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: Sampled DataFrame and sampling metadata
        """
        if not self.should_sample(data):
            logger.info(f"Data size ({len(data)} rows) below sampling threshold, using full dataset")
            return data, {"sampled": False, "original_size": len(data), "sample_size": len(data)}
        
        start_size = len(data)
        
        # Extract relevant kwargs for each strategy
        if strategy == "random":
            relevant_kwargs = {k: v for k, v in kwargs.items() if k in ['sample_size', 'random_state']}
            sampled_data = self.random_sample(data, **relevant_kwargs)
            method = "random"
        elif strategy == "stratified":
            relevant_kwargs = {k: v for k, v in kwargs.items() if k in ['sample_size', 'random_state', 'stratify_columns']}
            sampled_data = self.stratified_sample(data, **relevant_kwargs)
            method = "stratified"
        elif strategy == "outlier_biased":
            relevant_kwargs = {k: v for k, v in kwargs.items() if k in [
                'sample_size', 'random_state', 'numerical_columns', 
                'outlier_fraction', 'method', 'threshold'
            ]}
            sampled_data = self.outlier_biased_sample(data, **relevant_kwargs)
            method = "outlier_biased"
        else:
            logger.warning(f"Unknown sampling strategy: {strategy}, falling back to random sampling")
            relevant_kwargs = {k: v for k, v in kwargs.items() if k in ['sample_size', 'random_state']}
            sampled_data = self.random_sample(data, **relevant_kwargs)
            method = "random (fallback)"
        
        metadata = {
            "sampled": True,
            "original_size": start_size,
            "sample_size": len(sampled_data),
            "sampling_ratio": len(sampled_data) / start_size,
            "method": method
        }
        
        return sampled_data, metadata
