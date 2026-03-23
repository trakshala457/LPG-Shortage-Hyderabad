import streamlit as st
import requests
import re
from gtts import gTTS
import os

# Page Configuration
st.set_page_config(page_title="LPG Availability Finder", page_icon="🔥", layout="centered")

# Custom CSS for the "Emergency/Alert" aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #fdf2f2;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #e63946;
        color: white;
        font-weight: bold;
    }
    .stSelectbox, .stTextInput {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Hyderabad LPG Tracker")
st.subheader("Find the nearest gas stock during current shortages.")

# Form for User Input
with st.form("lpg_finder_form"):
    st.write("### Enter Your Details")
    
    # Email Address Input with basic validation
    email = st.text_input("Email Address", placeholder="e.g. xyz@gmail.com")
    
    # Location Selection
    location = st.selectbox(
    "Select Your Nearest Area",
    options=[
        # West Hyderabad
        "Gachibowli", "Hitech City", "Madhapur", "Kondapur", "Miyapur",
        "Kukatpally", "Nizampet", "Bachupally", "Hafeezpet", "Chandanagar",

        # North Hyderabad
        "Alwal", "Kompally", "Bowenpally", "Suchitra", "Petbasheerabad",
        "Jeedimetla", "Shamirpet",

        # Central Hyderabad
        "Begumpet", "Ameerpet", "Punjagutta", "Somajiguda",
        "SR Nagar", "Sanath Nagar",

        # East Hyderabad
        "Uppal", "LB Nagar", "Nagole", "Habsiguda",
        "Ramanthapur", "Kothapet",

        # South / Old City
        "Mehdipatnam", "Attapur", "Tolichowki",
        "Falaknuma", "Chandrayangutta", "Bahadurpura",

        # Other / Developing Areas
        "Manikonda", "Narsingi", "Puppalaguda",
        "Tellapur", "Financial District", "Kokapet"
    ],
    index=0
)
    
    submit_btn = st.form_submit_button("Find Nearest Gas & Send SMS")

# Logic to trigger n8n Webhook
if submit_btn:
    # Simple regex for email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not re.match(email_regex, email):
        st.error("❌ Please enter a valid email address (e.g., name@example.com).")
    else:
        # Your specific n8n Webhook URL
        N8N_WEBHOOK_URL = "https://workflow.ccbp.in/webhook-test/82cad76c-3271-4806-aad4-4cd5e4d617d8"
        
        # Data payload to send to the Agent
        payload = {
            "email": email,
            "location": location
        }
        
        try:
            with st.spinner(f"Agent is searching for outlets in {location}..."):
                # Sending the POST request to n8n
                response = requests.post(N8N_WEBHOOK_URL, json=payload)
            
            if response.status_code == 200:
                st.success(f"✅ Search Complete! An SMS with the location pin, cost, and availability is being sent to {email}.")
                st.balloons()
                data = response.json()
                # --- NEW: Result Display Card ---
                st.markdown("### 📍 Found Nearest Outlet")
                with st.container():

                        st.metric("Price", data['cost'])
                        st.write(f"Agency: {data['name']}")

                        st.metric("Status", data['availability'])
                        st.write(f"Area: {data['area']}")
                    
                    # Google Maps Button
                        st.link_button("🗺️ Open Google Maps Pin", data['pin'], use_container_width=True)
                # --------------------------------
                data = response.json()

                # 1. Create the text string for the audio
                audio_text = f"LPG availability found. Agency: {data['name']}. Price: {data['cost']}. Status: {data['availability']}."

                # 2. Generate the audio file
                tts = gTTS(text=audio_text, lang='en')
                tts.save("result.mp3")

                # 3. Play the audio in the UI
                st.audio("result.mp3", format="audio/mp3", autoplay=False)

                # 4. Clean up the file (optional)
                # os.remove("result.mp3")
                st.balloons()
            else:
                st.error(f"⚠️ Error: The Agent responded with status {response.status_code}. Please check your n8n workflow.")
            
        except Exception as e:
            st.error(f"❌ Connection Error: Could not reach the AI Agent. ({str(e)})")

# Footer
st.markdown("---")
st.caption("Data is pulled from a dummy real-time availability database for demonstration purposes.")