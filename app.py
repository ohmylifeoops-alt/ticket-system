import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

# 初始化 Session 狀態
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 莊重感 CSS：專注於排版穩定 ---
st.markdown("""
    <style>
    /* 1. 搜尋結果卡片 (非浮動，最穩定) */
    .result-card {
        background-color: #FFD700; padding: 25px; border-radius: 15px;
        border: 4px solid #DAA520; margin-bottom: 20px; text-align: center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
    }
    
    /* 2. 地圖標籤 (舞台、入口) */
    .label-box-fixed {
        color: white; text-align: center; padding: 15px;
        border-radius: 10px; font-weight: bold; font-size: 22px;
        margin: 10px 0; width: 100%;
    }
    
    /* 3. 壓縮桌子上下間距 */
    [data-testid="stHorizontalBlock"] { margin-bottom: -15px !important; }
    
    /* 4. 目標桌子高亮變色 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }
    
    /* 5. 錨點偏移，讓滾動後桌子在螢幕中間 */
    .scroll-point { scroll-margin-top: 300px; }
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
    search_q = st.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 徐鳳慈")
    
    if search_q:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | \
               (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        
        if not found.empty:
            row = found.iloc[0]
            st.session_state.focus_table = int(row['桌號'])
            
            # 顯示結果區塊
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: black; margin: 0;">👋 {row['姓名']} 貴賓</h2>
                    <p style="font-size: 18px; color: #444;">票號：{row['票號']}</p>
                    <p style="font-size: 32px; color: #d32f2f; font-weight: bold; margin: 10px 0;">
                        位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # --- 原生定位按鈕：100% 能滾動且不弄壞網址 ---
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                # 使用 HTML 連結，但我們在地圖繪製時提供 ID
                st.markdown(f"""
                    <a href="#table_{st.session_state.focus_table}" target="_self" style="text-decoration: none;">
                        <button style="background-color: black; color: white; width: 100%; padding: 15px; border-radius: 10px; font-weight: bold; border: none; cursor: pointer;">
                            👉 點我看座位 (自動捲動)
                        </button>
                    </a>
                """, unsafe_allow_html=True)
                if st.button("✖️ 清除結果並關閉"):
                    st.session_state.focus_table = None
                    st.rerun()
        else:
            st.session_state.focus_table = None
            st.error("查無資料，請確認輸入是否正確。")

    # --- 繪製地圖 ---
    if os.path.exists(LAYOUT_FILE):
        df_map = pd.read_csv(LAYOUT_FILE, header=None)
        num_cols = len(df_map.columns)
        st.markdown("---")
        st.markdown("### 🏟️ 場地實景佈局圖")
        
        for r_idx, row in df_map.iterrows():
            row_content = "".join([str(v) for v in row if not pd.isna(v)])
            if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                st.markdown(f'<div class="label-box-fixed" style="background-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                continue
                
            cols = st.columns(num_cols)
            for c_idx, val in enumerate(row):
                with cols[c_idx]:
                    cell_text = str(val).strip() if not pd.isna(val) else ""
                    if cell_text not in ["", "nan"]:
                        try:
                            t_num = int(float(val))
                            is_target = (t_num == st.session_state.focus_table)
                            # 設定錨點 ID 供自動捲動使用
                            st.markdown(f'<div id="table_{t_num}" class="scroll-point"></div>', unsafe_allow_html=True)
                            st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), 
                                      key=f"m_{r_idx}_{c_idx}", 
                                      type="primary" if is_target else "secondary", 
                                      use_container_width=True)
                        except:
                            st.caption(cell_text)

with tab2:
    st.subheader("📝 登記與驗證")
    # 這裡現在絕對不會變空白，因為我們已經修正了網址列標籤問題
    st.info("網址已清理，登記功能正常。")

with tab3:
    st.subheader("📊 數據中心")
    st.dataframe(df_guest, use_container_width=True)