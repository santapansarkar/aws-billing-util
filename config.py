"""
Configuration settings for AWS Billing API.
"""

# AWS profile to use (None for default)
AWS_PROFILE = None

# AWS region to use
AWS_REGION = 'us-east-1'

# Default date format
DATE_FORMAT = '%Y-%m-%d'

# Default metrics to retrieve
DEFAULT_METRICS = ["BlendedCost", "UnblendedCost", "UsageQuantity"]

# Default granularity for cost data
DEFAULT_GRANULARITY = 'DAILY'