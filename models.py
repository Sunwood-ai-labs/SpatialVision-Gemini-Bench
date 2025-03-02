"""
Gemini APIモデル関連のモジュール
APIクライアントの初期化、画像処理、推論処理などを管理
"""

from PIL import Image
from google.genai import Client
from google.genai import types
import streamlit as st
from io import BytesIO
import asyncio
import time

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
        image: PILのImageオブジェクトまたはバイト配列
        
    Returns:
        PIL.Image: リサイズされた画像オブジェクト
    """
    # バイト型の場合はPIL.Imageに変換
    if isinstance(image, bytes):
        image = Image.open(BytesIO(image))
        
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
        image: PILのImageオブジェクトまたはバイト配列
        temperature: 生成の多様性制御パラメータ
        
    Returns:
        APIレスポンス
    """
    # バウンディングボックスを取得
    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            system_instruction=get_system_instruction(),
            temperature=temperature,
            safety_settings=get_safety_settings(),
        )
    )
    
    return response

def detect_objects_with_multiple_models(client, model_names, prompt, image, temperature=0.5):
    """
    複数のモデルを使用して画像内のオブジェクトを検出
    
    Args:
        client: Gemini APIクライアント
        model_names: 使用するモデル名のリスト
        prompt: プロンプトテキスト
        image: PILのImageオブジェクトまたはバイト配列
        temperature: 生成の多様性制御パラメータ
        
    Returns:
        dict: モデル名をキーとしたAPIレスポンスの辞書
    """
    results = {}
    errors = []
    progress_text = st.empty()
    progress_bar = st.progress(0)
    total_models = len(model_names)
    
    for i, model_name in enumerate(model_names):
        progress = (i / total_models)
        progress_bar.progress(progress)
        progress_text.text(f"モデル {i+1}/{total_models}: {model_name} で検出中...")
        
        try:
            response = detect_objects(client, model_name, prompt, image, temperature)
            results[model_name] = response
        except Exception as e:
            error_msg = f"{model_name}での検出に失敗しました: {str(e)}"
            st.error(error_msg)
            errors.append(error_msg)
            results[model_name] = None
        
        # APIレート制限に配慮して少し待機
        if i < total_models - 1:
            time.sleep(1)
    
    progress_bar.progress(1.0)
    progress_text.text("すべてのモデルでの検出が完了しました")
    
    # エラーの要約を表示
    if errors:
        st.warning(f"{len(errors)}個のモデルでエラーが発生しました。詳細はログを確認してください。")
    
    return results
