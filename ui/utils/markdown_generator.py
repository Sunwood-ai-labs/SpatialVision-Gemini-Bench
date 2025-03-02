"""
マークダウンレポート生成ユーティリティ
"""

import json
import os
import base64
from datetime import datetime
import streamlit as st
from config import MODEL_DISPLAY_NAMES
from ui.utils.image_processing import parse_json
from ui.utils.file_utils import get_image_as_base64, save_image, create_reports_directory

def generate_object_detection_report(response_dict, img=None, img_path=None, include_raw_json=True):
    """
    オブジェクト検出結果をマークダウン形式のレポートとして生成する
    
    Args:
        response_dict: モデル名をキーとしたレスポンス辞書
        img: 元画像（PIL Imageオブジェクト、オプション）
        img_path: 元画像のパス（オプション）
        include_raw_json: 生のJSONレスポンスを含めるかどうか
        
    Returns:
        str: マークダウン形式のレポート
    """
    if not response_dict:
        return "# ❌ 検出結果\n\nAPIからの応答がありませんでした。"
    
    # 現在の日時
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # レポートのヘッダー
    md = f"# 🔍 Gemini オブジェクト検出レポート\n\n"
    md += f"**生成日時**: {now}\n\n"
    
    if img_path:
        md += f"**対象画像**: `{img_path}`\n\n"
    
    # 画像を埋め込む
    if img:
        # 画像をローカルに保存
        reports_dir = create_reports_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_filename = f"original_image_{timestamp}.png"
        img_path = os.path.join(reports_dir, img_filename)
        save_image(img, img_path)
        
        # 相対パスを使用したマークダウンリンク
        md += "## 元画像\n\n"
        md += f"![元画像]({img_path})\n\n"
        md += f"*画像を保存しました: `{img_path}`*\n\n"
    
    # サマリーセクション
    md += "## 📋 検出結果サマリー\n\n"
    md += "| モデル | 検出オブジェクト数 | 検出ラベル |\n"
    md += "|--------|-------------------|------------|\n"
    
    # 各モデルの結果をサマリーに追加
    for model, response in response_dict.items():
        model_display = MODEL_DISPLAY_NAMES.get(model, model)
        if response and response.text:
            try:
                json_text = parse_json(response.text)
                bounding_boxes = json.loads(json_text)
                obj_count = len(bounding_boxes)
                labels = sorted(set(box.get("label", "不明") for box in bounding_boxes))
                md += f"| {model_display} | {obj_count} | {', '.join(labels)} |\n"
            except:
                md += f"| {model_display} | エラー | - |\n"
        else:
            md += f"| {model_display} | データなし | - |\n"
    
    md += "\n"
    
    # 各モデルの詳細結果
    for model, response in response_dict.items():
        # モデル名のヘッダー
        md += f"## 📊 {MODEL_DISPLAY_NAMES.get(model, model)} の検出結果\n\n"
        
        if not response or not response.text:
            md += "このモデルからの応答がありませんでした。\n\n"
            continue
        
        try:
            # JSONテキストを解析
            json_text = parse_json(response.text)
            bounding_boxes = json.loads(json_text)
            
            # 検出されたオブジェクト数
            obj_count = len(bounding_boxes)
            md += f"### 検出オブジェクト: {obj_count}個\n\n"
            
            # 検出されたオブジェクトの一覧表
            md += "| No. | ラベル | 座標 (y1, x1, y2, x2) | 信頼度 |\n"
            md += "|-----|--------|----------------------|--------|\n"
            
            for i, box in enumerate(bounding_boxes, 1):
                # 座標を1000で正規化された形式で表示
                coords = box.get("box_2d", [0, 0, 0, 0])
                coords_str = f"({coords[0]}, {coords[1]}, {coords[2]}, {coords[3]})"
                
                # 信頼度（あれば）
                confidence = box.get("confidence", "N/A")
                confidence_str = f"{confidence:.2f}" if isinstance(confidence, (int, float)) else "N/A"
                
                md += f"| {i} | {box.get('label', '不明')} | {coords_str} | {confidence_str} |\n"
            
            md += "\n"
            
            # JSONレスポンス全体（オプション）
            if include_raw_json:
                md += "### 生のJSONレスポンス\n\n"
                md += "```json\n"
                md += json_text
                md += "\n```\n\n"
            
        except Exception as e:
            md += f"⚠️ レスポンスの解析中にエラーが発生しました: {e}\n\n"
            md += "### 生のレスポンステキスト\n\n"
            md += "```\n"
            md += response.text
            md += "\n```\n\n"
    
    # 注意書き
    md += "---\n\n"
    md += "**注意**: バウンディングボックスの座標は0〜1000の範囲で正規化されています。\n"
    md += "実際の画像サイズに変換するには、以下の計算を行ってください：\n"
    md += "- y座標 = y値 × 画像の高さ ÷ 1000\n"
    md += "- x座標 = x値 × 画像の幅 ÷ 1000\n"
    
    return md

def generate_comparison_report(results_dict1, results_dict2, img=None, img_path=None, comparison_title="モデル比較レポート"):
    """
    2つの検出結果を比較するマークダウンレポートを生成する
    
    Args:
        results_dict1: 1つ目の結果辞書
        results_dict2: 2つ目の結果辞書
        img: 元画像（PIL Imageオブジェクト、オプション）
        img_path: 元画像のパス（オプション）
        comparison_title: 比較レポートのタイトル
        
    Returns:
        str: マークダウン形式の比較レポート
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # レポートのヘッダー
    md = f"# 📊 {comparison_title}\n\n"
    md += f"**生成日時**: {now}\n\n"
    
    if img_path:
        md += f"**対象画像**: `{img_path}`\n\n"
    
    # 画像を埋め込む
    if img:
        # 画像をローカルに保存
        reports_dir = create_reports_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_filename = f"comparison_image_{timestamp}.png"
        img_path = os.path.join(reports_dir, img_filename)
        save_image(img, img_path)
        
        # 相対パスを使用したマークダウンリンク
        md += "## 元画像\n\n"
        md += f"![元画像]({img_path})\n\n"
        md += f"*画像を保存しました: `{img_path}`*\n\n"
    
    # 結果1のサマリー
    model1 = list(results_dict1.keys())[0]
    md += f"## 🔹 モデル1: {MODEL_DISPLAY_NAMES.get(model1, model1)}\n\n"
    
    try:
        response1 = results_dict1[model1]
        if response1 and response1.text:
            json_text1 = parse_json(response1.text)
            boxes1 = json.loads(json_text1)
            md += f"- 検出オブジェクト数: {len(boxes1)}個\n"
            
            # ラベル一覧
            labels1 = sorted(set(box.get("label", "不明") for box in boxes1))
            md += f"- 検出ラベル: {', '.join(labels1)}\n\n"
        else:
            md += "- データなし\n\n"
    except Exception as e:
        md += f"- エラー: {e}\n\n"
    
    # 結果2のサマリー
    model2 = list(results_dict2.keys())[0]
    md += f"## 🔸 モデル2: {MODEL_DISPLAY_NAMES.get(model2, model2)}\n\n"
    
    try:
        response2 = results_dict2[model2]
        if response2 and response2.text:
            json_text2 = parse_json(response2.text)
            boxes2 = json.loads(json_text2)
            md += f"- 検出オブジェクト数: {len(boxes2)}個\n"
            
            # ラベル一覧
            labels2 = sorted(set(box.get("label", "不明") for box in boxes2))
            md += f"- 検出ラベル: {', '.join(labels2)}\n\n"
        else:
            md += "- データなし\n\n"
    except Exception as e:
        md += f"- エラー: {e}\n\n"
    
    # 比較結果
    md += "## 🔄 比較分析\n\n"
    
    try:
        if response1 and response1.text and response2 and response2.text:
            labels1_set = set(labels1)
            labels2_set = set(labels2)
            
            # 共通のラベル
            common_labels = labels1_set.intersection(labels2_set)
            if common_labels:
                md += f"### 共通で検出されたラベル ({len(common_labels)}個)\n"
                md += ", ".join(sorted(common_labels)) + "\n\n"
            
            # モデル1のみのラベル
            only_model1 = labels1_set - labels2_set
            if only_model1:
                md += f"### {MODEL_DISPLAY_NAMES.get(model1, model1)}のみが検出したラベル ({len(only_model1)}個)\n"
                md += ", ".join(sorted(only_model1)) + "\n\n"
            
            # モデル2のみのラベル
            only_model2 = labels2_set - labels1_set
            if only_model2:
                md += f"### {MODEL_DISPLAY_NAMES.get(model2, model2)}のみが検出したラベル ({len(only_model2)}個)\n"
                md += ", ".join(sorted(only_model2)) + "\n\n"
    except Exception as e:
        md += f"比較分析中にエラーが発生しました: {e}\n\n"
    
    return md

def save_markdown_to_file(markdown_text, filename=None, directory=None):
    """
    マークダウンテキストをファイルに保存する
    
    Args:
        markdown_text: 保存するマークダウンテキスト
        filename: ファイル名（指定がなければタイムスタンプ付きの名前を生成）
        directory: 保存先ディレクトリ（指定がなければreportsディレクトリを使用）
    
    Returns:
        str: 保存されたファイルのパス
    """
    try:
        # レポート保存用ディレクトリ
        if directory is None:
            directory = create_reports_directory()
        else:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # ファイル名の生成
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_report_{timestamp}.md"
        
        # ファイルパスの生成
        filepath = os.path.join(directory, filename)
        
        # ファイルに書き込み
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        return filepath
    except Exception as e:
        if st:  # Streamlitが利用可能な場合
            st.error(f"レポート保存中にエラーが発生しました: {e}")
        print(f"レポート保存中にエラーが発生しました: {e}")
        return None
