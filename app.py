import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

# 初始化狀態
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 莊重感 CSS (只做顏色，不做定位，確保穩定) ---
st.markdown("""
    <style>
    /* 標籤盒樣式 (舞台、入口等) */
    .label-box-original {
        color: white; text-align: center; 
        padding: 15px; border-radius: 10px; font-weight: bold; 
        font-size: 20px; margin: 10px 0; width: 100%;
    }
    /* 搜尋結果顯示區 */
    .result-card {
        background-color: #FFD700; padding: 20px; border-radius: 15px;
        border: 3px solid #DAA520; margin-bottom: 20px; text-align: center;
    }
    /* 桌子按鈕間距微調 */
    [data-testid="column"] { margin-bottom: -10px !important; }
    
    /* 亮黃色選中桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if '票號' in data.columns: data['票號_str'] = data['票號'].astype(str)
        if '桌號' in data.columns: data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

# --- 2. 介面內容 ---
st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    search_q = st.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 王大明")
    
    if search_q:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | \
               (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        
        if not found.empty:
            row = found.iloc[0]
            st.session_state.focus_table = int(row['桌號'])
            
            # 顯示搜尋結果卡片（在頁面上，非浮動，最穩定）
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: black; margin: 0;">👋 {row['姓名']} 貴賓</h2>
                    <p style="font-size: 18px; color: #444; margin: 5px 0;">票號：{row['票號']}</p>
                    <p style="font-size: 26px; color: #d32f2f; font-weight: bold; margin: 10px 0;">
                        您的位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("✖️ 清除搜尋結果"):
                st.session_state.focus_table = None
                st.rerun()
        else:
            st.session_state.focus_table = None
            st.error("查無資料，請重新輸入。")

    # --- 繪製地圖 ---
    if os.path.exists(LAYOUT_FILE):
        df_map = pd.read_csv(LAYOUT_FILE, header=None)
        num_cols = len(df_map.columns)
        st.markdown("### 🏟️ 場地實景佈局圖")
        
        for r_idx, row in df_map.iterrows():
            row_content = "".join([str(v) for v in row if not pd.isna(v)])
            if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                st.markdown(f'<div class="label-box-original" style="background-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                continue
                
            cols = st.columns(num_cols)
            for c_idx, val in enumerate(row):
                with cols[c_idx]:
                    cell_text = str(val).strip() if not pd.isna(val) else ""
                    if cell_text not in ["", "nan"]:
                        try:
                            t_num = int(float(val))
                            is_target = (t_num == st.session_state.focus_table)
                            st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), 
                                      key=f"m_{r_idx}_{c_idx}", 
                                      type="primary" if is_target else "secondary", 
                                      use_container_width=True)
                        except:
                            st.caption(cell_text)

with tab2:
    st.subheader("📝 登記與驗證")
    # 這裡現在絕對不會變空白，因為沒有任何網址標籤
    st.text_input("輸入姓名")
    st.number_input("輸入票號", 1)

with tab3:
    st.subheader("📊 數據中心")
    st.dataframe(df_guest, use_container_width=True)