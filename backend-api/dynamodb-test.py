import boto3, json, requests, os
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError
from dotenv import load_dotenv, dotenv_values

load_dotenv()
# AWS Clients
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
data_table = dynamodb.Table("PovertyDataCache")
country_table = dynamodb.Table("CountryCodes")

secrets_client = boto3.client(
    "secretsmanager",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def get_country_name(country_code):
    """Get full country name from DynamoDB country codes table"""
    try:
        response = country_table.get_item(Key={"country_code": country_code.upper()})
        if "Item" in response:
            return response["Item"]["country_name"]
        else:
            return country_code  # Fallback to code if not found
    except Exception as e:
        print(f"Error fetching country name: {e}")
        return country_code


def get_secret():
    try:
        get_secret_value_response = secrets_client.get_secret_value(
            SecretId="CHARITY_API_KEY"
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)


def convert_floats_to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB compatibility"""
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def lambda_handler(event, context):
    all_results = []
    page = 1
    per_page = 100

    # Extract country code from request
    country_code = event.get("queryStringParameters", {}).get("country", "BGD")
    country_name = get_country_name(country_code)

    # Get API keys from secrets
    secret = get_secret()
    api_key = secret["EVERYORG_API"]
    print(
        f"Fetching data for {country_name} ({country_code}) using API key {api_key}"
    )  # Debug log

    # 1. Check cache in DynamoDB
    response = data_table.get_item(Key={"country": country_code})
    if "Item" in response:
        cached = response["Item"]
        # if data is fresh (<1 day), return cached
        current_timestamp = int(datetime.now().timestamp())
        if (current_timestamp - cached["timestamp"]) < 86400:  # 86400 seconds = 1 day
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(cached["data"], default=str),
            }

    # 2. Fetch Poverty Data (World Bank API)
    pip_url = f"https://api.worldbank.org/pip/v1/pip?country={country_code}&year=all&povline=2.15&format=json"
    print(f"Fetching poverty data from: {pip_url}")

    try:
        pip_response = requests.get(pip_url)
        if pip_response.status_code == 200 and pip_response.text.strip():
            pip_resp = pip_response.json()
            print(
                f"Successfully fetched poverty data: {len(pip_resp) if isinstance(pip_resp, list) else 'single object'}"
            )
        else:
            print("No poverty data available, using empty list")
            pip_resp = []
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching poverty data: {e}")
        pip_resp = []

    # 3. Fetch NGO Data (Every.org API) - Paginate through all pages
    while True:
        non_profit_url = f"https://partners.every.org/v0.2/browse/poverty?apiKey={api_key}&take={per_page}&page={page}"
        response = requests.get(non_profit_url)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()
        nonprofits = data.get("nonprofits", [])
        if not nonprofits:
            break

        all_results.extend(nonprofits)

        # Stop if we've reached the last page
        pagination = data.get("pagination", {})
        if page >= pagination.get("pages", page):
            break

        page += 1

    # 4. Filter nonprofits by country in location and description
    country_results = [
        org
        for org in all_results
        if country_name.lower() in str(org.get("description", "")).strip().lower()
        or country_name.lower() in str(org.get("location", "")).strip().lower()
    ]

    # 5. Aggregate data
    result = {
        "country": {"name": country_name, "code": country_code},
        "poverty_data": pip_resp,
        "nonprofits": [
            {
                "name": org.get("name"),
                "description": org.get("description"),
                "website": org.get("websiteUrl"),
                "location": org.get("location"),
                "tags": org.get("tags", []),
                "profileUrl": org.get("profileUrl"),
                "logoUrl": org.get("logoUrl"),
                "coverImageUrl": org.get("coverImageUrl"),
                "matchedByLocation": country_name.lower()
                in str(org.get("location", "")).strip().lower(),
                "matchedByDescription": country_name.lower()
                in str(org.get("description", "")).strip().lower(),
            }
            for org in country_results
        ],
        "summary": {
            "total_nonprofits_found": len(country_results),
            "total_poverty_data_years": (
                len(pip_resp) if isinstance(pip_resp, list) else 1
            ),
            "generated_at": datetime.now().isoformat(),
        },
    }

    # 6. Save to DynamoDB
    # Convert the result to DynamoDB-compatible format
    dynamo_result = convert_floats_to_decimal(result)

    data_table.put_item(
        Item={
            "country": country_code,
            "timestamp": int(datetime.now().timestamp()),
            "data": dynamo_result,
        }
    )

    # 7. Return JSON
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }


if __name__ == "__main__":
    # Test event
    test_event = {"queryStringParameters": {"country": "AUS"}}  # Test with Australia

    test_context = {}

    result = lambda_handler(test_event, test_context)
    # print(json.dumps(json.loads(result["body"]), indent=2))
