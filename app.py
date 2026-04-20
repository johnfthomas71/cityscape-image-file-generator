import os
import io
import base64

import streamlit as st
from PIL import Image
from openai import OpenAI

# ---------- OpenAI client & API key guard ----------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error(
        "OPENAI_API_KEY environment variable is not set. "
        "Please configure it in your Streamlit deployment settings."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# ---------- App config ----------
st.set_page_config(page_title="Cityscape Generator", layout="centered")
st.title("🏙️ Cityscape Image Generator")
st.write(
    "Generate wide, horizontally rectangular cityscape illustrations for MongoDB "
    "location pages with a consistent hero-banner style."
)

# ---------- Session state ----------
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "generated_filenames" not in st.session_state:
    st.session_state.generated_filenames = []
if "generated_location" not in st.session_state:
    st.session_state.generated_location = ""

# ---------- Controls ----------
st.subheader("1. Location")
location = st.text_input(
    "City / region / country",
    value="New York City, New York",
)

st.subheader("2. Options")
col_o1, col_o2 = st.columns(2)
with col_o1:
    num_images = st.slider("Number of variations", 1, 3, 3)
with col_o2:
    # Valid sizes for DALL·E 3
    aspect_choice = st.selectbox(
        "Aspect / size",
        (
            "Wide 1792×1024 (hero-like)",
            "Square 1024×1024",
        ),
        index=0,
    )

# Map aspect choice to API size
image_size = "1792x1024" if aspect_choice.startswith("Wide") else "1024x1024"

STYLE_PROMPT = (
    "wide, horizontally rectangular cityscape illustration: "
    "clean, flat/vector-like, soft gradients, subtle atmospheric depth, "
    "limited palette of MongoDB greens and teals. "
    "No text, no people, stylized hero-image composition."
)

def b64_to_image(b64_data: str) -> Image.Image:
    img_bytes = base64.b64decode(b64_data)
    return Image.open(io.BytesIO(img_bytes)).convert("RGBA")

# ---------- Generation ----------
st.subheader("3. Generate")
if st.button("Generate cityscape images"):
    if not location.strip():
        st.error("Please enter a location.")
    else:
        # Clear previous state
        st.session_state.generated_images = []
        st.session_state.generated_filenames = []
        st.session_state.generated_location = location

        with st.spinner(f"Generating image(s) for {location}..."):
            try:
                for idx in range(num_images):
                    # Slight steering phrase to reduce prompt rewriting quirks
                    prompt = (
                        f"I want a {STYLE_PROMPT} "
                        f"Focus on {location} landmarks and skyline."
                    )

                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size=image_size,
                        n=1,
                        quality="hd",
                        response_format="b64_json",
                    )

                    b64_image = response.data[0].b64_json
                    img = b64_to_image(b64_image)

                    loc_slug = (
                        location.lower()
                        .replace(",", "")
                        .replace(" ", "_")
                    )
                    fname = f"{loc_slug}_cityscape_{idx + 
