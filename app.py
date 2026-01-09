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

# --- 定義確認對話框 (放在程式碼前段) ---
@st.dialog("⚠️ 重複資料警告")
def confirm_overwrite(ticket_val, name, phone, seller, df, conn):
    # 這裡顯示舊資料讓使用者比對（選用）
    old_name = df[df["票號"] == ticket_val]["姓名"].values
    st.write(f"票號 **{ticket_val}** 已經被 **{old_name}** 註冊過了！")
    st.write("您確定要用目前的資料覆蓋並取代舊資料嗎？")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ 取消"):
            st.rerun() # 重新整理，關閉視窗
            
    with col2:
        if st.button("✅ 確認覆蓋", type="primary"):
            # --- 執行覆蓋邏輯 ---
            # 1. 算出桌號
            table_num = (ticket_val - 1) // 10 + 1
            
            # 2. 在資料中找到該票號的位置並更新 (Update)
            # 使用 update 寫法：先刪除舊的，再加新的，確保乾淨
            df_new = df[df["票號"]!= ticket_val].copy()
            
            new_entry = pd.DataFrame([{
                "姓名": name,
                "聯絡電話": phone,
                "票號": ticket_val,
                "售出者": seller,
                "桌號": table_num
            }])
            
            df_final = pd.concat([df_new, new_entry], ignore_index=True)
            
            # 3. 寫回 Google Sheets
            conn.update(worksheet="Sheet1", data=df_final)
            
            # 4. 清除快取並顯示成功訊息
            st.cache_data.clear()
            st.session_state["success_msg"] = f"已成功覆蓋票號 {ticket_val}！"
            st.rerun()

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
            else:
                # 檢查票號是否已存在
                if not df.empty and ticket_val in df["票號"].values:
                    # [關鍵] 如果重複，不直接寫入，而是呼叫對話框
                    confirm_overwrite(ticket_val, name, phone, seller, df, conn)
                else:
                    # 如果沒重複，直接新增 (這部分保持原本的新增邏輯)
                    table_num = calculate_table(ticket_val)
                    new_entry = pd.DataFrame([{
                        "姓名": name,
                        "聯絡電話": phone,
                        "票號": ticket_val,
                        "售出者": seller,
                        "桌號": table_num
                    }])
                    updated_df = pd.concat([df, new_entry], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.cache_data.clear()
                    st.success(f"✅ 登記成功！{name} 在第 {table_num} 桌")

    # --- 顯示覆蓋成功的訊息 (放在側邊欄底部) ---
    if "success_msg" in st.session_state:
        st.success(st.session_state["success_msg"])
        # 顯示一次後刪除，避免訊息一直留著
        del st.session_state["success_msg"]

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
    
# 將資料轉為 CSV 字串
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 下載完整總表 (CSV)",
    data=csv,
    file_name='guest_list_total.csv',
    mime='text/csv',)