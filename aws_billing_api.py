#!/usr/bin/env python3
"""
AWS Billing API - A Python API for accessing AWS billing information based on date range.
"""

import boto3
import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Union, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('aws_billing_api')


class AWSBillingAPI:
    """
    API for accessing AWS billing information based on date range.
    """
    
    def __init__(self, profile_name: Optional[str] = None, region_name: str = 'us-east-1'):
        """
        Initialize the AWS Billing API.
        
        Args:
            profile_name: AWS profile name to use. If None, default profile is used.
            region_name: AWS region name to use.
        """
        self.session = boto3.Session(profile_name=profile_name, region_name=region_name)
        self.ce_client = self.session.client('ce')  # Cost Explorer client
        logger.info(f"Initialized AWS Billing API with region: {region_name}")
        
    def get_cost_and_usage(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        granularity: str = 'DAILY',
        metrics: List[str] = None,
        group_by: List[Dict[str, str]] = None,
        filter_expression: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get cost and usage data for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            metrics: List of metrics to include (defaults to ["BlendedCost", "UnblendedCost", "UsageQuantity"])
            group_by: List of grouping dimensions
            filter_expression: Cost Explorer filter expression
            
        Returns:
            Dict containing the cost and usage data
        """
        # Convert datetime objects to strings if needed
        if isinstance(start_date, datetime.date):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime.date):
            end_date = end_date.strftime('%Y-%m-%d')
            
        # Default metrics if none provided
        if metrics is None:
            metrics = ["BlendedCost", "UnblendedCost", "UsageQuantity"]
            
        # Prepare request parameters
        params = {
            'TimePeriod': {
                'Start': start_date,
                'End': end_date
            },
            'Granularity': granularity,
            'Metrics': metrics
        }
        
        # Add optional parameters if provided
        if group_by:
            params['GroupBy'] = group_by
            
        if filter_expression:
            params['Filter'] = filter_expression
            
        try:
            logger.info(f"Requesting cost and usage data from {start_date} to {end_date}")
            response = self.ce_client.get_cost_and_usage(**params)
            return response
        except Exception as e:
            logger.error(f"Error getting cost and usage data: {str(e)}")
            raise
    
    def get_cost_by_service(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        granularity: str = 'MONTHLY'
    ) -> Dict[str, Any]:
        """
        Get cost data grouped by service for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            
        Returns:
            Dict containing the cost data grouped by service
        """
        group_by = [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            group_by=group_by
        )
    
    def get_cost_by_account(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        granularity: str = 'MONTHLY'
    ) -> Dict[str, Any]:
        """
        Get cost data grouped by account for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            
        Returns:
            Dict containing the cost data grouped by account
        """
        group_by = [{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}]
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            group_by=group_by
        )
    
    def get_cost_by_region(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        granularity: str = 'MONTHLY'
    ) -> Dict[str, Any]:
        """
        Get cost data grouped by region for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            
        Returns:
            Dict containing the cost data grouped by region
        """
        group_by = [{'Type': 'DIMENSION', 'Key': 'REGION'}]
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            group_by=group_by
        )
    
    def get_cost_by_resource_id(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        resource_ids: List[str] = None,
        granularity: str = 'DAILY'
    ) -> Dict[str, Any]:
        """
        Get cost data grouped by resource ID for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            resource_ids: Optional list of specific resource IDs to filter by
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            
        Returns:
            Dict containing the cost data grouped by resource ID
        """
        # Group by resource ID
        group_by = [{'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}]
        
        # Filter by specific resource IDs if provided
        filter_expression = None
        if resource_ids:
            filter_expression = {
                'Dimensions': {
                    'Key': 'RESOURCE_ID',
                    'Values': resource_ids
                }
            }
        
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            group_by=group_by,
            filter_expression=filter_expression
        )
    
    def get_cost_by_resource_tags(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        tag_key: str,
        tag_values: List[str] = None,
        granularity: str = 'DAILY'
    ) -> Dict[str, Any]:
        """
        Get cost data grouped by a specific resource tag for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            tag_key: The tag key to group by (without the 'tag:' prefix)
            tag_values: Optional list of specific tag values to filter by
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            
        Returns:
            Dict containing the cost data grouped by the specified tag
        """
        # Group by the specified tag
        tag_key_with_prefix = f"tag:{tag_key}"
        group_by = [{'Type': 'TAG', 'Key': tag_key}]
        
        # Filter by specific tag values if provided
        filter_expression = None
        if tag_values:
            filter_expression = {
                'Tags': {
                    'Key': tag_key,
                    'Values': tag_values
                }
            }
        
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            group_by=group_by,
            filter_expression=filter_expression
        )
    
    def get_cost_forecast(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        granularity: str = 'MONTHLY',
        metric: str = 'UNBLENDED_COST'
    ) -> Dict[str, Any]:
        """
        Get cost forecast for the specified date range.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            granularity: Time granularity of the data (DAILY or MONTHLY)
            metric: Forecast metric (UNBLENDED_COST, BLENDED_COST, AMORTIZED_COST, NET_UNBLENDED_COST, NET_AMORTIZED_COST)
            
        Returns:
            Dict containing the cost forecast data
        """
        # Convert datetime objects to strings if needed
        if isinstance(start_date, datetime.date):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime.date):
            end_date = end_date.strftime('%Y-%m-%d')
            
        try:
            logger.info(f"Requesting cost forecast from {start_date} to {end_date}")
            response = self.ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metric=metric
            )
            return response
        except Exception as e:
            logger.error(f"Error getting cost forecast: {str(e)}")
            raise
    
    def get_monthly_cost_summary(self, months_back: int = 6) -> Dict[str, Any]:
        """
        Get a summary of costs for the last N months.
        
        Args:
            months_back: Number of months to look back
            
        Returns:
            Dict containing monthly cost summary
        """
        end_date = datetime.date.today()
        start_date = end_date - relativedelta(months=months_back)
        
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity='MONTHLY'
        )
    
    def get_service_costs_for_period(
        self, 
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        services: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get costs for specific services in the given period.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            services: List of service names to filter by (e.g., ["Amazon EC2", "Amazon S3"])
            
        Returns:
            Dict containing service costs
        """
        filter_expression = None
        if services:
            filter_expression = {
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': services
                }
            }
            
        group_by = [{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity='MONTHLY',
            group_by=group_by,
            filter_expression=filter_expression
        )
    
    def get_resource_utilization(
        self,
        start_date: Union[str, datetime.date], 
        end_date: Union[str, datetime.date],
        resource_id: str,
        granularity: str = 'DAILY'
    ) -> Dict[str, Any]:
        """
        Get detailed utilization and cost data for a specific resource.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format or as datetime.date object
            end_date: End date in 'YYYY-MM-DD' format or as datetime.date object
            resource_id: The specific resource ID to analyze
            granularity: Time granularity of the data (DAILY, MONTHLY, or HOURLY)
            
        Returns:
            Dict containing detailed resource utilization and cost data
        """
        # Filter for the specific resource ID
        filter_expression = {
            'Dimensions': {
                'Key': 'RESOURCE_ID',
                'Values': [resource_id]
            }
        }
        
        # Get more detailed metrics for this resource
        metrics = [
            "BlendedCost", 
            "UnblendedCost", 
            "UsageQuantity",
            "NormalizedUsageAmount"
        ]
        
        return self.get_cost_and_usage(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            metrics=metrics,
            filter_expression=filter_expression
        )