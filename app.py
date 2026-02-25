import streamlit as st
import pandas as pd
import os

# 1. 頁面基本配置
st.set_page_config(page_title="VIP 座位系統", layout="wide")

# 2. 設定資料庫路徑 (這就是你剛才確認的檔名)
DB_PATH = "排桌.xlsx - 工作表1.csv"

# 3. 自定義 CSS 樣式：美化桌位方塊，模擬現場桌圖感
st.markdown("""
    <style>
    .table-card {
        border: 2px solid #2E86C1;
        border-radius: 15px;
        padding: 15px;
        background-color: #F4F9FD;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        min-height: 150px;
    }
    .table-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1B4F72;
        border-bottom: 2px solid #AED6F1;
        margin-bottom: 10px;
        padding-bottom: 5px;
    }
    .seat-item {
        font-size: 1rem;
        text-align: left;
        color: #2C3E50;
        margin: 5px 0;
        padding: 2px 8px;
        background: white;
        border-radius: 5px;
        border: 1px solid #D6DBDF;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-top: 10px;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 資料載入函式：自動偵測編碼，防止讀取中文 CSV 失敗
def load_data():
    if os.path.exists(DB_PATH):
        try:
            # 優先嘗試 utf-8