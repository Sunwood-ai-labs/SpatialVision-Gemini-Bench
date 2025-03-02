"""
デバッグユーティリティモジュール
アプリケーションの処理進捗をログで可視化するためのユーティリティ
"""

import os
import sys
import time
from loguru import logger

# ログファイル設定
LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOG_DIR, "gemini_processing.log")

# ログディレクトリが存在しない場合は作成
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ロガー設定
logger.remove()  # デフォルト設定をクリア
logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add(LOG_FILE, rotation="10 MB", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}")

def log_api_call(model_name, step, duration=None, status="実行中"):
    """
    API呼び出しの進捗をログに記録
    
    Args:
        model_name: 使用しているモデル名
        step: 現在のステップ
        duration: 処理時間（秒）
        status: ステータス（実行中/完了/エラー）
    """
    if duration:
        logger.info(f"[{model_name}] {step} - {status} (所要時間: {duration:.2f}秒)")
    else:
        logger.info(f"[{model_name}] {step} - {status}")

def timer_decorator(func):
    """
    関数の実行時間を計測するデコレータ
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        return result, duration
    return wrapper

def log_memory_usage():
    """
    現在のメモリ使用量をログに記録
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        logger.debug(f"現在のメモリ使用量: {memory_usage_mb:.2f} MB")
    except ImportError:
        logger.debug("psutilがインストールされていません。メモリ使用量は記録されません。")
