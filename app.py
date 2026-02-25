import streamlit as st
import pandas as pd
import os

# 頁面配置
st.set_page_config(page_title="VIP 席位配置系統", layout="wide")

# 定義預設資料庫路徑 (請確保你的檔案夾中有這個檔案，或名稱正確)
DB_PATH = "ticket_system_db.csv" 

# 自定義桌位 CSS
st.markdown("""
    <style>
    .table-card {
        border: 2px solid #2E86C1;
        border-radius: 12px;
        padding: 15px;
        background-color: #EBF5FB;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .table-header {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1B4F72;
        border-bottom: 2px solid #AED6F1;
        margin-bottom: 10px;
    }
    .seat-item {
        font-size: 0.95rem;
        text-align: left;
        color: #212F3C;
        margin: 3px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# 資料讀取邏輯：自動連結原有資料庫
# ----------------------------------------------------------------
def load_data():
    if os.path.exists(DB_PATH):
        return pd.read_csv(DB_PATH)
    return None

# 初始化資料
if 'df' not in st.session_state or st.session_state.df is None:
    st.session_state.df = load_data()

# ----------------------------------------------------------------
# UI 分頁設計
# ----------------------------------------------------------------
tab_map, tab_database, tab_files = st.tabs(["📍 現場桌次圖", "📋 資料庫總表", "⚙️ 檔案管理"])

# 頁籤一：現場桌次圖 (首頁)
with tab_map:
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # 確保必要欄位存在
        required_cols = ['VIP_Level', 'Table_No', 'Seat_ID', 'Name']
        if all(col in df.columns for col in required_cols):
            
            target_vip = st.radio("選擇區域：", ["VIP1", "VIP2", "VIP3"], horizontal=True)
            filtered_df = df[df['VIP_Level'] == target_vip]
            
            # 關鍵：依桌號分組，解決非連號顯示
            tables = filtered_df.groupby('Table_No')
            
            st.subheader(f"🏟️ {target_vip} 區座次分佈 (已自動連結資料庫)")
            
            num_cols = 4
            cols = st.columns(num_cols)
            
            for i, (table_no, group) in enumerate(tables):
                with cols[i % num_cols]:
                    seat_html = "".join([f'<div class="seat-item">💺 {row["Seat_ID"]} - {row["Name"]}</div>' for _, row in group.iterrows()])
                    st.markdown(f"""
                        <div class="table-card">
                            <div class="table-header">第 {table_no} 桌</div>
                            {seat_html}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.error(f"資料庫格式不符，缺少必要欄位：{required_cols}")
    else:
        st.warning(f"⚠️ 找不到預設資料庫檔案 ({DB_PATH})，請至『檔案管理』上傳。")

# 頁籤二：資料庫總表
with tab_database:
    st.header("所有人員名單總表")
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df, use_container_width=True)
    else:
        st.info("目前無資料。")

# 頁籤三：檔案管理
with tab_files:
    st.header("數據管理與備份")
    
    # 下載功能
    if st.session_state.df is not None:
        csv_data = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載目前資料庫 (CSV)", csv_data, "vip_export.csv", "text/csv")
    
    st.markdown("---")
    
    # 覆蓋功能：更新原本的資料庫檔案
    st.subheader("🔄 更新資料庫檔案")
    new_file = st.file_uploader("上傳新檔案以替換現有資料庫", type=["csv"])
    if new_file:
        new_df = pd.read_csv(new_file)
        new_df.to_csv(DB_PATH, index=False) # 存回伺服器/路徑
        st.session_state.df = new_df
        st.success("資料庫已成功更新並存檔！請切換到『桌次圖』查看。")