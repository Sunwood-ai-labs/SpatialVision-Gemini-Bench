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
import json
import traceback
from loguru import logger

from debug_utils import log_api_call, timer_decorator, log_memory_usage
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
        logger.info("Gemini APIクライアントを初期化中...")
        client = Client(api_key=api_key)
        logger.success("Gemini APIクライアントの初期化に成功しました")
        return client
    except Exception as e:
        error_msg = f"APIクライアントの初期化に失敗しました: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        st.error(error_msg)
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
    logger.debug(f"元の画像サイズ: {img_resized.size}")
    
    if max(img_resized.size) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(img_resized.size)
        new_size = (int(img_resized.size[0] * ratio), int(img_resized.size[1] * ratio))
        logger.info(f"画像をリサイズします: {img_resized.size} -> {new_size}")
        img_resized = img_resized.resize(new_size, Image.Resampling.LANCZOS)
    
    return img_resized

@timer_decorator
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
    log_api_call(model_name, "バウンディングボックス検出開始")
    logger.debug(f"プロンプト: {prompt}")
    logger.debug(f"温度設定: {temperature}")
    
    try:
        # システムインストラクションを取得
        system_instruction = get_system_instruction()
        logger.debug(f"システムインストラクション: {system_instruction}")
        
        # バウンディングボックスを取得
        log_api_call(model_name, "API呼び出し開始")
        log_memory_usage()
        
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                safety_settings=get_safety_settings(),
            )
        )
        
        logger.success(f"[{model_name}] APIレスポンス受信完了")
        
        # レスポンスの検証（ログ用）
        try:
            response_text = response.text
            logger.debug(f"レスポンスのテキスト長: {len(response_text)} 文字")
            
            # JSONが含まれているか検証
            if response_text.find('{') >= 0 and response_text.find('}') >= 0:
                logger.info(f"[{model_name}] JSONデータを含むレスポンスを受信")
            else:
                logger.warning(f"[{model_name}] レスポンスにJSONデータが含まれていない可能性があります")
                logger.debug(f"レスポンス先頭100文字: {response_text[:100]}...")
        except Exception as e:
            logger.error(f"レスポンス解析中のエラー: {e}")
        
        return response
    
    except Exception as e:
        error_msg = f"API呼び出し中にエラーが発生しました: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise

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
    
    logger.info(f"複数モデル処理を開始: {', '.join(model_names)}")
    
    for i, model_name in enumerate(model_names):
        progress = (i / total_models)
        progress_bar.progress(progress)
        progress_message = f"モデル {i+1}/{total_models}: {model_name} で検出中..."
        progress_text.text(progress_message)
        logger.info(progress_message)
        
        try:
            # メモリ使用状況ログ
            log_memory_usage()
            
            # モデル処理開始
            log_api_call(model_name, f"処理開始 ({i+1}/{total_models})")
            
            # モデル呼び出しとタイミング計測
            response, duration = detect_objects(client, model_name, prompt, image, temperature)
            
            # 処理完了ログ
            log_api_call(model_name, f"処理完了 ({i+1}/{total_models})", duration, "完了")
            
            results[model_name] = response
        except Exception as e:
            error_msg = f"{model_name}での検出に失敗しました: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            st.error(error_msg)
            errors.append(error_msg)
            results[model_name] = None
        
        # APIレート制限に配慮して少し待機
        if i < total_models - 1:
            logger.info(f"APIレート制限を考慮して1秒待機中...")
            time.sleep(1)
    
    progress_bar.progress(1.0)
    completion_message = "すべてのモデルでの検出が完了しました"
    progress_text.text(completion_message)
    logger.success(completion_message)
    
    # エラーの要約を表示
    if errors:
        error_summary = f"{len(errors)}個のモデルでエラーが発生しました。詳細はログを確認してください。"
        logger.warning(error_summary)
        st.warning(error_summary)
    
    # 結果の概要をログに記録
    for model, response in results.items():
        if response:
            logger.info(f"[{model}] 正常に結果を受信")
        else:
            logger.warning(f"[{model}] 結果が取得できませんでした")
    
    return results
