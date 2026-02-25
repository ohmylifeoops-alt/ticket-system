import streamlit as st
import pandas as pd
import os

# 1. 頁面基本配置
st.set_page_config(page_title="VIP 座位系統", layout="wide")

# 2. 設定資料庫路徑
DB_PATH = "排桌.xlsx - 工作表1.csv"

# 3. 自定義 CSS 樣式
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
    </style>
    """, unsafe_allow_html=True)

# 4. 資料載入函式 (修正縮排問題)
def load_data():
    if os.path.exists(DB_PATH):
        try:
            # 優先嘗試 utf-8-sig
            return pd.read_csv(DB_PATH, encoding='utf-8-sig')
        except:
            try:
                # 若失敗則嘗試 big5 (繁體中文)
                return pd.read_csv(DB_PATH, encoding='big5')
            except:
                return None
    return None

# 初始化資料
if 'df' not in st.session_state or st.session_state.df is None:
    st.session_state.df = load_data()

# 5. UI 分頁設計
tab_map, tab_database, tab_files = st.tabs(["📍 現場桌次圖", "📋 資料庫總表", "⚙️ 檔案管理"])

# --- 頁籤一：現場桌次圖 ---
with tab_map:
    st.title("🏟️ VIP 現場桌次分佈")
    if st.session_state.df is not None:
        df = st.session_state.df
        target_vip = st.radio("切換區域：", ["VIP1", "VIP2", "VIP3"], horizontal=True)
        
        filtered_df = df[df['VIP_Level'] == target_vip]
        
        if not filtered_df.empty:
            # 核心：依「桌號」分組，完美解決非連號
            tables = filtered_df.groupby('Table_No')
            num_cols = 4
            cols = st.columns(num_cols)
            
            for i, (table_no, group) in enumerate(tables):
                with cols[i % num_cols]:
                    seat_html = ""
                    for _, row in group.iterrows():
                        seat_html += f'<div class="seat-item">💺 座號 {row["Seat_ID"]} - {row["Name"]}</div>'
                    
                    st.markdown(f"""
                        <div class="table-card">
                            <div class="table-header">第 {table_no} 桌</div>
                            {seat_html}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info(f"目前 {target_vip} 區域內沒有任何座位資料。")
    else:
        st.error(f"❌ 找不到預設檔案：{DB_PATH}")

# --- 頁籤二：資料庫總表 ---
with tab_database:
    st.title("📋 資料庫完整清單")
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df, use_container_width=True, height=600)

# --- 頁籤三：檔案管理 ---
with tab_files:
    st.title("⚙️ 數據管理")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📤 更新/上傳檔案")
        new_file = st.file_uploader("選取 CSV 檔案", type=["csv"])
        if new_file:
            try:
                new_df = pd.read_csv(new_file, encoding='utf-8-sig')
            except:
                new_df = pd.read_csv(new_file, encoding='big5')
            
            new_df.to_csv(DB_PATH, index=False, encoding='utf-8-sig')
            st.session_state.df = new_df
            st.success("檔案已更新！請回地圖頁查看。")
            st.rerun() # 自動重新整理頁面

    with col_b:
        st.subheader("📥 備份下載")
        if st.session_state.df is not None:
            csv_data = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("點擊下載目前資料庫", csv_data, "backup_seats.csv", "text/csv")