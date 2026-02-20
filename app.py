import streamlit as st
import pandas as pd
import os

# --- 1. 設定與初始化 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="票號桌次管理與地圖系統", page_icon="🎟️", layout="wide")

# 讀取資料庫
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 核心邏輯：計算桌次 (保留你原本的票號除以10邏輯)
def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 介面標題 ---
st.title("🎟️ 票務登記與桌次視覺化系統")

# 使用分頁區分功能
tab1, tab2, tab3 = st.tabs(["🔍 桌次地圖搜尋", "📝 新增賓客登記", "📊 所有數據管理"])

# --- 功能一：桌次地圖搜尋 (整合手繪圖邏輯) ---
with tab1:
    st.subheader("快速定位搜尋")
    search_term = st.text_input("🔍 輸入姓名、電話、票號或售出者：", placeholder="搜尋後地圖上的桌號會變色...")
    
    # 搜尋邏輯
    highlighted = []
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        highlighted = df[mask]['桌號'].tolist()
        if highlighted:
            st.success(f"找到賓客！請引導至第 {list(set(highlighted))} 桌")
        else:
            st.warning("查無資料，請確認輸入資訊。")

    st.markdown("---")
    
    # 定義桌子按鈕函數
    def draw_table(num):
        is_active = num in highlighted
        label = f"{num}"
        # 搜尋到的桌子會變成 Primary (藍色)，其餘是白色
        st.button(label, key=f"map_t{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # A. 舞台區 (1-100號)
    st.markdown("<h2 style='text-align: center; color: red; background-color: #fff0f0; padding: 10px; border-radius: 10px;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)