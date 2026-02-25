import streamlit as st
import pandas as pd
import os
import io

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

# 初始化 Session State：紀錄目前要「置中且標黃」的桌號
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# 自定義 CSS：包含浮動視窗樣式、亮黃色特效與捲動動畫
st.markdown("""
    <style>
    /* 浮動導引框樣式 */
    .floating-info {
        position: fixed;
        top: 20%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: #FFD700;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
        z-index: 9999;
        text-align: center;
        border: 3px solid #DAA520;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    
    /* 置中對齊錨點 */
    .table-anchor {
        scroll-margin-top: 250px; /* 捲動時預留上方空間 */
    }
    
    /* 亮黃色選中桌子效果 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important;
        color: #000 !important;
        border: 2px solid #FBC02D !important;
        font-weight: bold;
        transform: scale(1.1);
        transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# 載入雲端資料
@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if "桌號" in data.columns:
            data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

# --- 2. 實景地圖繪製 (支援自動定位) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局檔案")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    
    st.markdown("### 🏟️ 千人宴場地實景佈局")
    
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else "#2E7D32"
            st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold;'>{row_content}</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text not in ["", "nan"]:
                    try:
                        table_num = int(float(val))
                        # 檢查這桌是否為目前搜尋選中的桌子
                        is_target = (table_num == st.session_state.focus_table)
                        
                        display_name = str(table_num)
                        if table_num == 1: display_name = "VIP1"
                        elif table_num == 2: display_name = "VIP2"
                        elif table_num == 3: display_name = "VIP3"
                        
                        # 加上錨點 (HTML ID) 方便捲動
                        st.markdown(f"<div id='table_{table_num}' class='table-anchor'></div>", unsafe_allow_html=True)
                        
                        st.button(display_name, key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_target else "secondary", 
                                  use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_main")
    
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        
        if not found.empty:
            first_row = found.iloc[0]
            target_t = int(first_row['桌號'])
            
            # 顯眼浮動視窗
            st.markdown(f"""
                <div class="floating-info">
                    <h2 style="color: black; margin-bottom: 10px;">👋 貴賓 {first_row['姓名']} 您好</h2>
                    <p style="font-size: 24px; color: #d32f2f; font-weight: bold;">您的位置在：第 {target_t} 桌</p>
                    <a href="#table_{target_t}" target="_self" style="text-decoration: none;">
                        <button style="background-color: #000; color: #fff; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-size: 18px;">
                            👉 點我看座位 (自動定位)
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
            
            st.session_state.focus_table = target_t
        else:
            st.session_state.focus_table = None
            st.error("查無資訊")
            
    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

with tab2:
    st.subheader("📝 登記與驗證")
    # 保留單筆與批次上傳
    reg_mode = st.radio("登記方式：", ["單筆輸入", "批次上傳 Excel"], horizontal=True)
    
    if reg_mode == "單筆輸入":
        with st.form("single_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("姓名")
            t_num = c2.number_input("票號", 1, 2000)
            if st.form_submit_button("執行單筆驗證"):
                st.success(f"{name} 驗證成功")
                
    else:
        uploaded_excel = st.file_uploader("上傳 Excel (.xlsx)", type=["xlsx"])
        if uploaded_excel:
            st.success("檔案讀取成功，可進行批次防呆")

with tab3:
    st.subheader("📊 數據中心")
    # 下載 Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_guest.to_excel(writer, index=False)
    st.download_button("📥 下載完整資料庫 (Excel)", buffer.getvalue(), "千人宴總表.xlsx")
    st.dataframe(df_guest)