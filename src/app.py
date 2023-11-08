import base64
import streamlit as st
from openai import OpenAI

client = OpenAI()

def get_response(messages):
    response = client.chat.completions.create(
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

st.title("Study Buddy with GPT-4 Vision")

if "messages" not in st.session_state:

    with st.form("Take a picture and add a comment (optional)", clear_on_submit=True):
        image = st.camera_input("Picture", label_visibility="collapsed")
        prompt = st.text_input("Comment", label_visibility="collapsed", placeholder="Comment the picture (optional)")
        submit_button = st.form_submit_button(label="Send")

    if submit_button:
        if not image:
            st.error("Please take a picture")
            st.stop()

    user_content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image.read()).decode('utf-8')}", "detail": "high"}}]
    if prompt:
        user_content.append({"type": "text", "text": prompt})

    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

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
            with st.chat_message("assistant"):
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