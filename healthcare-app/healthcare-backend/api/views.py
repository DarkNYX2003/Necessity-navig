from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Facility
from .serializers import UserSerializer, FacilitySerializer
from django.contrib.auth.hashers import make_password, check_password
import requests
from django.contrib.auth import authenticate
import logging
import coreapi

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register(request):
    data = request.data
    try:
        if 'email' not in data or 'username' not in data or 'password' not in data:
            return Response({"error": "Email, Username, and Password are required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password=make_password(data['password'])
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    except KeyError as e:
        logger.error(f"KeyError: {str(e)}")
        return Response({"error": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def login(request):
    try:
        data = request.data

        if data is None:
            return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            if user.check_password(password):
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An unexpected error occurred while retrieving the user.")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.exception("An unexpected error occurred in the login view.")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def get_facilities(request):
    location = request.data
    if not all(k in location for k in ('lat', 'lng')):
        return Response({"error": "Invalid location data"}, status=400)

    user_location = f"{location['lat']},{location['lng']}"
    radius = 1500  # Radius in meters

    try:
        # Fetch nearby healthcare facilities using Overpass API
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node
            ["amenity"="hospital"]
            (around:{radius},{location['lat']},{location['lng']});
          node
            ["amenity"="clinic"]
            (around:{radius},{location['lat']},{location['lng']});
          node
            ["amenity"="doctors"]
            (around:{radius},{location['lat']},{location['lng']});
          node
            ["amenity"="pharmacy"]
            (around:{radius},{location['lat']},{location['lng']});
          node
            ["amenity"="amrita"]
            (around:{radius},{location['lat']},{location['lng']});
        );
        out body;
        """
        
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()

        if 'elements' not in data:
            return Response({"error": "Error fetching data from OpenStreetMap API"}, status=500)

        facilities = data['elements']
        facility_locations = [f"{facility['lat']},{facility['lon']}" for facility in facilities]
        destinations = '|'.join(facility_locations)

        # Fetch travel times and distances using GraphHopper API
        graphhopper_url = "https://graphhopper.com/api/1/route"
        graphhopper_api_key = '086d2616-dfd4-448f-8c37-5bddb41025b2'
        
        facilities_list = []
        for facility in facilities:
            facility_location = f"{facility['lat']},{facility['lon']}"
            gh_response = requests.get(
                graphhopper_url,
                params={
                    'point': [user_location, facility_location],
                    'vehicle': 'car',
                    'locale': 'en',
                    'calc_points': 'false',
                    'key': graphhopper_api_key
                }
            )
            gh_data = gh_response.json()

            if 'paths' not in gh_data:
                return Response({"error": "Error fetching data from GraphHopper API"}, status=500)

            path = gh_data['paths'][0]
            travel_time = path['time'] / 60000  # Convert from ms to minutes
            distance = path['distance'] / 1000  # Convert from meters to kilometers

            facility_data = {
                'name': facility.get('tags', {}).get('name', 'Unknown'),
                'address': facility.get('tags', {}).get('addr:full', 'Address not available'),
                'lat': facility['lat'],
                'lon': facility['lon'],
                'travel_time': f"{travel_time:.1f} mins",
                'distance': f"{distance:.1f} km"
            }
            facilities_list.append(facility_data)

    except requests.exceptions.RequestException as e:
        return Response({"error": f"Request to API failed: {e}"}, status=500)

    return Response(facilities_list)

@api_view(['POST'])
def get_facilities1(request):
    location = request.data
    user_location = f"{location['lat']},{location['lng']}"
    api_url = 'https://healthsites.io/api/v3/facilities'
    api_token ='be9e9bbc597512e7fd067dcb07917e2a5976485f'

    params = {
        #'lat': location['lat'],
        #'lng': location['lng'],
        'api-key' : api_token,
        'country' : 'India',
        'page'   : 3, 
        'output' : 'Json'
    }
   # headers = {'Authorization':f'token {api_token}'}
    try:
        response = request.get(api_url,params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return Response({"error": "Error fetching data from Healthsites.io API"}, status=500)

        facilities = data
        facilities_list= []

        for facility in facilities:
            attributes = facility.get('attributes',{})
            centroid = facility.get('centroid',{}).get('coordinates',[None,None])
            
            if None in centroid:
                continue
            
            facility_location = f"{centroid[1]},{centroid[0]}"

            graphhopper_url = "https://graphhopper.com/api/1/route"
            graphhopper_api_key = 'YOUR_GRAPHHOPPER_API_KEY'
            
            gh_response = requests.get(
                graphhopper_url,
                params={
                    'point': [user_location, facility_location],
                    'vehicle': 'car',
                    'locale': 'en',
                    'calc_points': 'false',
                    'key': graphhopper_api_key
                }
            )
            gh_data = gh_response.json()

            if 'paths' not in gh_data:
                return Response({"error": "Error fetching data from GraphHopper API"}, status=500)

            path = gh_data['paths'][0]
            travel_time = path['time'] / 60000  # Convert from ms to minutes
            distance = path['distance'] / 1000  # Convert from meters to kilometers

            facility_data = {
                'name' : attributes.get('name','not available'),
                'address': f"{attributes.get('addr_street', 'Unknown')} {attributes.get('addr_city', '')} {attributes.get('addr_postcode', '')}".strip(),
                'lat': centroid[1],
                'lon': centroid[0],
                'travel_time': f"{travel_time:.1f} mins",
                'distance': f"{distance:.1f} km",
                'contact': attributes.get('contact', 'Contact not available'),  # Assuming contact field exists
                'reviews': attributes.get('reviews', 'Reviews not available') , # Assuming reviews field exists
                'type' : attributes.get('healthcare' 'not specified '),
                'timings' : f"{attributes.get('opening_hours','not specified')}",
            }
            facilities_list.append(facility_data)

    except requests.exceptions.RequestException as e:
        return Response({"error": f"Request to API failed: {e}"}, status=500)

    return Response(facilities_list)

@api_view(['POST'])
def get_facilities3(request) :

# Initialize a client & load the schema document
    client = coreapi.Client()
    schema = client.get("https://healthsites.io/api/docs/")
    api_url = 'https://healthsites.io/api/v3/facilities'
    api_token ='be9e9bbc597512e7fd067dcb07917e2a5976485f'

        # Interact with the API endpoint
    action = ["facilities", "list"]
    params = {
        "api-key": api_token,
        "page": 3,
        "country": 'India',  
        "output": 'json',
        }
    result = client.action(schema, action, params=params)
    data = result.json()
    print(result)