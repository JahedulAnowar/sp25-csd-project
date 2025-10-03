"""
Script to populate DynamoDB CountryCodes table with country mappings
Run this once to set up the country code mappings in DynamoDB
"""

import os
import json
import boto3
from dotenv import load_dotenv, dotenv_values

load_dotenv()


def create_and_populate_country_table():
    """Create CountryCodes table and populate with country code mappings"""

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    # Create table if it doesn't exist
    try:
        table = dynamodb.create_table(
            TableName="CountryCodes",
            KeySchema=[{"AttributeName": "country_code", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "country_code", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait for table to be created
        table.wait_until_exists()
        print("CountryCodes table created successfully")

    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("CountryCodes table already exists")
        table = dynamodb.Table("CountryCodes")

    # Load country codes from JSON file
    with open("country-codes.json", "r") as f:
        country_data = json.load(f)

    # Batch write country codes to DynamoDB
    with table.batch_writer() as batch:
        for country in country_data:
            batch.put_item(
                Item={
                    "country_code": country["country_code"],
                    "country_name": country["country_name"],
                }
            )

    print(f"Successfully populated {len(country_data)} country codes into DynamoDB")


if __name__ == "__main__":
    create_and_populate_country_table()
