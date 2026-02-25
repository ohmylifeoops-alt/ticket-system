import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定與檔案讀取 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
LOCAL_DB = "thousand_banquet_db.csv"

st.set_page_config(page_title="千人盛宴實景導引系統", page_icon="🧧", layout="wide")

# 讀取資料邏輯：千人宴資料庫優先
def load_data():
    if os.path.exists(LOCAL_DB):
        try:
            return pd.read_csv(LOCAL_DB).astype(str)
        except:
            pass
    return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

# 💡 智慧顯示轉化 (針對千人規模，將桌號轉為票號區間)
def get_display_label(val):
    try:
        n = int(float(str(val).strip()))
        # 這裡會將 CSV 裡的 1 號桌自動顯示為 1~10，讓千人宴賓客快速對號
        if 1 <= n <= 300: 
            return f"{(n-1)*10+1}~{n*10}"
    except:
        pass
    return str(val)

# --- 2. 實景地圖 (千人盛宴視覺強化版) ---
def draw_seating_chart(highlighted_ids):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局檔案。請確認 GitHub 根目錄有「排桌.xlsx - 工作表1.csv」")
        return
    
    df_map = pd.read_csv(LAYOUT_FILE, header=None).astype(str)
    num_cols = len(df_map.columns)
    highlight_set = {str(x).strip().replace(".0", "") for x in highlighted_ids}

    st.markdown("### 🏟️ 千人盛宴：場地實景佈局")
    for r_idx, row in df_map.iterrows():
        # 標籤辨識
        row_content = "".join([val for val in row if val != "nan"])
        if any(k in row_content for k in ["舞台", "入口", "電視", "收銀", "禮賓"]):
            color = "#D32F2F" if "舞台" in row_content else ("#2E7D32" if "入口" in row_content else "#37474F")
            st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:15px; border-radius:12px; font-weight:bold; font-size:22px; margin: 15px 0; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);'>✨ {row_content} ✨</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                raw_id = val.strip().replace(".0", "") if val != "nan" else ""
                if raw_id:
                    display_text = get_display_label(raw_id)
                    is_active = raw_id in highlight_set
                    st.button(
                        display_text, 
                        key=f"btn_{r_idx}_{c_idx}_{raw_id}", 
                        type="primary" if is_active else "secondary", 
                        use_container_width=True
                    )

# --- 3. 介面內容 ---
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>🧧 千人盛宴實景管理系統</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>專業、效率、千人規模完美引導</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 賓客位置搜尋", "📊 批次數據更新"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號 (地圖對應區間將亮起)：", placeholder="請輸入搜尋關鍵字...")
    highlighted_list = []
    if search_q and not df_guest.empty:
        mask = df_guest.apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            highlighted_list = found['桌號'].tolist()
            labels = [get_display_label(x) for x in set(highlighted_list)]
            st.success(f"✅ 找到賓客！請引導至地圖標記區域：{', '.join(labels)}")
        else:
            st.warning("查無此賓客，請確認資料庫是否已更新。")
    
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📥 1. 下載千人宴名單範本")
    csv_temp = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下載目前的賓客總表 (CSV)",
        data=csv_temp,
        file_name="千人宴名單總表.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("📤 2. 批次更新全場資料")
    st.info("請上傳修正好「桌號」的 CSV 檔案。注意：地圖按鈕會根據 Excel 中的「桌號」對應 CSV 佈局編號亮起。")
    uploaded_file = st.file_uploader("選擇上傳已整理好的賓客 CSV", type="csv")
    
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        new_df.to_csv(LOCAL_DB, index=False)
        st.success("✅ 全場資料更新成功！千人盛宴準備就緒。")
        if st.button("🔄 立即重新整理"):
            st.rerun()

    st.divider()
    st.subheader("📋 現有資料預覽")
    st.dataframe(df_guest, use_container_width=True)