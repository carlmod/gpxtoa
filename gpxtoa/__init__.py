import base64
import json
import http.client
import urllib.request
import urllib.parse
import urllib.error

import gpxpy.gpx

def main():
    """Entry point for the application script"""

    headers = {
    }

    params = urllib.parse.urlencode({
        #'Kommun': '{string}',
        #'Hamn': '{string}',
        #'Info': '{string}',
    })
    data = download(headers, params)
    gpx = gpxpy.gpx.GPX()
    for habour in data:
        if has_position(habour) and has_pumpout(habour):
            gpx.waypoints.append(create_waypoint(habour))


    #print("Start out")
    print(gpx.to_xml())
    #print("End out")

def create_waypoint(api_data):
    """Return a waypoint object from the api data."""
    #print(api_data)
    messages=[]
    if 'Info' in api_data and api_data['Info']:
        messages.append(api_data['Info'])
    for message in api_data.get('Meddelanden', []):
        if message.get('Serviceanlaggningsnamn') == 'Sugtömning':
            date=message['Datum']
            status="Trasig" if message.get('Fungerande')==False else "Funkar"
            text=message['Meddelande']
            messages.append(', '.join([date, status, text]))
    messages='\n'.join(messages)
    waypoint = gpxpy.gpx.GPXWaypoint(
        latitude=api_data['Latitud'],
        longitude=api_data['Longitud'],
        name=api_data['Hamn'],
        symbol="Service-Pump-Out-Facility",
        type='WPT',
        description=messages
        )
    return waypoint

def has_pumpout(api_data):
    """Return True if habour has "Sugtömmning" """
    for item in api_data['Serviceanlaggningar']:
        if item['Id'] == 3:
            return True
    return False

def has_position(api_data):
    """Return True if habour has a defined position."""
    if "Longitud" in api_data:
        return True
    else:
        return False

def download(headers, params):
    """Download the data from Transportstyrelsen.

    The API is documented at: https://tsopendata.portal.azure-api.net/docs/services
    The code below is taken from Transportstyrelsens webpage.
    """
    try:
        conn = http.client.HTTPSConnection('tsopendata.azure-api.net')
        conn.request("GET", "/hamnar/v0.1/?%s" % params, "{body}", headers)
        response = conn.getresponse()
        body = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    data = json.loads(body.decode("utf-8"))
    return data


if __name__ == "__main__":
    main()