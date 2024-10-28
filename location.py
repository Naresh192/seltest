import streamlit as st
from extra_streamlit_components import CookieManager
import requests
import matplotlib.pyplot as plt
import numpy as np
from streamlit_js_eval import streamlit_js_eval
import pandas as pd

st.markdown('''<style>div[data-testid="stToolbar"] {
  visibility: hidden;
}</style>''',unsafe_allow_html=True)

st.markdown('''<style>iframe{
    visibility: hidden;
}
</style>''',unsafe_allow_html=True)


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
  
    def get_uv_color(uv_index):
        if uv_index <= 2:
            return 'green'
        elif uv_index <= 5:
            return 'yellow'
        elif uv_index <= 7:
            return 'orange'
        elif uv_index <= 10:
            return 'red'
        else:
            return 'red'
    
        # Function to display UV index on a reversed gradient scale with a pointer and transparent background
    def display_uv_index(uv_index):
        fig, ax = plt.subplots(figsize=(6, 1))
        gradient = np.linspace(1, 0, 256)  # Reverse the gradient
        gradient = np.vstack((gradient, gradient))
    
        ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap('RdYlGn'))
        ax.set_axis_off()
    
        color = get_uv_color(uv_index)
        
        # Calculate the position of the pointer
        pointer_position = uv_index / 11.0
    
        # Add a pointer to the gradient
        ax.annotate('▼', xy=(pointer_position, -0.1), xycoords='axes fraction', color=color, fontsize=20, ha='center')
        ax.text(0.5, -0.5, f'UV Index: {uv_index}', color=color, fontsize=15, ha='center', va='center', transform=ax.transAxes)
    
        # Set transparent background
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
    
        st.pyplot(fig)
    
    # Streamlit app
    st.markdown("<h4>UV Index Display</h4>", unsafe_allow_html=True)
    display_uv_index(uv_index)

except :
    st.warning("Turn on Location")


if st.button("Refresh") :
      streamlit_js_eval(js_expressions="parent.window.location.reload()")
