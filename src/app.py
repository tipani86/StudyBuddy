import base64
import hashlib
from utils import *
from PIL import Image
from io import BytesIO
import streamlit as st
from pathlib import Path
# from openai import OpenAI
import openai

FILE_ROOT = Path(__file__).parent

# client = OpenAI()
blob_op = AzureBlobOp()

@st.cache_data(show_spinner=False)
def get_css() -> str:
    # Read CSS code from style.css file
    with open(FILE_ROOT / "style.css", "r") as f:
        return f"<style>{f.read()}</style>"

def get_response(messages):
    # response = client.chat.completions.create(
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=messages,
        max_tokens=1500,
    )
    return response.choices[0]

system_prompt = """
You are a resourceful and creative school tutor, helping elementary school students with their homework. You will be presented with a picture of some problem (or problems) along with their answer. You should identify whether everything is correct or if there are mistakes. 
If there are mistakes, you should not give the answer directly, but rather offer a nudge or hint to the students so that they can figure out themselves, first of all where the problem even is, and then how to arrive at the correct solution. 
This path to revelation can take multiple back-and-forths of dialogue, so try to lead them on in baby steps instead of throwing too much to chew at a time.
"""
system_prompt = """
You are an expert, resourceful and creative school tutor. You are helping elementary school students with their homework. You will be presented with a problem (or problems) of some sorts. 
If you are also presented with an image, start by carefully analyzing the image. Remember, you are equipped with all the necessary expert knowledge to solve whatever problem is presented in the image. 
If you see that the student has answered, first determine if the student's reasoning is sound and the answer is correct. 
Break down the problem into simpler steps of inference and deduction, and then guide the student through the steps to arrive at the correct answer. 
If there is an image and you want to highlight one or several areas of the image, as part of and referred in your response, add a text section at the very end of your reply, starting with 'IMAGE_RECTANGLES: ' (always in plural and capitalized), followed by a standard JSON array of objects, as follows:
IMAGE_RECTANGLES: {
    "rectangles": [
        {"top_left": {"x": 0.0, "y": 0.0}, "bottom_right": {"x": 0.0, "y": 0.0}, color: "#ff0000"}
    ]
} 
The coordinates are normalized to relative positions in the image, with (0, 0) being the top left corner and (1, 1) being the bottom right corner. The color is a standard CSS color string.
"""

# Set page title and favicon
st.set_page_config(
    page_title="Study Buddy with GPT-4 Vision",
    page_icon="https://openai.com/favicon.ico"
)

# Load CSS code
st.markdown(get_css(), unsafe_allow_html=True)

st.title("Study Buddy with GPT-4 Vision")

if "messages" not in st.session_state:

    with st.form("Take a picture and add a comment (optional)", clear_on_submit=True):
        image = st.camera_input("Picture", label_visibility="collapsed")
        prompt = st.text_input("Comment", label_visibility="collapsed", placeholder="Comment/ask about the picture (optional)")
        submit_button = st.form_submit_button(label="Send")

    if submit_button:
        if not image:
            st.error("Please take a picture")
            st.stop()

        image_url = None
        # Load the image in PIL and resize so the long side is less than 2,000 px and short side less than 768 px, whichever limit comes first
        img = Image.open(image)
        # Check the original image size
        img_width, img_height = img.size
        # Calculate the resized image so it fits the limits
        if img_width > img_height:
            new_width = min(img_width, 2000)
            new_height = int(img_height * new_width / img_width)
            if new_height > 768:
                new_height = 768
                new_width = int(img_width * new_height / img_height)
        else:
            new_height = min(img_height, 2000)
            new_width = int(img_width * new_height / img_height)
            if new_width > 768:
                new_width = 768
                new_height = int(img_height * new_width / img_width)
        # Resize the image
        img = img.resize((new_width, new_height))
        # Uploaded filename is the image hash and .jpg format extension
        with BytesIO() as buffer:
            img.save(buffer, "JPEG")
            image_file = buffer.getvalue()
        image_hash = hashlib.md5(image_file).hexdigest()
        image_filename = f"{image_hash}.jpg"
        status, message, url = blob_op.upload_blob(image_file, image_filename)
        if status != 0:
            st.error(f"Error uploading image: {message}")
            st.stop()
        image_url = url

        user_content = [{"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}]
        if prompt:
            user_content.append({"type": "text", "text": prompt})

        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        st.rerun()

else:
    reset_button = st.button("Reset chat history")
    if reset_button:
        del st.session_state.messages
        st.rerun()

    # Displaying chat history so far
    for message in st.session_state.messages:
        match message["role"]:
            case "user":
                with st.chat_message("user"):
                    if isinstance(message["content"], list):
                        for content in message["content"]:
                            match content["type"]:
                                case "image_url":
                                    st.image(content["image_url"]["url"])
                                case "text":
                                    st.markdown(content["text"])
                    else:   # string
                        st.markdown(message["content"])
            case "assistant":
                with st.chat_message("assistant", avatar="https://openai.com/favicon.ico"):
                    st.markdown(message["content"])

    # If the last message is from the user, get the response and rerun, otherwise display a chat input widget

    if st.session_state.messages[-1]["role"] == "user":
        with st.spinner("Thinking..."):
            st.session_state.messages.append(get_response(st.session_state.messages))
        st.rerun()
    else:
        prompt = st.chat_input("Continue the conversation")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()