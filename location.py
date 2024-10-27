import streamlit as st
from extra_streamlit_components import CookieManager
import requests

# JavaScript code to get the user's location and update URL parameters
js_code = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        document.getElementById("location").innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    
    document.cookie = "latitude=" + latitude + "; path=/";
    document.cookie = "longitude=" + longitude + "; path=/";
}

getLocation();
</script>

"""

# Embed the JavaScript code in Streamlit
st.components.v1.html(js_code)

cookie_manager = CookieManager()


# Get a cookie
cookies = cookie_manager.get_all()

try :
    lat = cookies['latitude']
    st.write("Latitude : " , lat)
    
    long = cookies['longitude']
    st.write("longitude : " , long)


    def get_uv_index(api_key, latitude, longitude):
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{long}"
        response = requests.get(url)
        data = response.json()
        uv_index = data['current']['uv']
        return uv_index
    
    # Example usage
    api_key = 'f3fec67a02fe41d58e8114039242710'
    uv_index = get_uv_index(api_key, lat, long)
    st.write(f"The UV index for your location is {uv_index}.")
    
    from geopy.geocoders import Photon
    
    geolocator = Photon(user_agent="test")
    location = geolocator.reverse((lat, long), language='en')
    st.write("Location : ",location.address)
    
    def sunscreen_recommender(uv_index):
        if uv_index < 3:
            return "Low risk. No sunscreen needed."
        elif 3 <= uv_index < 6:
            return "Moderate risk. Use SPF 15+ sunscreen."
        elif 6 <= uv_index < 8:
            return "High risk. Use SPF 30+ sunscreen."
        elif 8 <= uv_index < 11:
            return "Very high risk. Use SPF 50+ sunscreen."
        else:
            return "Extreme risk. Use SPF 50+ sunscreen and avoid going outside."
    
    # Example usage
    recommendation = sunscreen_recommender(uv_index)
    st.write(f"UV Index: {uv_index} - Recommendation: {recommendation}")
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Generate a range of numbers
    numbers = np.linspace(0, 1, 100).reshape(10, 10)
    
    # Create a gradient image
    plt.imshow(numbers, cmap='viridis', aspect='auto')
    plt.colorbar()
    
    # Save the image
    plt.savefig('gradient.png')
    
    # Display the image in Streamlit
    st.image('gradient.png')
except :
    st.warning("Turn on Location")

