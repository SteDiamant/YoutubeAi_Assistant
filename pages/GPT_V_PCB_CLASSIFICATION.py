import streamlit as st
import os
from PIL import Image
import base64
import requests
from dotenv import load_dotenv

st.set_page_config(layout="wide")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def compress_png_to_size(input_image, output_path, target_size_mb):
    target_size_bytes = target_size_mb * 1024 * 1024
    
    # Open the input image
    img = Image.open(input_image)
    
    # Get original dimensions
    width, height = img.size
    aspect_ratio = width / height
    
    # Resize image until it is smaller than the target size
    while True:
        img.save(output_path, format='png', optimize=True)
        file_size = os.path.getsize(output_path)
        
        if file_size <= target_size_bytes:
            break
        
        width = int(width * 0.5)
        height = int(width / aspect_ratio)
        img = img.resize((width, height))
        
    st.success(f"Image Compressed Successfully. Final size: {file_size / (1024 * 1024):.2f} MB")
    return output_path

def identify_PCB_grade(image_path, system_desc):
    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f""" "system": {system_desc}" """
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def main():
    st.title("GPT V PCB Classification")
    
    file_ = open("TSE-Project [Autosaved].gif", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<div style="display: flex; justify-content: center;"><img src="data:image/gif;base64,{data_url}" alt="GPT approach" width="800" ></div>',
        unsafe_allow_html=True
    )
    
    # File uploader
    uploaded_image = st.sidebar.file_uploader("Choose an image...", type="png")
    
    # System description
    with st.expander("System Description"):
        system_desc = st.text_area("Describe Here", """You are provided with an image of a PCB. Your task is to classify the grade of the PCB based on the following criteria:
            | Bins            | Criteria                                                                                                                                                                 |
            |-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------  |
            | AA  | At least one side heavily populated with ICs and CPUs (almost no space left on the PCB). No attachments like batteries, aluminum, iron, or capacitors.                  |
            | A   | At least one side well populated with ICs and CPUs. No attachments like batteries, aluminum, iron, or capacitors.                                                       |
            | B   | Quality between A & C. At least one side moderately populated.                                                                                                          |
            | C   | Almost or completely not populated with ICs, CPUs, or Gold. No attachments like batteries, often brown in color / heavy weight. Large capacitors.                       |

            Steps to Classify PCB Grade:

            1. **Image Examination:**
            - Carefully observe the provided image of the PCB.

            2. **Check for Heavy Population (ICs and CPUs):**
            - Determine if at least one side of the PCB is heavily populated with Integrated Circuits (ICs) and Central Processing Units (CPUs).
            - Assess if there is almost no space left on the PCB due to the dense population of ICs and CPUs.

            3. **Check for Attachments:**
            - Look for any attachments on the PCB such as batteries, aluminum, iron, or capacitors.

            4. **Classification Decision:**
            - **PCB AA:**
                - If at least one side is heavily populated with ICs and CPUs (almost no space left) and there are no attachments like batteries, aluminum, iron, or capacitors, classify as PCB AA.
            - **PCB A:**
                - If at least one side is well populated with ICs and CPUs and there are no attachments like batteries, aluminum, iron, or capacitors, classify as PCB A.
            - **PCB B:**
                - If the quality is between A & C and at least one side is moderately populated, classify as PCB B.
            - **PCB C:**
                - If the PCB is almost or completely not populated with ICs, CPUs, or Gold, and often brown in color/heavy weight with large capacitors, classify as PCB C.

            5. **Return Classification:**
            - Return the class of the PCB (AA, A, B, C) with reasoning behind the grade.

            Image:""", height=500)
    
    # Submit button
    submitted = st.button("Submit")
    
    # Classification logic
    if submitted and uploaded_image:
        with st.spinner('Compressing and classifying image...'):
            compressed_image_path = compress_png_to_size(uploaded_image, f'compressed_{uploaded_image.name}', 20)
            img = Image.open(compressed_image_path)
            st.image(img)
            category = identify_PCB_grade(compressed_image_path, system_desc)
            st.markdown(category['choices'][0]['message']['content'])
    
    if uploaded_image and not submitted:
        st.sidebar.warning("Please press the Submit button to classify the PCB.")

if __name__ == "__main__":
    main()
