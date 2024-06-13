import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import os
from ultralytics import YOLO
import cv2
import numpy as np
import xgboost as xgb
import joblib
from sklearn.preprocessing import LabelEncoder
from math import pi

st.set_page_config(page_title="E-Waste Project", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

def string_to_json(input_string):
    # Split the input string by comma and remove any leading or trailing whitespace
    items = [item.strip() for item in input_string.split(',')][:-1]
    results=[]
    for item in items:
        number,label=item.split(' ')
        number=int(number)
        label=str(label)
        dict1 = {"class":label,"Quantity":number}
        results.append(dict1) 
    try:  
        return pd.DataFrame(results)
    except:
        return results

def get_random_image_path(method):
    ROOT_DIRECTORIES=[r'./demo_images/AA',
                      r'./demo_images/A',
                      r'./demo_images/B',
                      r'./demo_images/C']
    if method=='random':
        ROOT_DIRECTORY=np.random.choice(ROOT_DIRECTORIES)
        list_files = os.listdir(ROOT_DIRECTORY)
        random_image = np.random.choice(list_files)
        final_path = os.path.join(ROOT_DIRECTORY, random_image)
    elif method=='AA':
        ROOT_DIRECTORY=ROOT_DIRECTORIES[0]
        list_files = os.listdir(ROOT_DIRECTORY)
        random_image = np.random.choice(list_files)
        final_path = os.path.join(ROOT_DIRECTORY, random_image)
    elif method=='A':
        ROOT_DIRECTORY=ROOT_DIRECTORIES[1]
        list_files = os.listdir(ROOT_DIRECTORY)
        random_image = np.random.choice(list_files)
        final_path = os.path.join(ROOT_DIRECTORY, random_image)
    elif method=='B':
        ROOT_DIRECTORY=ROOT_DIRECTORIES[2]
        list_files = os.listdir(ROOT_DIRECTORY)
        random_image = np.random.choice(list_files)
        final_path = os.path.join(ROOT_DIRECTORY, random_image)
    elif method=='C':
        ROOT_DIRECTORY=ROOT_DIRECTORIES[3]
        list_files = os.listdir(ROOT_DIRECTORY)
        random_image = np.random.choice(list_files)
        final_path = os.path.join(ROOT_DIRECTORY, random_image)
    return final_path


def process_YOLO_results(results):
    for r in results:
        im_array = r.plot(conf=True)  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
    return im,r

def preprocess_image_for_display(image_path):
    # Load the image
    image = Image.open(image_path)
    
    # Convert to RGB mode if image has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Convert the image to numpy array
    image_np = np.array(image)
    
    # Find coordinates of non-zero pixels
    non_zero_pixels = np.argwhere(np.all(image_np != [0, 0, 0], axis=-1))
    
    # Find bounding box
    top_left = np.min(non_zero_pixels, axis=0)
    bottom_right = np.max(non_zero_pixels, axis=0)
    
    # Crop the image to the bounding box
    cropped_image_np = image_np[top_left[0]:bottom_right[0]+1, top_left[1]:bottom_right[1]+1]
    
    # Convert numpy array back to PIL image
    cropped_image = Image.fromarray(cropped_image_np)
    
    return cropped_image

def apply_yolo_model_return_image(image_path):
    model=YOLO(r'./models/best.pt')
    results = model(image_path)  # results list
    im, result = process_YOLO_results(results)
    return im,(result.tojson())

def calculate_area(row):
    width = abs(row['x2'] - row['x1'])
    height = abs(row['y2'] - row['y1'])
    #TODO normalize based on the image size
    return width * height

def most_dominant_color(image_path):
    # Load the image
    img = cv2.imread(image_path)

    # Convert image to RGB (OpenCV uses BGR by default)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Calculate histogram
    hist = cv2.calcHist([img_rgb], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])

    # Define ranges for green and brown in RGB
    green_lower = (0, 50, 0)
    green_upper = (100, 255, 100)

    brown_lower = (100, 40, 0)
    brown_upper = (255, 180, 120)

    # Mask green and brown regions
    green_mask = cv2.inRange(img_rgb, green_lower, green_upper)
    brown_mask = cv2.inRange(img_rgb, brown_lower, brown_upper)

    # Count pixels in each region
    green_pixels = cv2.countNonZero(green_mask)
    brown_pixels = cv2.countNonZero(brown_mask)

    # Determine the most dominant color
    if green_pixels > brown_pixels:
        return "Green"
    else:
        return "Brown"

def rearrange_columns(column_names, new_order):
    """
    Rearranges the column names according to the specified order.

    Args:
        column_names (list): The original list of column names.
        new_order (list): The desired order of column names.

    Returns:
        list: The rearranged list of column names.
    """
    rearranged_columns = []
    for col_name in new_order:
        if col_name in column_names:
            rearranged_columns.append(col_name)
    return rearranged_columns







with st.expander('Component Detection Model'):
    method=st.selectbox('Select a method',['AA','A','B','C'])
    random_path=get_random_image_path(method)
    image=preprocess_image_for_display(random_path)
    im,results=apply_yolo_model_return_image(image)
    df = pd.read_json(results)
    classes = df['name'].value_counts()
    df['box'] = df['box'].apply(lambda x: calculate_area(x)).to_dict()
    components_area = df.groupby('name')['box'].sum().to_dict()
    components_area = pd.concat([pd.Series(components_area,name='area'), classes], axis=1)
    components_area['area'].apply(lambda x: x/(image.width*image.height))
    transposed_classes = classes.to_frame().T
    c1,c2=st.columns(2)
    with c1:
        class_name=random_path.split('/')[-1].split('_')[0]
        sample_id=random_path
        st.subheader(f"Class: {class_name}")
        st.subheader(f"Sample ID: {class_name}   Most Dominant Color: {most_dominant_color(random_path)}")
        st.image(image,use_column_width=True)
    with c2:
        st.dataframe(transposed_classes)
        st.image(im)
    component_counts = df['name'].value_counts()
    row_dict = {'image_id': sample_id, 'class': class_name,'color':most_dominant_color(random_path)}
    for key in components_area.T.keys():
        row_dict[key+'_area'] = components_area.T[key].values[0]
        row_dict[key+'_count'] = component_counts.get(key, 0)
    display_df = pd.DataFrame([row_dict])
    image_features = pd.DataFrame(columns=['class','color','Connector_count','Connector_area','IC_count','IC_area','L_count','L_area','MC_count','MC_area','Q_count','Q_area','STC_count','STC_area','TC_count','TC_area','X_count','X_area'])
    image_features=pd.concat([display_df,image_features],axis=0)
    image_features.fillna(0, inplace=True)
    st.write(image_features)
    
    
with st.expander('Classifier Model Prediction'):
    #Load the model
    model = joblib.load(r'./models/model2.pkl')
    label_encoder = LabelEncoder()
    image_features['class'] = label_encoder.fit_transform(image_features['class'])
    image_features['color'] = label_encoder.fit_transform(image_features['color'])
    image_features.drop(['image_id','class'], axis=1, inplace=True)
    column_names = [
    "color",
    "Connector_count",
    "Connector_area",
    "IC_count",
    "IC_area",
    "MC_count",
    "MC_area",
    "Q_count",
    "Q_area",
    "STC_count",
    "STC_area",
    "TC_count",
    "TC_area",
    "X_count",
    "X_area"
    ]
    image_features = image_features[rearrange_columns(image_features.columns, column_names)]
    predictions = model.predict(image_features)
    prediction_proba = model.predict_proba(image_features)
    probabiloties = pd.DataFrame(prediction_proba, columns=['A+','A','B','C'])
    model_data = {
    'Feature': ['IC_area', 'Connector_area', 'IC_count', 'L_count', 'TC_area', 'STC_count', 'color', 
                'STC_area', 'Q_area', 'L_area', 'TC_count', 'MC_area', 'MC_count', 'Q_count', 
                'Connector_count', 'X_count', 'X_area'],
    'Importance %': [15.704155, 7.809552, 7.614070, 7.558182, 7.458121, 7.000160, 6.964724,
                    6.654294, 5.240713, 5.219999, 5.096698, 4.576005, 3.873281, 2.670056,
                    2.443540, 2.325694, 1.790743]
    }
    st.subheader(f'The predicted class is trained with 300 images' )
    feature_descriptions = {
        "color": "Color of the object",
        "Connector_count": "Number of connectors present and its area normalized against the image size",
        "IC_count": "Number of integrated circuits and its area normalized against the image size",
        "L_count": "Number of inductors and its area normalized against the image size",
        "MC_count": "Number of microcontrollers and its area normalized against the image size",
        "Q_count": "Number of transistors and its area normalized against the image size",
        "STC_count": "Number of surface mount technology components and its area normalized against the image size",
        "TC_count": "Number of through-hole components and its area normalized against the image size",
        "X_count": "Number of miscellaneous components and its area normalized against the image size"
    }
    combined_features = {
        "Connector": "Connectors (count and area normalized against the image size)",
        "IC": "Integrated Circuits (count and area normalized against the image size)",
        "L": "Inductors (count and area normalized against the image size)",
        "MC": "Microcontrollers (count and area normalized against the image size)",
        "Q": "Transistors (count and area normalized against the image size)",
        "STC": "Surface Mount Technology Components (count and area normalized against the image size)",
        "TC": "Through-Hole Components (count and area normalized against the image size)",
        "X": "Miscellaneous Components (count and area normalized against the image size)"
    }
    st.subheader("Feature Selection")
    for feature in feature_descriptions:
        if any(keyword in feature for keyword in combined_features.keys()):
            category = feature.split("_")[0]
            st.write(f"- **{combined_features[category]}**: {feature_descriptions[feature]}")
        else:
            st.write(f"- **{feature}**: {feature_descriptions[feature]}")
    st.subheader(f'Feature Importance' )
    model_data = pd.DataFrame(model_data).set_index('Feature')
    st.write(model_data.T)
    predictions=predictions[0].max()
    if predictions == 0:
        predictions_let = 'A+'
    elif predictions == 1:
        predictions_let = 'A'
    elif predictions == 2:
        predictions_let = 'B'
    else:
        predictions_let = 'C'
    st.write(f'The predicted class is {predictions_let}')
    st.bar_chart(probabiloties.T)