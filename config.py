"""
設定情報の管理モジュール
システムインストラクション、ページ設定、安全設定などの定数とユーティリティ関数
"""

import os
import streamlit as st
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# ページ設定
PAGE_CONFIG = {
    "page_title": "空間認識オブジェクト検出アプリ",
    "page_icon": "🔍",
    "layout": "wide",
}

# モデル選択オプション
MODEL_OPTIONS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite", 
    "gemini-2.0-pro-exp-02-05", 
    "gemini-1.5-flash-latest"
]

# モデル表示名（日本語説明付き）
MODEL_DISPLAY_NAMES = {
    "gemini-2.0-flash": "Gemini 2.0 Flash (高速・高精度)",
    "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite (軽量版)", 
    "gemini-2.0-pro-exp-02-05": "Gemini 2.0 Pro (高性能)", 
    "gemini-1.5-flash-latest": "Gemini 1.5 Flash (最新版)"
}

# デフォルト設定
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_TEMPERATURE = 0.5
MAX_IMAGE_SIZE = 1024

# API Key取得
def get_api_key():
    """
    環境変数からGoogle API Keyを取得
    
    Returns:
        str: Google API Key
    """
    return os.getenv("GOOGLE_API_KEY", "")

# バウンディングボックスのシステムインストラクション
def get_system_instruction():
    """
    バウンディングボックス用のシステムインストラクションを取得
    
    Returns:
        str: システムインストラクション
    """
    return """
    Return bounding boxes as a JSON array with labels. Never return masks or code fencing. Limit to 25 objects.
    If an object is present multiple times, name them according to their unique characteristic (colors, size, position, unique characteristics, etc..).
    The bounding box coordinates should be normalized between 0 and 1000 in the box_2d array.
    Format: [{"label": "object name", "box_2d": [y1, x1, y2, x2]}, ...]
    """

# 安全設定
def get_safety_settings():
    """
    安全設定を取得
    
    Returns:
        list: 安全設定のリスト
    """
    return [{
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH",
    }]
