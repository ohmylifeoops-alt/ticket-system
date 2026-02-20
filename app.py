import streamlit as st
import pandas as pd
import os

# --- 1. 系統效能設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="宴會桌次管理系統", page_icon="🎟️", layout="wide")

# 優化緩存：ttl=30 表示每 30 秒才去雲端抓一次，減輕伺服器負擔
@st.cache_data(ttl=30, show_spinner=False)
def load_cloud_data():
    try:
        data = pd.read_csv(SHEET_URL)
        # 確保關鍵欄位存在，避免程式報錯當掉
        required_cols = ["姓名", "票號", "桌號"]
        for col in required_cols:
            if col not in data.columns:
                return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 預載資料
df_guest = load_cloud_data()

# 快速算桌邏輯
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 (效能優化版) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案")
        return

    # 使用快取讀取佈局，避免反覆讀取硬碟
    @st.cache_data
    def get_layout():
        return pd.read_csv(LAYOUT_FILE, header=None)
    
    df_map = get_layout()
    
    # 建立一個 Set 加快搜尋速度
    highlight_set = set(highlighted_tables)

    for r_idx, row in df_map.iterrows():
        row_str = "".join([str(v) for v in row if not pd.isna(v)])
        
        if "舞台" in row_str:
            st.markdown("<div style='background-color:#FF4B4B; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚩 舞 臺 STAGE</div>", unsafe_allow_html=True)
            continue
        elif "入口" in row_str:
            st.markdown("<div style='background-color:#2E7D32; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚪 主 入 口 ENTRANCE</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break 
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text in ["", "nan"]:
                    st.write("")
                elif "電視" in cell_text:
                    st.markdown("<div style='background-color:#333; color:white; text-align:center; padding:5px; border-radius:5px;'>📺</div>", unsafe_allow_html=True)
                else:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        st.button(f"{table_num}", key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_active else "secondary", 
                                  use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 3. 主介面 ---
st.title("🎟️ 宴會桌次實景管理系統")

tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋地圖", "📝 登記與防呆", "📊 完整清單"])

with tab1:
    search_q = st.text_input("🔍 輸入姓名、電話或票號 (自動亮起桌號)：", key="search_main")
    highlighted_list = []
    if search_q:
        # 優化搜尋：避免全表掃描，只轉字串一次
        search_target = df_guest.astype(str)
        mask = search_target.apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            highlighted_list = found['桌號'].dropna().unique().tolist()
            st.success(f"✅ 找到賓客！位於：{list(set(highlighted_list))} 桌")
    
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📝 賓客入座登記 (防呆驗證)")
    with st.form("guest_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("姓名")
            t_id = st.number_input("票號 (1-1700)", 1, 1700, 1)
        with c2:
            phone = st.text_input("電話")
            seller = st.text_input("售出者")
        
        btn = st.form_submit_button("執行防呆檢查")
        
        if btn:
            # 1. 空值檢查
            if not name.strip():
                st.error("⚠️ 姓名不能為空！")
            # 2. 重複票號檢查
            elif not df_guest.empty and t_id in df_guest['票號'].values:
                # 找出那位賓客的名字
                exist_name = df_guest[df_guest['票號'] == t_id]['姓名'].values[0]
                st.error(f"❌ 票號 {t_id} 已被使用！ (登記人：{exist_name})")
            else:
                table = calculate_table(t_id)
                st.balloons()
                st.success(f"🎉 驗證通過！請將此資料填入 Google 表格：")
                st.code(f"姓名: {name} | 桌號: {table} | 票號: {t_id}", language="text")
                st.info("請於 Google Sheets 完成填寫，網頁端將自動同步。")

with tab3:
    st.subheader("📊 雲端數據同步預覽")
    st.dataframe(df_guest, use_container_width=True)
    if st.button("🔄 立即重新讀取雲端 (若資料未顯示請點此)"):
        st.cache_data.clear()
        st.rerun()