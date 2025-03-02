"""
UIモジュールパッケージ
StreamlitのUIコンポーネントを管理する
"""

# レイアウト
from ui.layouts.header import show_header
from ui.layouts.sidebar import show_sidebar
from ui.layouts.footer import show_footer

# コンポーネント
from ui.components.image_selector import show_sample_image_selector
from ui.components.image_uploader import show_image_uploader

# レポート
from ui.reports.detection_results import show_detection_results, generate_markdown_report, save_markdown_report

# ユーティリティ
from ui.utils.image_processing import plot_bounding_boxes, parse_json
from ui.utils.file_utils import save_text_file, generate_filename
from ui.utils.markdown_generator import (
    generate_object_detection_report,
    generate_comparison_report,
    save_markdown_to_file
)

# すべてのコンポーネントをエクスポート
__all__ = [
    'show_header',
    'show_sidebar',
    'show_footer',
    'show_sample_image_selector',
    'show_image_uploader',
    'show_detection_results',
    'generate_markdown_report',
    'save_markdown_report',
    'plot_bounding_boxes',
    'parse_json',
    'save_text_file',
    'generate_filename',
    'generate_object_detection_report',
    'generate_comparison_report',
    'save_markdown_to_file'
]
