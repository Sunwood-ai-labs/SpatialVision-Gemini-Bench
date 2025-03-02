"""
画像アップロードコンポーネント
"""

import streamlit as st
from PIL import Image

def show_image_uploader():
    """
    画像アップロードUIを表示
    
    Returns:
        PIL.Image: アップロードされた画像
    """
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
    image = None
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
    
    return image
