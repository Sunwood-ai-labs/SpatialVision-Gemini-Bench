"""
画像処理ユーティリティ関数
"""

import json
import io
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageColor
import numpy as np
import random
import streamlit as st

def get_color_list():
    """バウンディングボックス描画用のカラーリストを取得する"""
    # プロジェクト用カスタムカラーマップ
    custom_colors = [
        '#7D4EBF',  # 紫
        '#52378C',  # 濃い紫
        '#352559',  # 暗い紫
        '#0F5C8C',  # 青
        '#092B40',  # 暗い青
    ]
    
    # 基本色（バックアップとして保持）
    basic_colors = [
        'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple',
        'brown', 'gray', 'beige', 'turquoise', 'cyan', 'magenta',
        'lime', 'navy', 'maroon', 'teal', 'olive', 'coral',
        'lavender', 'violet', 'gold', 'silver',
    ]
    
    # カスタムカラーを優先的に使用
    return custom_colors + basic_colors

def parse_json(json_output):
    """マークダウンフェンシングからJSONを抽出する"""
    try:
        # 最初にJSON形式として解析を試みる
        json.loads(json_output)
        return json_output
    except json.JSONDecodeError:
        # JSONとして解析できない場合、マークダウンフェンシングを解析
        lines = json_output.splitlines()
        for i, line in enumerate(lines):
            if line == "```json" or line == "```":
                json_output = "\n".join(lines[i+1:])  # "```json"より前のすべてを削除
                json_output = json_output.split("```")[0]  # 閉じる"```"の後のすべてを削除
                break  # "```json"が見つかったらループを終了
        return json_output

def plot_bounding_boxes(img, bounding_boxes_text, font_path=None):
    """
    バウンディングボックスを画像に描画する
    
    Args:
        img: PIL Image オブジェクト
        bounding_boxes_text: バウンディングボックス情報を含むテキスト
        font_path: フォントパスの指定（オプション）
    
    Returns:
        バウンディングボックスが描画されたPIL Imageオブジェクト
    """
    # 画像のコピーを作成
    img_with_boxes = img.copy()
    width, height = img_with_boxes.size
    
    # 描画オブジェクトを作成
    draw = ImageDraw.Draw(img_with_boxes)
    
    # 色のリストを取得
    colors = get_color_list()
    # モデル間の結果比較の際にも同じ識別子には同じ色を使用するため、シードを固定
    random.seed(42)
    random.shuffle(colors)
    
    # マークダウンフェンシングを解析
    json_text = parse_json(bounding_boxes_text)
    
    try:
        # フォントの設定
        try:
            if font_path:
                font = ImageFont.truetype(font_path, size=14)
            else:
                # Linuxの一般的な日本語フォントパスを試す
                font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", size=14)
        except IOError:
            # フォントが見つからない場合はデフォルトフォントを使用
            font = ImageFont.load_default()
        
        # バウンディングボックスを描画
        bounding_boxes = json.loads(json_text)
        for i, bbox in enumerate(bounding_boxes):
            # 色の選択
            color = colors[i % len(colors)]
            
            # 正規化された座標を絶対座標に変換
            abs_y1 = int(bbox["box_2d"][0]/1000 * height)
            abs_x1 = int(bbox["box_2d"][1]/1000 * width)
            abs_y2 = int(bbox["box_2d"][2]/1000 * height)
            abs_x2 = int(bbox["box_2d"][3]/1000 * width)
            
            # x1とx2、y1とy2が逆転している場合は入れ替え
            if abs_x1 > abs_x2:
                abs_x1, abs_x2 = abs_x2, abs_x1
            if abs_y1 > abs_y2:
                abs_y1, abs_y2 = abs_y2, abs_y1
            
            # バウンディングボックスを描画
            draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=3)
            
            # ラベルを描画
            if "label" in bbox:
                # ラベルの背景を描画
                text_width, text_height = draw.textbbox((0, 0), bbox["label"], font=font)[2:]
                draw.rectangle(
                    ((abs_x1, abs_y1 - text_height - 4), (abs_x1 + text_width + 8, abs_y1)),
                    fill=color
                )
                # ラベルテキストを描画
                draw.text((abs_x1 + 4, abs_y1 - text_height - 2), bbox["label"], fill="white", font=font)
        
        return img_with_boxes
    
    except Exception as e:
        st.error(f"バウンディングボックスの描画中にエラーが発生しました: {e}")
        return img  # エラーが発生した場合は元の画像を返す
