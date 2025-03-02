"""
Gemini APIモデル関連のモジュール
APIクライアントの初期化、画像処理、推論処理などを管理
"""

from PIL import Image
import google.generativeai as genai
from google.genai import Client
from google.generativeai import types
import streamlit as st

from config import get_system_instruction, get_safety_settings, MAX_IMAGE_SIZE

@st.cache_resource
def get_genai_client(api_key):
    """
    Gemini APIクライアントを取得
    
    Args:
        api_key: Google API Key
        
    Returns:
        初期化されたクライアントインスタンス
    
    Raises:
        Exception: API初期化に失敗した場合
    """
    if not api_key:
        st.error("有効なAPI Keyを入力してください")
        st.stop()
    
    try:
        client = Client(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"APIクライアントの初期化に失敗しました: {e}")
        st.stop()

def resize_image(image):
    """
    画像をAPIに適したサイズにリサイズ
    
    Args:
        image: PILのImageオブジェクト
        
    Returns:
        リサイズされたImageオブジェクト
    """
    img_resized = image.copy()
    if max(img_resized.size) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(img_resized.size)
        new_size = (int(img_resized.size[0] * ratio), int(img_resized.size[1] * ratio))
        img_resized = img_resized.resize(new_size, Image.Resampling.LANCZOS)
    return img_resized

def detect_objects(client, model_name, prompt, image, temperature=0.5):
    """
    画像内のオブジェクトを検出
    
    Args:
        client: Gemini APIクライアント
        model_name: 使用するモデル名
        prompt: プロンプトテキスト
        image: PILのImageオブジェクト
        temperature: 生成の多様性制御パラメータ
        
    Returns:
        APIレスポンス
    """
    # 画像をリサイズ
    img_resized = resize_image(image)
    
    # バウンディングボックスを取得
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, img_resized],
        config=types.GenerateContentConfig(
            system_instruction=get_system_instruction(),
            temperature=temperature,
            safety_settings=get_safety_settings(),
        )
    )
    
    return response
