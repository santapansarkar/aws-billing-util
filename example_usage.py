#!/usr/bin/env python3
"""
Example usage of the AWS Billing API.
"""

import datetime
from dateutil.relativedelta import relativedelta
import json
from aws_billing_api import AWSBillingAPI
import config

def format_cost(cost_data):
    """Format cost data for display"""
    amount = float(cost_data.get('Amount', 0))
    unit = cost_data.get('Unit', 'USD')
    return f"{amount:.2f} {unit}"

def main():
    # Initialize the API
    billing_api = AWSBillingAPI(
        profile_name=config.AWS_PROFILE,
        region_name=config.AWS_REGION
    )
    
    # Example 1: Get costs for the last 30 days
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    
    print(f"\n=== Cost for the last 30 days ({start_date} to {end_date}) ===")
    response = billing_api.get_cost_and_usage(start_date, end_date)
    
    for result in response.get('ResultsByTime', []):
        time_period = result.get('TimePeriod', {})
        start = time_period.get('Start')
        end = time_period.get('End')
        costs = result.get('Total', {})
        
        print(f"\nPeriod: {start} to {end}")
        for metric, cost_data in costs.items():
            print(f"  {metric}: {format_cost(cost_data)}")
    
    # Example 2: Get costs by service for the current month
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    first_day_of_next_month = (today.replace(day=1) + relativedelta(months=1))
    
    print(f"\n=== Costs by service for current month ({first_day_of_month} to {today}) ===")
    response = billing_api.get_cost_by_service(first_day_of_month, today)
    
    for result in response.get('ResultsByTime', []):
        time_period = result.get('TimePeriod', {})
        start = time_period.get('Start')
        end = time_period.get('End')
        groups = result.get('Groups', [])
        
        print(f"\nPeriod: {start} to {end}")
        for group in groups:
            service = group.get('Keys', ['Unknown'])[0]
            metrics = group.get('Metrics', {})
            blended_cost = metrics.get('BlendedCost', {})
            print(f"  {service}: {format_cost(blended_cost)}")
    
    # Example 3: Get monthly cost summary for the last 6 months
    print("\n=== Monthly cost summary for the last 6 months ===")
    response = billing_api.get_monthly_cost_summary(6)
    
    for result in response.get('ResultsByTime', []):
        time_period = result.get('TimePeriod', {})
        start = time_period.get('Start')
        end = time_period.get('End')
        costs = result.get('Total', {})
        
        print(f"\nMonth: {start} to {end}")
        for metric, cost_data in costs.items():
            print(f"  {metric}: {format_cost(cost_data)}")
    
    # Example 4: Get cost forecast for the next month
    next_month_start = first_day_of_next_month
    next_month_end = (next_month_start + relativedelta(months=1))
    
    print(f"\n=== Cost forecast for next month ({next_month_start} to {next_month_end}) ===")
    try:
        response = billing_api.get_cost_forecast(next_month_start, next_month_end)
        total = response.get('Total', {})
        forecast = total.get('Amount', 'N/A')
        unit = total.get('Unit', 'USD')
        print(f"Forecasted cost: {forecast} {unit}")
    except Exception as e:
        print(f"Could not get forecast: {str(e)}")
    
    # Example 5: Get costs by resource ID for the current month
    print(f"\n=== Costs by resource ID for current month ({first_day_of_month} to {today}) ===")
    try:
        response = billing_api.get_cost_by_resource_id(first_day_of_month, today)
        
        for result in response.get('ResultsByTime', []):
            time_period = result.get('TimePeriod', {})
            start = time_period.get('Start')
            end = time_period.get('End')
            groups = result.get('Groups', [])
            
            print(f"\nPeriod: {start} to {end}")
            # Sort resources by cost (highest first)
            sorted_groups = sorted(
                groups, 
                key=lambda g: float(g.get('Metrics', {}).get('BlendedCost', {}).get('Amount', 0)), 
                reverse=True
            )
            
            # Print top 10 resources by cost
            for i, group in enumerate(sorted_groups[:10]):
                resource_id = group.get('Keys', ['Unknown'])[0]
                metrics = group.get('Metrics', {})
                blended_cost = metrics.get('BlendedCost', {})
                print(f"  {i+1}. {resource_id}: {format_cost(blended_cost)}")
    except Exception as e:
        print(f"Could not get resource costs: {str(e)}")
    
    # Example 6: Get costs by tag for the current month (if tag cost allocation is enabled)
    print(f"\n=== Costs by tag 'Environment' for current month ({first_day_of_month} to {today}) ===")
    try:
        response = billing_api.get_cost_by_resource_tags(
            start_date=first_day_of_month,
            end_date=today,
            tag_key='Environment'
        )
        
        for result in response.get('ResultsByTime', []):
            time_period = result.get('TimePeriod', {})
            start = time_period.get('Start')
            end = time_period.get('End')
            groups = result.get('Groups', [])
            
            print(f"\nPeriod: {start} to {end}")
            for group in groups:
                tag_value = group.get('Keys', ['Unknown'])[0]
                metrics = group.get('Metrics', {})
                blended_cost = metrics.get('BlendedCost', {})
                print(f"  Environment={tag_value}: {format_cost(blended_cost)}")
    except Exception as e:
        print(f"Could not get tag costs (tag cost allocation may not be enabled): {str(e)}")

if __name__ == "__main__":
    main()