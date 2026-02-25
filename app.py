import streamlit as st
import pandas as pd
import os

# ... 前面設定維持不變 ...

# --- 🎨 緊湊版佈局 CSS ---
st.markdown("""
    <style>
    /* 1. 強制壓縮水平欄位間距 (解決間隔太寬的問題) */
    [data-testid="stHorizontalBlock"] {
        gap: 5px !important;
    }

    /* 2. 縮小按鈕元件的上下間距 */
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0px !important;
        padding-bottom: 2px !important;
    }

    /* 3. 按鈕本身的樣式調整：縮小內邊距讓桌子更緊湊 */
    .stButton > button {
        padding: 5px 2px !important;
        font-size: 14px !important;
        min-height: 40px !important;
    }

    /* 4. 浮動視窗絕對排版 (全 HTML，確保不跑版) */
    .popup-container {
        position: fixed; top: 35%; left: 50%; transform: translate(-50%, -50%);
        width: 350px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 10000;
        text-align: center; border: 4px solid #DAA520; 
        padding: 30px 15px; animation: fadeIn 0.3s forwards;
    }
    
    .close-x {
        position: absolute; top: 5px; right: 15px;
        font-size: 30px; color: #555; text-decoration: none;
        font-weight: bold;
    }

    .anchor-btn {
        display: inline-block; background-color: #000; color: #fff !important;
        padding: 12px 20px; border-radius: 10px; text-decoration: none;
        font-size: 16px; font-weight: bold; width: 85%; margin-top: 15px;
    }
    
    .table-anchor { scroll-margin-top: 250px; }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# ... 中間讀取資料邏輯維持不變 ...

def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局檔案")
        return
    
    # 讀取佈局
    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    highlight_set = set(highlighted_tables)
    
    st.markdown("### 🏟️ 千人宴場地實景佈局")
    
    for r_idx, row in df_map.iterrows():
        # --- 處理舞台/標籤 (維持滿版) ---
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else "#2E7D32"
            st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:10px; border-radius:10px; font-weight:bold; margin-bottom:5px;'>{row_content}</div>", unsafe_allow_html=True)
            continue

        # --- 處理桌位 (使用緊湊欄位) ---
        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text not in ["", "nan"]:
                    try:
                        table_num = int(float(val))
                        is_target = table_num in highlight_set
                        
                        # 顯示名稱
                        display_name = f"VIP{table_num}" if table_num in [1,2,3] else str(table_num)
                        
                        # 置中錨點
                        st.markdown(f"<div id='table_{table_num}' class='table-anchor'></div>", unsafe_allow_html=True)
                        
                        # 繪製按鈕
                        st.button(display_name, 
                                  key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_target else "secondary", 
                                  use_container_width=True)
                    except:
                        # 非數字文字 (如牆壁或走道標示)
                        st.markdown(f"<div style='text-align:center; font-size:10px; color:gray;'>{cell_text}</div>", unsafe_allow_html=True)

# ... 後面搜尋邏輯維持不變 ...