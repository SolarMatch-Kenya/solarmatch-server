import google.oauth2.credentials
import googleapiclient.discovery
from flask import current_app


def get_solar_data(lat, lng):
    api_key = current_app.config["GOOGLE_API_KEY"]
    service = googleapiclient.discovery.build("solar", "v1", api_key=api_key)

    # The request body
    body = {
        "location": {
            "latitude": lat,
            "longitude": lng
        },
        "radius_meters": 100
    }

    # Execute the request
    try:
        response = service.buildingInsights().findClosest(body=body).execute()
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
