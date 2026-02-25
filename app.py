import streamlit as st
import pandas as pd

st.set_page_config(page_title="VIP 席位配置系統", layout="wide")

# 自定義 CSS 讓桌子看起來像「桌子」
st.markdown("""
    <style>
    .table-box {
        border: 2px solid #31333F;
        border-radius: 10px;
        padding: 10px;
        background-color: #f0f2f6;
        text-align: center;
        margin-bottom: 10px;
        min-height: 120px;
    }
    .vip-label { font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 會場桌次平面配置圖")

# 1. 檔案管理區
with st.sidebar:
    st.header("⚙️ 檔案中心")
    uploaded_file = st.file_uploader("重新上傳座位表 (CSV)", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # 提供下載原始檔
        st.download_button("📥 下載目前資料庫", df.to_csv(index=False).encode('utf-8-sig'), "current_seats.csv")

# 2. 顯示邏輯
if uploaded_file is not None:
    # 這裡假設你的 CSV 有：Table_No, Seat_ID, VIP_Level, Name
    # 如果有座標欄位 (X, Y) 更好，若沒有，我們依 Table_No 排序呈現
    
    selected_vip = st.selectbox("選擇要查看的等級", ["VIP1", "VIP2", "VIP3"])
    
    # 篩選資料
    display_df = df[df['VIP_Level'] == selected_vip]
    
    # 依據「桌號」分組 (這解決了非連號問題)
    grouped = display_df.groupby('Table_No')
    
    # --- 開始繪製桌次圖 ---
    st.subheader(f"📍 {selected_vip} 區域佈局")
    
    # 建立多欄位來模擬會場感 (例如一排 4 桌)
    col_count = 4
    cols = st.columns(col_count)
    
    for i, (table_no, group) in enumerate(grouped):
        with cols[i % col_count]:
            # 使用 HTML 標籤讓介面更像「圖」
            seat_details = "<br>".join([f"💺 {row['Seat_ID']} ({row['Name']})" for _, row in group.iterrows()])
            
            st.markdown(f"""
                <div class="table-box">
                    <div style="font-size: 1.2em; font-weight: bold; border-bottom: 1px solid #ccc; margin-bottom: 5px;">
                        第 {table_no} 桌
                    </div>
                    <div style="font-size: 0.85em; text-align: left;">
                        {seat_details}
                    </div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.info("👋 請上傳 CSV 檔案，我會立刻幫你繪製桌次平面圖！")
    # 範例提示
    st.write("預期格式：")
    st.table(pd.DataFrame({
        'Table_No': [49, 49, 50],
        'Seat_ID': [101, 999, 103],
        'Name': ['張三', '李四(非連號)', '王五'],
        'VIP_Level': ['VIP1', 'VIP1', 'VIP1']
    }))