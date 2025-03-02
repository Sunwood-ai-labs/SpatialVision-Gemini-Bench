"""
ヘッダーレイアウトコンポーネント
"""

import streamlit as st

def show_header():
    """
    アプリケーションのヘッダーを表示
    """
    st.markdown(
        """
<div align="center">

# SpatialVision-Gemini-Bench

</div>

        """,
        unsafe_allow_html=True
    )
