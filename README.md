# AWS Billing Utility

A Python API for accessing AWS billing information based on date ranges.

## Features

- Get cost and usage data for specific date ranges
- Group costs by service, account, or region
- Group costs by resource ID to track individual resource costs
- Group costs by resource tags for better cost allocation
- Get cost forecasts for future periods
- Monthly cost summaries
- Filter costs by specific services
- Detailed resource utilization analysis

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/aws-billing-util.git
   cd aws-billing-util
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure AWS credentials:
   - Either set up your AWS credentials using the AWS CLI: `aws configure`
   - Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - Or specify a profile in the `config.py` file

## Usage

### Basic Usage

```python
from aws_billing_api import AWSBillingAPI
import datetime

# Initialize the API
billing_api = AWSBillingAPI()

# Get costs for a specific date range
start_date = '2023-01-01'
end_date = '2023-01-31'
response = billing_api.get_cost_and_usage(start_date, end_date)

# Print the results
for result in response.get('ResultsByTime', []):
    time_period = result.get('TimePeriod', {})
    start = time_period.get('Start')
    end = time_period.get('End')
    costs = result.get('Total', {})
    
    print(f"Period: {start} to {end}")
    for metric, cost_data in costs.items():
        amount = float(cost_data.get('Amount', 0))
        unit = cost_data.get('Unit', 'USD')
        print(f"  {metric}: {amount:.2f} {unit}")
```

### Getting Costs by Resource ID

```python
# Get costs grouped by resource ID
response = billing_api.get_cost_by_resource_id(start_date, end_date)

# Get costs for specific resource IDs
resource_ids = ['i-1234567890abcdef0', 'vol-1234567890abcdef0']
response = billing_api.get_cost_by_resource_id(start_date, end_date, resource_ids=resource_ids)
```

### Getting Costs by Resource Tags

```python
# Get costs grouped by a specific tag
response = billing_api.get_cost_by_resource_tags(start_date, end_date, tag_key='Environment')

# Get costs for specific tag values
response = billing_api.get_cost_by_resource_tags(
    start_date, 
    end_date, 
    tag_key='Environment', 
    tag_values=['Production', 'Development']
)
```

### Advanced Usage

```python
# Get costs grouped by service
response = billing_api.get_cost_by_service(start_date, end_date)

# Get costs grouped by account
response = billing_api.get_cost_by_account(start_date, end_date)

# Get costs grouped by region
response = billing_api.get_cost_by_region(start_date, end_date)

# Get cost forecast for the next month
today = datetime.date.today()
first_day_of_next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
last_day_of_next_month = (first_day_of_next_month + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
response = billing_api.get_cost_forecast(first_day_of_next_month, last_day_of_next_month)

# Get detailed utilization for a specific resource
response = billing_api.get_resource_utilization(start_date, end_date, 'i-1234567890abcdef0')
```

## Command Line Interface

The utility includes a command-line interface for easy access:

```
# Get general cost and usage data
./cli.py cost --start-date 2023-01-01 --end-date 2023-01-31

# Get costs by service
./cli.py service --start-date month_start --end-date today

# Get costs by resource ID
./cli.py resource --start-date month_start --end-date today

# Get costs for specific resource IDs
./cli.py resource --start-date month_start --end-date today --resource-ids i-1234567890abcdef0 vol-1234567890abcdef0

# Get costs by tag
./cli.py tag --start-date month_start --end-date today --tag-key Environment

# Get detailed utilization for a specific resource
./cli.py utilization --start-date month_start --end-date today --resource-id i-1234567890abcdef0

# Get a cost forecast for the next month
./cli.py forecast --start-date month_end --end-date "month_end + 30 days"

# Get a monthly summary for the last 6 months
./cli.py summary --months 6

# Output in JSON format for further processing
./cli.py resource --start-date month_start --end-date today --json
```

## Example Script

Run the example script to see the API in action:

```
./example_usage.py
```

## Configuration

You can modify the `config.py` file to change default settings:

- `AWS_PROFILE`: AWS profile to use (None for default)
- `AWS_REGION`: AWS region to use
- `DATE_FORMAT`: Default date format
- `DEFAULT_METRICS`: Default metrics to retrieve
- `DEFAULT_GRANULARITY`: Default granularity for cost data

## Requirements

- Python 3.6+
- boto3
- python-dateutil

## Notes

- To use the tag-based cost allocation features, you must first activate cost allocation tags in the AWS Billing console.
- The AWS Cost Explorer API has a delay of up to 24 hours for data to become available.
- If you haven't used Cost Explorer before, there might be a delay before data becomes available.

## License

MIT