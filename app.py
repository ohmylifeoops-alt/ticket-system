import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 設定頁面 ---
st.set_page_config(page_title="雲端票務系統", page_icon="☁️", layout="wide")
st.title("☁️ 雲端活動票務管理系統")

# --- 連線 Google Sheets ---
# 使用 ttl=0 確保每次都讀到最新資料
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(worksheet="Sheet1", ttl=0) # 預設工作表名稱通常是 Sheet1
    # 如果是空表，確保欄位存在
    if df.empty:
        df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])
except Exception:
    # 處理第一次讀取可能為空的情況
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# --- 核心邏輯：計算桌號 ---
def calculate_table(ticket_id):
    try:
        tid = int(ticket_id)
        if tid <= 0: return None
        return (tid - 1) // 10 + 1
    except ValueError:
        return None

# --- 側邊欄：輸入資料 ---
with st.sidebar:
    st.header("📝 新增賓客")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("姓名")
        phone = st.text_input("聯絡電話")
        # 限制輸入 1-2000
        ticket_val = st.number_input("票號 (1-2000)", min_value=1, max_value=2000, step=1)
        seller = st.text_input("售出者")
        
        submitted = st.form_submit_button("確認登記")
        
        if submitted:
            if not name:
                st.error("姓名為必填！")
            elif not df.empty and ticket_val in df["票號"].values:
                st.error(f"錯誤：票號 {ticket_val} 已經被註冊過了！")
            else:
                table_num = calculate_table(ticket_val)
                # 建立新資料
                new_data = pd.DataFrame([{
                    "姓名": name,
                    "聯絡電話": phone,
                    "票號": ticket_val,
                    "售出者": seller,
                    "桌號": table_num
                }])
                
                # 合併舊資料並寫回 Google Sheets
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                
                st.success(f"✅ 登記成功！{name} 在第 {table_num} 桌")
                # 強制刷新快取以顯示最新資料
                st.cache_data.clear()

# --- 主畫面：搜尋與顯示 ---
st.subheader("🔍 名單查詢")
search_term = st.text_input("輸入關鍵字 (姓名、票號、桌號...)")

if not df.empty:
    # 顯示用的 DataFrame
    display_df = df.copy()
    
    # 搜尋邏輯
    if search_term:
        mask = display_df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False).any(), axis=1
        )
        display_df = display_df[mask]
    
    # 排序：依票號
    display_df = display_df.sort_values(by="票號")
    
    # 美化表格顯示
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "票號": st.column_config.NumberColumn(format="%d"),
            "桌號": st.column_config.NumberColumn(format="%d 桌"),
        }
    )
    st.caption(f"共 {len(display_df)} 筆資料")
else:
    st.info("目前資料庫是空的，請從側邊欄新增資料。")