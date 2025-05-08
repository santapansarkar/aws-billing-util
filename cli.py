#!/usr/bin/env python3
"""
Command-line interface for the AWS Billing API.
"""

import argparse
import datetime
import json
import sys
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from aws_billing_api import AWSBillingAPI
import config

def parse_date(date_str):
    """Parse date string into datetime.date object"""
    if date_str.lower() == 'today':
        return datetime.date.today()
    elif date_str.lower() == 'yesterday':
        return datetime.date.today() - datetime.timedelta(days=1)
    elif date_str.lower() == 'month_start':
        today = datetime.date.today()
        return today.replace(day=1)
    elif date_str.lower() == 'month_end':
        today = datetime.date.today()
        next_month = today.replace(day=1) + relativedelta(months=1)
        return next_month - datetime.timedelta(days=1)
    elif date_str.lower() == 'year_start':
        today = datetime.date.today()
        return today.replace(month=1, day=1)
    else:
        try:
            return parse(date_str).date()
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'")
            sys.exit(1)

def format_cost(cost_data):
    """Format cost data for display"""
    amount = float(cost_data.get('Amount', 0))
    unit = cost_data.get('Unit', 'USD')
    return f"{amount:.2f} {unit}"

def print_json(data):
    """Print data as formatted JSON"""
    print(json.dumps(data, indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(description='AWS Billing API CLI')
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--region', default=config.AWS_REGION, help='AWS region name')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Cost and usage command
    cost_parser = subparsers.add_parser('cost', help='Get cost and usage data')
    cost_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    cost_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    cost_parser.add_argument('--granularity', default='DAILY', choices=['DAILY', 'MONTHLY', 'HOURLY'], help='Time granularity')
    cost_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Cost by service command
    service_parser = subparsers.add_parser('service', help='Get cost by service')
    service_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    service_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    service_parser.add_argument('--granularity', default='MONTHLY', choices=['DAILY', 'MONTHLY'], help='Time granularity')
    service_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Cost by account command
    account_parser = subparsers.add_parser('account', help='Get cost by account')
    account_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    account_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    account_parser.add_argument('--granularity', default='MONTHLY', choices=['DAILY', 'MONTHLY'], help='Time granularity')
    account_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Cost by region command
    region_parser = subparsers.add_parser('region', help='Get cost by region')
    region_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    region_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    region_parser.add_argument('--granularity', default='MONTHLY', choices=['DAILY', 'MONTHLY'], help='Time granularity')
    region_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Cost by resource ID command
    resource_parser = subparsers.add_parser('resource', help='Get cost by resource ID')
    resource_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    resource_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    resource_parser.add_argument('--resource-id', help='Specific resource ID to filter by')
    resource_parser.add_argument('--resource-ids', nargs='+', help='List of resource IDs to filter by')
    resource_parser.add_argument('--granularity', default='DAILY', choices=['DAILY', 'MONTHLY', 'HOURLY'], help='Time granularity')
    resource_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Resource utilization command
    utilization_parser = subparsers.add_parser('utilization', help='Get detailed utilization for a specific resource')
    utilization_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    utilization_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    utilization_parser.add_argument('--resource-id', required=True, help='Resource ID to analyze')
    utilization_parser.add_argument('--granularity', default='DAILY', choices=['DAILY', 'MONTHLY', 'HOURLY'], help='Time granularity')
    utilization_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Cost by tag command
    tag_parser = subparsers.add_parser('tag', help='Get cost by resource tag')
    tag_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    tag_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    tag_parser.add_argument('--tag-key', required=True, help='Tag key to group by')
    tag_parser.add_argument('--tag-values', nargs='+', help='List of tag values to filter by')
    tag_parser.add_argument('--granularity', default='DAILY', choices=['DAILY', 'MONTHLY'], help='Time granularity')
    tag_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Forecast command
    forecast_parser = subparsers.add_parser('forecast', help='Get cost forecast')
    forecast_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    forecast_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD or special: today, yesterday, month_start, month_end, year_start)')
    forecast_parser.add_argument('--granularity', default='MONTHLY', choices=['DAILY', 'MONTHLY'], help='Time granularity')
    forecast_parser.add_argument('--metric', default='UNBLENDED_COST', choices=['UNBLENDED_COST', 'BLENDED_COST', 'AMORTIZED_COST'], help='Forecast metric')
    forecast_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Get monthly cost summary')
    summary_parser.add_argument('--months', type=int, default=6, help='Number of months to look back')
    summary_parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize the API
    billing_api = AWSBillingAPI(
        profile_name=args.profile,
        region_name=args.region
    )
    
    try:
        if args.command == 'cost':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_cost_and_usage(
                start_date=start_date,
                end_date=end_date,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Cost for {start_date} to {end_date} ===")
                for result in response.get('ResultsByTime', []):
                    time_period = result.get('TimePeriod', {})
                    start = time_period.get('Start')
                    end = time_period.get('End')
                    costs = result.get('Total', {})
                    
                    print(f"\nPeriod: {start} to {end}")
                    for metric, cost_data in costs.items():
                        print(f"  {metric}: {format_cost(cost_data)}")
        
        elif args.command == 'service':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_cost_by_service(
                start_date=start_date,
                end_date=end_date,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Costs by service for {start_date} to {end_date} ===")
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
        
        elif args.command == 'account':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_cost_by_account(
                start_date=start_date,
                end_date=end_date,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Costs by account for {start_date} to {end_date} ===")
                for result in response.get('ResultsByTime', []):
                    time_period = result.get('TimePeriod', {})
                    start = time_period.get('Start')
                    end = time_period.get('End')
                    groups = result.get('Groups', [])
                    
                    print(f"\nPeriod: {start} to {end}")
                    for group in groups:
                        account = group.get('Keys', ['Unknown'])[0]
                        metrics = group.get('Metrics', {})
                        blended_cost = metrics.get('BlendedCost', {})
                        print(f"  Account {account}: {format_cost(blended_cost)}")
        
        elif args.command == 'region':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_cost_by_region(
                start_date=start_date,
                end_date=end_date,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Costs by region for {start_date} to {end_date} ===")
                for result in response.get('ResultsByTime', []):
                    time_period = result.get('TimePeriod', {})
                    start = time_period.get('Start')
                    end = time_period.get('End')
                    groups = result.get('Groups', [])
                    
                    print(f"\nPeriod: {start} to {end}")
                    for group in groups:
                        region = group.get('Keys', ['Unknown'])[0]
                        metrics = group.get('Metrics', {})
                        blended_cost = metrics.get('BlendedCost', {})
                        print(f"  {region}: {format_cost(blended_cost)}")
        
        elif args.command == 'resource':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            
            # Combine single resource ID and list if both are provided
            resource_ids = []
            if args.resource_id:
                resource_ids.append(args.resource_id)
            if args.resource_ids:
                resource_ids.extend(args.resource_ids)
                
            response = billing_api.get_cost_by_resource_id(
                start_date=start_date,
                end_date=end_date,
                resource_ids=resource_ids if resource_ids else None,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Costs by resource ID for {start_date} to {end_date} ===")
                for result in response.get('ResultsByTime', []):
                    time_period = result.get('TimePeriod', {})
                    start = time_period.get('Start')
                    end = time_period.get('End')
                    groups = result.get('Groups', [])
                    
                    print(f"\nPeriod: {start} to {end}")
                    for group in groups:
                        resource_id = group.get('Keys', ['Unknown'])[0]
                        metrics = group.get('Metrics', {})
                        blended_cost = metrics.get('BlendedCost', {})
                        print(f"  {resource_id}: {format_cost(blended_cost)}")
        
        elif args.command == 'utilization':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_resource_utilization(
                start_date=start_date,
                end_date=end_date,
                resource_id=args.resource_id,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Resource utilization for {args.resource_id} from {start_date} to {end_date} ===")
                for result in response.get('ResultsByTime', []):
                    time_period = result.get('TimePeriod', {})
                    start = time_period.get('Start')
                    end = time_period.get('End')
                    costs = result.get('Total', {})
                    
                    print(f"\nPeriod: {start} to {end}")
                    for metric, cost_data in costs.items():
                        print(f"  {metric}: {format_cost(cost_data)}")
        
        elif args.command == 'tag':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_cost_by_resource_tags(
                start_date=start_date,
                end_date=end_date,
                tag_key=args.tag_key,
                tag_values=args.tag_values,
                granularity=args.granularity
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Costs by tag '{args.tag_key}' for {start_date} to {end_date} ===")
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
                        print(f"  {args.tag_key}={tag_value}: {format_cost(blended_cost)}")
        
        elif args.command == 'forecast':
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            response = billing_api.get_cost_forecast(
                start_date=start_date,
                end_date=end_date,
                granularity=args.granularity,
                metric=args.metric
            )
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Cost forecast for {start_date} to {end_date} ===")
                total = response.get('Total', {})
                forecast = total.get('Amount', 'N/A')
                unit = total.get('Unit', 'USD')
                print(f"Forecasted cost: {forecast} {unit}")
        
        elif args.command == 'summary':
            response = billing_api.get_monthly_cost_summary(args.months)
            
            if args.json:
                print_json(response)
            else:
                print(f"\n=== Monthly cost summary for the last {args.months} months ===")
                for result in response.get('ResultsByTime', []):
                    time_period = result.get('TimePeriod', {})
                    start = time_period.get('Start')
                    end = time_period.get('End')
                    costs = result.get('Total', {})
                    
                    print(f"\nMonth: {start} to {end}")
                    for metric, cost_data in costs.items():
                        print(f"  {metric}: {format_cost(cost_data)}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()