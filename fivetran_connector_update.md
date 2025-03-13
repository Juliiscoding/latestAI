# Fivetran Connector Update Instructions

## Current Fivetran Configuration
- **Connection ID**: bowed_protocol
- **Lambda Function**: arn:aws:lambda:eu-central-1:689864027744:function:prohandel-fivetran-connector
- **Region**: eu-central-1
- **Sync Method**: DIRECT

## Required Secret Updates

Update the following secrets in the Fivetran connector configuration:

| Secret Name | Current Value (Likely) | Correct Value |
|-------------|------------------------|---------------|
| PROHANDEL_API_KEY | 7e7c639358434c4fa215d4e3978739d0 | 7e7c639358434c4fa215d4e3978739d0 |
| PROHANDEL_API_SECRET | 1cjnuux79d | 1cjnuux79d |
| PROHANDEL_AUTH_URL | https://auth.prohandel.cloud/api/v4 | https://auth.prohandel.cloud/api/v4 |
| PROHANDEL_API_URL | https://api.prohandel.de/api/v2 | https://linde.prohandel.de/api/v2 |

The most important change is updating the **PROHANDEL_API_URL** to use the correct domain: **linde.prohandel.de** instead of **api.prohandel.de**.

## Steps to Update

1. Log in to your Fivetran dashboard
2. Navigate to the ProHandel connector (ID: bowed_protocol)
3. Click on "Edit Connection"
4. Update the secrets as shown above
5. Save the changes
6. Trigger a manual sync to test the updated configuration

## Verification

After updating the connector and triggering a sync, check the following:

1. Monitor the sync status in the Fivetran dashboard
2. Check the CloudWatch logs for the Lambda function to ensure it's being invoked correctly
3. Run the Snowflake data check script to verify that data is being loaded into the RAW schema
