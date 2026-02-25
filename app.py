import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

# 初始化 Session 狀態，確保切換分頁時資料不遺失
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 莊重感 CSS ---
st.markdown("""
    <style>
    .label-box-original {
        color: white; text-align: center; padding: 15px; border-radius: 10px; 
        font-weight: bold; font-size: 20px; margin: 10px 0; width: 100%;
    }
    .result-card {
        background-color: #FFD700; padding: 20px; border-radius: 15px;
        border: 3px solid #DAA520; margin-bottom: 20px; text-align: center;
    }
    [data-testid="column"] { margin-bottom: -10px !important; }
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

# --- Tab 1: 快速搜尋 ---
with tab1:
    search_q = st.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 王大明", key="search_input_main")
    
    if search_q:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | \
               (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        
        if not found.empty:
            row = found.iloc[0]
            st.session_state.focus_table = int(row['桌號'])
            
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: black; margin: 0;">👋 {row['姓名']} 貴賓</h2>
                    <p style="font-size: 18px; color: #444; margin: 5px 0;">票號：{row['票號']}</p>
                    <p style="font-size: 26px; color: #d32f2f; font-weight: bold; margin: 10px 0;">
                        位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                    </p>
                    <p style="font-size: 14px; color: #666;">(請直接往下看地圖黃色標註處)</p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("✖️ 清除搜尋結果"):
                st.session_state.focus_table = None
                st.rerun()
        else:
            st.session_state.focus_table = None
            st.error("查無資料。")

    # 繪製地圖 (確保穩定不崩潰)
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
                            st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), key=f"m_{r_idx}_{c_idx}", type="primary" if is_target else "secondary", use_container_width=True)
                        except:
                            st.caption(cell_text)

# --- Tab 2: 批次登記與防呆 (還原功能) ---
with tab2:
    st.subheader("📝 登記與防呆驗證")
    reg_mode = st.radio("選擇登記模式：", ["連號批次登記", "Excel 批次上傳"], horizontal=True)
    
    if reg_mode == "連號批次登記":
        with st.form("batch_reg_form"):
            c1, c2 = st.columns(2)
            name_rep = c1.text_input("代表姓名")
            seller_rep = c2.text_input("售票負責人")
            start_t = c1.number_input("起始票號", 1, 2000)
            count_t = c2.number_input("張數", 1, 100)
            target_t = st.number_input("統一桌號", 1, 200)
            
            if st.form_submit_button("生成登記預覽"):
                t_range = range(int(start_t), int(start_t) + int(count_t))
                st.info(f"📍 預覽：即將為 {name_rep} 登記從 {start_t} 到 {start_t + count_t - 1} 號票")
                # 生成表格供檢查
                preview_list = [{"姓名": name_rep, "票號": t, "負責人": seller_rep, "桌號": target_t} for t in t_range]
                st.table(preview_list)
                st.code("\n".join([f"{name_rep}\t電話\t{t}\t{seller_rep}\t{target_t}" for t in t_range]), language="text")

    elif reg_mode == "Excel 批次上傳":
        uploaded_file = st.file_uploader("請選擇 Excel 檔案 (.xlsx)", type=["xlsx"])
        if uploaded_file:
            st.success("檔案上傳成功，正在解析欄位...")

# --- Tab 3: 數據中心 ---
with tab3:
    st.subheader("📊 數據中心")
    st.info(f"目前資料庫總計：{len(df_guest)} 筆資料")
    st.dataframe(df_guest, use_container_width=True)
    
    # 下載功能
    csv_data = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載目前資料庫 CSV", csv_data, "千人宴最新總表.csv", "text/csv")