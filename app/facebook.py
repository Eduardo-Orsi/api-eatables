from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights

# Replace these with your credentials
app_id = 'YOUR_APP_ID'
app_secret = 'YOUR_APP_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
ad_account_id = 'act_YOUR_AD_ACCOUNT_ID'

# Initialize the API
FacebookAdsApi.init(app_id, app_secret, access_token)

# Create an AdAccount object
account = AdAccount(ad_account_id)

# Fetch insights with spend data (e.g., for the last 30 days)
params = {
    'time_range': {'since': '2025-02-23', 'until': '2025-03-25'},  # Adjust dates as needed
    'fields': [
        AdsInsights.Field.campaign_name,
        AdsInsights.Field.adset_name,
        AdsInsights.Field.ad_name,
        AdsInsights.Field.spend,
        AdsInsights.Field.impressions,
        AdsInsights.Field.clicks
    ],
    'level': 'ad',  # Can be 'campaign', 'adset', or 'ad' depending on granularity
}

insights = account.get_insights(params=params)

# Process and print the data
for insight in insights:
    print(f"Campaign: {insight.get('campaign_name', 'N/A')}")
    print(f"Ad Set: {insight.get('adset_name', 'N/A')}")
    print(f"Ad: {insight.get('ad_name', 'N/A')}")
    print(f"Spend: ${insight.get('spend', '0')}")
    print(f"Impressions: {insight.get('impressions', '0')}")
    print(f"Clicks: {insight.get('clicks', '0')}")
    print("---")