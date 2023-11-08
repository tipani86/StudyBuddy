import base64
import streamlit as st
from openai import OpenAI

with st.form("Take a picture and add a comment (optional)", clear_on_submit=True):
    image = st.camera_input("Picture", label_visibility="collapsed")
    prompt = st.text_input("Comment", label_visibility="collapsed", placeholder="Optional comment")
    submit_button = st.form_submit_button(label="Send")

if submit_button:
    if not image:
        st.error("Please take a picture")
        st.stop()

    st.image(image, caption=prompt)