# ProHandel Fivetran Connector

This connector integrates the ProHandel API with Fivetran, enabling automated data extraction and loading into your data warehouse.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Fivetran account
- ProHandel API credentials

### Local Development

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the connector:

Edit the `configuration.json` file to include your ProHandel API credentials:

```json
{
  "api_url": "https://api.prohandel.example.com/v1",
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET"
}
```

4. Test the connector locally:

```bash
fivetran debug
```

This will create a local DuckDB database (`warehouse.db`) with the extracted data.

### Deployment to Fivetran

1. Deploy the connector to Fivetran:

```bash
fivetran deploy --api-key YOUR_FIVETRAN_API_KEY --destination YOUR_DESTINATION --connection prohandel
```

2. Configure the connector in the Fivetran dashboard:

- Set up the connection details
- Configure sync frequency
- Map tables to your destination schema

## Data Quality Integration

This connector includes basic data quality validation before sending data to Fivetran. For more comprehensive data quality monitoring, use the Mercurios.ai data quality monitoring system after the data is loaded into your warehouse.

## Entities Extracted

The connector extracts the following entities from ProHandel:

- **Articles**: Product catalog data
- **Customers**: Customer information
- **Orders**: Order header data
- **Sales**: Sales transaction data
- **Inventory**: Current inventory levels

## Incremental Loading

The connector supports incremental loading, only extracting data that has changed since the last sync. This is managed through the state tracking in Fivetran.

## Troubleshooting

- Check the logs in the Fivetran dashboard for any errors
- For local testing issues, examine the `fivetran.log` file
- Ensure your API credentials are correct and have the necessary permissions

## Security

- API credentials are securely stored in Fivetran's credential management system
- No credentials are stored in the code repository
