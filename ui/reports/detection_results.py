"""
検出結果表示とマークダウンレポート生成コンポーネント
"""

import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
from config import MODEL_DISPLAY_NAMES
from utils import parse_json, plot_bounding_boxes
from ui.utils.markdown_generator import generate_object_detection_report, save_markdown_to_file
from ui.utils.file_utils import get_file_download_link, create_reports_directory

def generate_markdown_report(response_dict, img=None, img_path=None):
    """
    検出結果をマークダウン形式のレポートとして生成する
    
    Args:
        response_dict: モデル名をキーとしたレスポンス辞書
        img: 元画像（PIL Imageオブジェクト、オプション）
        img_path: 元画像のパス（オプション）
        
    Returns:
        str: マークダウン形式のレポート
    """
    # 拡張マークダウン生成ユーティリティを使用
    return generate_object_detection_report(response_dict, img, img_path)

def save_markdown_report(markdown_text, filename=None):
    """
    マークダウンレポートをファイルに保存
    
    Args:
        markdown_text: マークダウンテキスト
        filename: 保存するファイル名（指定がなければタイムスタンプ付きの名前を生成）
    
    Returns:
        str: 保存されたファイルのパス（保存失敗時はNone）
    """
    # レポート保存ディレクトリを作成
    reports_dir = create_reports_directory()
    
    # ファイル名が指定されていない場合は日付付きのファイル名を生成
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detection_report_{timestamp}.md"
    
    # マークダウン保存ユーティリティを使用
    return save_markdown_to_file(markdown_text, filename, reports_dir)

def show_detection_results(response_dict, img_resized, img_path=None):
    """
    検出結果を表示
    
    Args:
        response_dict: モデル名をキーとしたレスポンス辞書
        img_resized: 検出に使用した画像
        img_path: 画像のパス（オプション）
    """
    if not response_dict:
        st.error("APIからの応答がありませんでした")
        return
    
    # タブで各モデルの結果を表示
    tab_labels = ["検出結果"] + list(MODEL_DISPLAY_NAMES.get(model, model) for model in response_dict.keys()) + ["マークダウンレポート"]
    tabs = st.tabs(tab_labels)
    
    # マークダウンレポートを生成
    markdown_report = generate_markdown_report(response_dict, img_resized, img_path)
    
    # 検出結果の概要タブ
    with tabs[0]:
        st.subheader("オブジェクト検出の概要")
        
        total_objects = 0
        all_labels = []
        
        # 各モデルの検出結果を集計
        for model, response in response_dict.items():
            if response and response.text:
                try:
                    json_text = parse_json(response.text)
                    bounding_boxes = json.loads(json_text)
                    model_objects = len(bounding_boxes)
                    total_objects += model_objects
                    
                    st.write(f"- {MODEL_DISPLAY_NAMES.get(model, model)}: {model_objects}個のオブジェクトを検出")
                    
                    # ラベルを収集
                    model_labels = [box.get("label", "不明") for box in bounding_boxes]
                    all_labels.extend(model_labels)
                except:
                    st.write(f"- {MODEL_DISPLAY_NAMES.get(model, model)}: レスポンスの解析に失敗しました")
        
        # 検出されたユニークなラベル一覧
        unique_labels = sorted(set(all_labels))
        if unique_labels:
            st.write(f"\n**検出されたユニークなラベル ({len(unique_labels)}種類):**")
            st.write(", ".join(f"`{label}`" for label in unique_labels))
    
    # 各モデルの結果タブ
    for i, (model, response) in enumerate(response_dict.items(), 1):
        with tabs[i]:
            if response and response.text:
                st.subheader("APIレスポンス")
                st.code(response.text, language="json")
                
                # バウンディングボックスの描画
                try:
                    result_image = plot_bounding_boxes(img_resized, response.text)
                    st.subheader("検出結果")
                    st.image(result_image, caption=f"{MODEL_DISPLAY_NAMES.get(model, model)}による検出結果", use_column_width=True)
                    
                    # 個別のモデル結果をダウンロード
                    single_model_report = generate_markdown_report({model: response}, img_resized, img_path)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{model}_report_{timestamp}.md"
                    
                    st.markdown(
                        get_file_download_link(single_model_report, filename),
                        unsafe_allow_html=True
                    )
                    
                    # 検出されたオブジェクトの数を表示
                    try:
                        json_text = parse_json(response.text)
                        bounding_boxes = json.loads(json_text)
                        st.success(f"{len(bounding_boxes)}個のオブジェクトが検出されました")
                        
                        # 検出されたラベル一覧
                        labels = [box.get("label", "不明") for box in bounding_boxes]
                        st.subheader("検出されたオブジェクト")
                        for i, label in enumerate(labels, 1):
                            st.write(f"{i}. {label}")
                    except Exception as e:
                        st.warning(f"検出オブジェクトのカウントに失敗しました: {e}")
                except Exception as e:
                    st.error(f"バウンディングボックスの描画に失敗しました: {e}")
            else:
                st.error(f"{MODEL_DISPLAY_NAMES.get(model, model)}からの応答がありませんでした")
    
    # マークダウンレポートタブ
    with tabs[-1]:
        st.subheader("マークダウンレポート")
        st.markdown(markdown_report)
        
        # レポート保存とダウンロードのセクション
        st.subheader("レポートの保存とダウンロード")
        
        col1, col2 = st.columns([1, 2])
        
        # ファイル名入力フィールド
        with col1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"detection_report_{timestamp}.md"
            custom_filename = st.text_input("ファイル名", default_filename)
        
        # ローカル保存ボタン
        with col2:
            if st.button("ローカルに保存"):
                saved_path = save_markdown_report(markdown_report, custom_filename)
                if saved_path:
                    st.success(f"レポートを保存しました: {saved_path}")
        
        # レポートのダウンロードリンク
        st.markdown("### ダウンロード")
        st.markdown(
            get_file_download_link(markdown_report, custom_filename),
            unsafe_allow_html=True
        )
        
        # 元の検出画像を含むZIPファイルのダウンロードも可能にする機能も将来的に追加可能
        
        # クリップボードにコピーするためのコードブロック
        st.subheader("マークダウンソース")
        st.code(markdown_report, language="markdown")
        st.caption("上記のコードブロックからマークダウンテキストをコピーできます")
