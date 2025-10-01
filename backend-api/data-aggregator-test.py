import json, requests, os
from datetime import datetime
from dotenv import load_dotenv, dotenv_values

# Configurations
load_dotenv()
CHARITY_API_KEY = os.getenv("CHARITY_API_KEY")
COUNTRY_CODE = os.getenv("COUNTRY_CODE")
COUNTRY = os.getenv("COUNTRY")

# Fetch Poverty Data (World Bank API)
pip_url = f"https://api.worldbank.org/pip/v1/pip?country={COUNTRY_CODE}&year=all&povline=2.15&format=json"
pip_resp = requests.get(pip_url).json()

# print("Poverty Data: \n", json.dumps(pip_resp, indent=4, ensure_ascii=False))
# pip_data_latest = pip_resp[-1] if isinstance(pip_resp, list) else pip_resp
# print(
#     "Recent Poverty Data: \n", json.dumps(pip_data_latest, indent=4, ensure_ascii=False)
# )

# Fetch NGO Data (Every.org API)

# non_profit_url = f"https://partners.every.org/v0.2/browse/poverty?apiKey={CHARITY_API_KEY}&take=5&page=1"
# non_profit_data = requests.get(non_profit_url).json()
# print("\nNGO Data: \n", non_profit_data)

all_results = []
page = 1
per_page = 100

# Paginate through all pages to get complete data
while True:
    non_profit_url = f"https://partners.every.org/v0.2/browse/poverty?apiKey={CHARITY_API_KEY}&take={per_page}&page={page}"  # all poverty related non profits
    response = requests.get(non_profit_url)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        break

    data = response.json()
    nonprofits = data.get("nonprofits", [])
    if not nonprofits:
        print("No more data available.")
        break

    all_results.extend(nonprofits)
    # print(f"Fetched page {page}, got {len(nonprofits)} results.")

    # Stop if we've reached the last page
    pagination = data.get("pagination", {})
    if page >= pagination.get("pages", page):
        break

    page += 1

# Filter nonprofits by country in either description or location
country_results = [
    org
    for org in all_results
    if COUNTRY.lower() in str(org.get("description", "")).strip().lower()
    or COUNTRY.lower() in str(org.get("location", "")).strip().lower()
]

print(f"\nNonprofits in Country: {len(country_results)} \n")

# Aggregate both poverty data and nonprofit data
result = {
    "country": {"name": COUNTRY, "code": COUNTRY_CODE},
    "poverty_data": pip_resp,  # All historical poverty data from World Bank API
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
            "matchedByLocation": COUNTRY.lower()
            in str(org.get("location", "")).strip().lower(),
            "matchedByDescription": COUNTRY.lower()
            in str(org.get("description", "")).strip().lower(),
        }
        for org in country_results
    ],
    "summary": {
        "total_nonprofits_found": len(country_results),
        "total_poverty_data_years": len(pip_resp) if isinstance(pip_resp, list) else 1,
        "generated_at": datetime.now().isoformat(),
    },
}

print("\n" + "=" * 50)
print("COMBINED DATA RESULT:")
print("=" * 50)
print(json.dumps(result, indent=4, ensure_ascii=False))
