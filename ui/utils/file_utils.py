"""
ファイル操作ユーティリティ
"""

import os
import base64
import io
from PIL import Image
import streamlit as st
from datetime import datetime

def ensure_directory_exists(directory):
    """ディレクトリが存在しない場合は作成する"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_filename(prefix="file", extension=".txt", include_timestamp=True):
    """
    タイムスタンプを含むファイル名を生成する
    
    Args:
        prefix: ファイル名の接頭辞
        extension: ファイル拡張子（ドット付き）
        include_timestamp: タイムスタンプを含めるかどうか
        
    Returns:
        str: 生成されたファイル名
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}{extension}"
    else:
        return f"{prefix}{extension}"

def get_file_size(file_path):
    """
    ファイルサイズを取得して適切な単位で表示する
    
    Args:
        file_path: ファイルのパス
        
    Returns:
        str: ファイルサイズの文字列（単位付き）
    """
    if not os.path.exists(file_path):
        return "ファイルが存在しません"
    
    size_bytes = os.path.getsize(file_path)
    
    # 適切な単位を選択
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

def save_text_file(text_content, file_path):
    """
    テキストコンテンツをファイルに保存
    
    Args:
        text_content: 保存するテキスト内容
        file_path: 保存先のファイルパス
        
    Returns:
        bool: 保存が成功したかどうか
    """
    try:
        # ディレクトリが存在するか確認
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # テキストファイルに書き込み
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text_content)
            
        return True
    except Exception as e:
        st.error(f"ファイル保存エラー: {e}")
        return False

def load_image(file_path):
    """
    画像ファイルをPIL Imageとして読み込む
    
    Args:
        file_path: 画像ファイルのパス
        
    Returns:
        PIL.Image: 読み込まれた画像、エラー時はNone
    """
    try:
        return Image.open(file_path)
    except Exception as e:
        st.error(f"画像読み込みエラー: {e}")
        return None

def create_reports_directory():
    """
    レポート保存用ディレクトリを作成
    
    Returns:
        str: レポートディレクトリのパス
    """
    reports_dir = os.path.join(os.getcwd(), "reports")
    ensure_directory_exists(reports_dir)
    return reports_dir

def get_image_as_base64(image):
    """
    PIL Imageオブジェクトをbase64エンコードされた文字列に変換
    
    Args:
        image: PIL Imageオブジェクト
        
    Returns:
        str: base64エンコードされた画像文字列
    """
    if image is None:
        return ""
        
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        st.error(f"画像変換エラー: {e}")
        return ""

def save_image(image, file_path):
    """
    PIL Imageオブジェクトをファイルに保存
    
    Args:
        image: PIL Imageオブジェクト
        file_path: 保存先のファイルパス
        
    Returns:
        bool: 保存が成功したかどうか
    """
    try:
        # ディレクトリが存在するか確認
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # 画像を保存
        image.save(file_path)
        
        return True
    except Exception as e:
        st.error(f"画像保存エラー: {e}")
        return False

def get_file_download_link(file_content, filename, button_text=None):
    """
    ファイルコンテンツをダウンロードするためのリンクHTMLを生成
    
    Args:
        file_content: ファイルの内容（テキスト）
        filename: ダウンロード時のファイル名
        button_text: ダウンロードボタンのテキスト（指定なしの場合はファイル名を使用）
        
    Returns:
        str: ダウンロードリンクのHTML
    """
    if button_text is None:
        button_text = f"📥 {filename} をダウンロード"
        
    # テキストをUTF-8バイトエンコード
    file_bytes = file_content.encode()
    
    # BASE64にエンコード
    b64 = base64.b64encode(file_bytes).decode()
    
    # ダウンロードリンクのHTML生成
    download_link = f"""
    <a href="data:text/plain;base64,{b64}" download="{filename}" 
       style="
           background-color: #4CAF50;
           color: white;
           padding: 10px 15px;
           text-align: center;
           text-decoration: none;
           display: inline-block;
           font-size: 14px;
           margin: 4px 2px;
           cursor: pointer;
           border-radius: 5px;
       ">
        {button_text}
    </a>
    """
    return download_link

def get_binary_file_download_link(file_content, filename, mime_type, button_text=None):
    """
    バイナリファイルコンテンツをダウンロードするためのリンクHTMLを生成
    
    Args:
        file_content: ファイルの内容（バイナリ）
        filename: ダウンロード時のファイル名
        mime_type: ファイルのMIMEタイプ (例: 'image/png', 'application/pdf')
        button_text: ダウンロードボタンのテキスト（指定なしの場合はファイル名を使用）
        
    Returns:
        str: ダウンロードリンクのHTML
    """
    if button_text is None:
        button_text = f"📥 {filename} をダウンロード"
        
    # バイナリデータをBASE64エンコード
    b64 = base64.b64encode(file_content).decode()
    
    # ダウンロードリンクのHTML生成
    download_link = f"""
    <a href="data:{mime_type};base64,{b64}" download="{filename}" 
       style="
           background-color: #4CAF50;
           color: white;
           padding: 10px 15px;
           text-align: center;
           text-decoration: none;
           display: inline-block;
           font-size: 14px;
           margin: 4px 2px;
           cursor: pointer;
           border-radius: 5px;
       ">
        {button_text}
    </a>
    """
    return download_link
