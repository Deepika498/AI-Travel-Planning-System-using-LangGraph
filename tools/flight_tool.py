import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


AIRPORTS = {
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "kolkata": "CCU",
    "chennai": "MAA",
    "hyderabad": "HYD",
    "pune": "PNQ",
    "goa": "GOI",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "patna": "PAT",
    "indore": "IDR",
    "bhubaneswar": "BBI",
    "raipur": "RPR",
    "dubai": "DXB",
    "london": "LHR",
    "paris": "CDG",
    "singapore": "SIN",
    "tokyo": "NRT",
    "new york": "JFK"
}


def get_airports(query):

    query = query.lower()
    found = []

    for city in sorted(AIRPORTS, key=len, reverse=True):

        if re.search(r"\b" + re.escape(city) + r"\b", query):

            code = AIRPORTS[city]

            if code not in found:
                found.append(code)

    return found


def search_flights(query):

    airports = get_airports(query)

    # User must provide departure and destination
    if len(airports) < 2:
        return (
            "Please provide both departure and destination cities. "
            "Example: Delhi to Mumbai"
        )

    departure_code = airports[0]
    arrival_code = airports[1]

    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": API_KEY,
        "dep_iata": departure_code,
        "arr_iata": arrival_code,
        "limit": 5
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

    except Exception as e:
        return f"Flight API Error: {str(e)}"


    # Check API error
    if "error" in data:
        return f"Flight API Error: {data['error']}"


    flights = data.get("data", [])

    if not flights:
        return (
            f"No live flights found for "
            f"{departure_code} → {arrival_code}."
        )


    results = []


    for flight in flights:

        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})

        actual_departure = departure.get("iata", "")
        actual_arrival = arrival.get("iata", "")


        # Strict route validation
        if actual_departure != departure_code:
            continue

        if actual_arrival != arrival_code:
            continue


        airline = flight.get(
            "airline", {}
        ).get(
            "name",
            "Unknown"
        )


        flight_number = flight.get(
            "flight", {}
        ).get(
            "iata",
            "Unknown"
        )


        departure_airport = departure.get(
            "airport",
            "Unknown"
        )


        arrival_airport = arrival.get(
            "airport",
            "Unknown"
        )


        departure_time = departure.get(
            "scheduled",
            "Unknown"
        )


        arrival_time = arrival.get(
            "scheduled",
            "Unknown"
        )


        status = flight.get(
            "flight_status",
            "Unknown"
        )


        results.append(
            f"""
✈️ Airline: {airline}
🔢 Flight: {flight_number}

🛫 From: {departure_airport}
⏰ Departure: {departure_time}

🛬 To: {arrival_airport}
⏰ Arrival: {arrival_time}

📌 Status: {status}
"""
        )


        # Maximum 5 flights
        if len(results) == 5:
            break


    if not results:
        return (
            f"No live flights found for "
            f"{departure_code} → {arrival_code}."
        )


    return "\n".join(results)
