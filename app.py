import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

# 初始化狀態，這是定位的關鍵
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 莊重感 CSS (不含任何會被擋掉的腳本) ---
st.markdown("""
    <style>
    /* 搜尋區域對齊 */
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }

    /* 金黃色小框：純展示用 */
    .popup-box {
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 999;
        text-align: center; border: 4px solid #DAA520; padding: 40px 20px 100px 20px;
    }

    /* 地圖排版縮小上下間距 */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { margin-bottom: -15px !important; }
    
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; 
        padding: 15px !important; border-radius: 10px; font-weight: bold; 
        font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    
    /* 亮黃色選中桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }

    /* 確保原生按鈕在最上層 */
    .stButton button { position: relative; z-index: 1001; }
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

# --- 介面 ---
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    c1, c2 = st.columns([4, 1])
    search_q = c1.text_input("輸入票號或姓名：", key="main_search")
    
    # 只要輸入框有變動，就執行搜尋
    if search_q:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        if not found.empty:
            row = found.iloc[0]
            st.session_state.focus_table = int(row['桌號'])
            
            # 1. 顯示黃色框（純 HTML 展示，不放任何點了沒反應的按鈕）
            st.markdown(f"""
                <div class="popup-box">
                    <h2 style="color: black;">👋 {row['姓名']} 貴賓</h2>
                    <p style="font-size: 20px; color: #555;">票號：{row['票號']}</p>
                    <p style="font-size: 32px; color: #d32f2f; font-weight: bold;">
                        位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # 2. 定位按鈕與叉叉：改用 Streamlit 原生按鈕（保證點了必應）
            # 透過 columns 讓按鈕並排在框框下緣位置
            btn_cols = st.columns([1, 2, 2, 1])
            with btn_cols[1]:
                if st.button("✖️ 關閉", key="close_pop"):
                    st.session_state.focus_table = None
                    st.rerun()
            with btn_cols[2]:
                # 這裡不再捲動，而是讓目標桌子變色，這在手機上最直觀
                st.button("📍 已在地圖標註", type="primary", key="loc_indicator")
        else:
            st.error("查無資料")

    # 繪製地圖
    if os.path.exists(LAYOUT_FILE):
        df_map = pd.read_csv(LAYOUT_FILE, header=None)
        num_cols = len(df_map.columns)
        for r_idx, row in df_map.iterrows():
            row_content = "".join([str(v) for v in row if not pd.isna(v)])
            if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                continue
            cols = st.columns(num_cols)
            for c_idx, val in enumerate(row):
                with cols[c_idx]:
                    cell_text = str(val).strip() if not pd.isna(val) else ""
                    if cell_text not in ["", "nan"]:
                        try:
                            table_num = int(float(val))
                            # 這是關鍵：如果搜尋到，桌子會直接變亮黃色，一眼就能看到
                            is_target = (table_num == st.session_state.focus_table)
                            st.button(f"VIP{table_num}" if table_num <= 3 else str(table_num), 
                                      key=f"m_{r_idx}_{c_idx}", 
                                      type="primary" if is_target else "secondary", 
                                      use_container_width=True)
                        except:
                            st.caption(cell_text)

with tab2:
    st.subheader("📝 登記與驗證")
    # 因為沒有 # 標籤，這裡絕對不會空白
    st.text_input("輸入測試欄位")
    st.button("測試按鈕")

with tab3:
    st.subheader("📊 數據中心")
    st.dataframe(df_guest, use_container_width=True)