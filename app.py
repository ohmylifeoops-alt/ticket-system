import streamlit as st
import pandas as pd

# 頁面配置
st.set_page_config(page_title="VIP 席位配置系統", layout="wide")

# 自定義桌位 CSS：模擬實體會場感
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
        padding-bottom: 5px;
    }
    .seat-item {
        font-size: 0.95rem;
        text-align: left;
        color: #212F3C;
        margin: 3px 0;
    }
    .non-sequential { color: #CB4335; font-weight: bold; } /* 非連號特別標註 */
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# 1. 建立三個頁籤：桌次圖 (預設)、資料庫總表、上傳與下載
# ----------------------------------------------------------------
tab_map, tab_database, tab_files = st.tabs(["📍 現場桌次圖", "📋 資料庫總表", "⚙️ 檔案管理"])

# 初始化 Session State (防止重新整理時資料消失)
if 'df' not in st.session_state:
    st.session_state.df = None

# ----------------------------------------------------------------
# 頁籤三：檔案管理 (優先處理資料來源)
# ----------------------------------------------------------------
with tab_files:
    st.header("數據管理中心")
    col_up, col_down = st.columns(2)
    
    with col_up:
        st.subheader("📤 上傳最新座位表")
        uploaded_file = st.file_uploader("選擇 CSV 檔案", type=["csv"])
        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success("資料庫已成功更新！")

    with col_down:
        st.subheader("📥 下載目前資料庫")
        if st.session_state.df is not None:
            csv_data = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="點擊下載目前的 CSV 檔案",
                data=csv_data,
                file_name='vip_seat_export.csv',
                mime='text/csv',
            )
        else:
            st.info("目前無資料可下載")

# ----------------------------------------------------------------
# 頁籤二：資料庫總表
# ----------------------------------------------------------------
with tab_database:
    st.header("所有人員名單總表")
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df, use_container_width=True)
    else:
        st.warning("請先到『檔案管理』分頁上傳資料。")

# ----------------------------------------------------------------
# 頁籤一：現場桌次圖 (首頁顯示)
# ----------------------------------------------------------------
with tab_map:
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # 選擇 VIP 等級
        target_vip = st.radio("顯示區域：", ["VIP1", "VIP2", "VIP3"], horizontal=True)
        
        # 過濾該等級資料
        filtered_df = df[df['VIP_Level'] == target_vip]
        
        # 關鍵邏輯：依據『桌號』分組，無視編號是否連號
        tables = filtered_df.groupby('Table_No')
        
        st.subheader(f"🏟️ {target_vip} 區座次分佈")
        
        # 設定每列顯示幾桌 (例如一排 4 桌)
        num_cols = 4
        cols = st.columns(num_cols)
        
        # 遍歷每一桌進行繪製
        for i, (table_no, group) in enumerate(tables):
            with cols[i % num_cols]:
                # 建立桌子 HTML 內容
                seat_html = ""
                for _, row in group.iterrows():
                    seat_html += f'<div class="seat-item">💺 {row["Seat_ID"]} - {row["Name"]}</div>'
                
                # 渲染桌子卡片
                st.markdown(f"""
                    <div class="table-card">
                        <div class="table-header">第 {table_no} 桌</div>
                        {seat_html}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("👋 歡迎使用座位系統。請先前往『檔案管理』上傳 CSV 資料庫以繪製地圖。")