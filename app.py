import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. ページレイアウト設定（centeredモード）
st.set_page_config(page_title="SOFC Analyzer", layout="centered")

# CSSによる超省スペース化設定
st.markdown("""
    <style>
    /* ページ全体の余白を最小化 */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; max-width: 700px; }
    
    /* スライダーの間隔を極限まで詰める */
    .stSlider { margin-top: -1.5rem; margin-bottom: -1.5rem; }
    
    /* タイトルとヘッダーのサイズと余白を最小化 */
    h2 { font-size: 1.2rem !important; margin-bottom: 0.5rem; margin-top: 0rem; color: #000; text-align: center; }
    
    /* スライダーのラベル文字を小さく */
    div[data-testid="stMarkdownContainer"] > p { font-size: 0.75rem !important; margin-bottom: 0rem; color: #000; font-weight: bold; }
    
    /* ウィジェット全体の上下間隔を調整 */
    [data-testid="stVerticalBlock"] { gap: 0.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# タイトル
st.write("## SOFC OCV 解析シミュレーター")

# スライダーを3列に配置（スマホでは自動的に縦に並びますが、隙間は最小です）
col1, col2, col3 = st.columns(3)
with col1:
    T_c = st.slider("温度 (°C)", 400, 1100, 800)
with col2:
    P_fuel_user = st.slider("燃料極 (atm)", 0.5, 10.0, 1.0, 0.5)
with col3:
    P_air_user = st.slider("空気極 (atm)", 0.5, 10.0, 1.0, 0.5)

# --- 定数計算 ---
T_k = T_c + 273.15
R, F = 8.314, 96485
E0 = 1.2844 - 0.0002521 * T_k 

def get_ocv(h2_ratio, p_f, p_a):
    x = max(min(h2_ratio / 100.0, 0.9999), 0.0001)
    p_h2, p_h2o, p_o2 = x * p_f, (1 - x) * p_f, 0.21 * p_a
    term = (R * T_k / (2 * F)) * np.log((p_h2 * (p_o2**0.5)) / p_h2o)
    return E0 + term

# --- データ作成 ---
h_list = np.arange(1, 100, 1)
y_user = [get_ocv(h, P_fuel_user, P_air_user) for h in h_list]
y_1 = [get_ocv(h, 1.0, 1.0) for h in h_list]
y_5 = [get_ocv(h, 5.0, 5.0) for h in h_list]

# --- グラフ描画 ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=h_list, y=y_1, name='1atm', line=dict(color='gray', width=1, dash='dot')))
fig.add_trace(go.Scatter(x=h_list, y=y_5, name='5atm', line=dict(color='black', width=1.5, dash='dash')))
fig.add_trace(go.Scatter(x=h_list, y=y_user, name='現在', line=dict(color='red', width=4)))

fig.update_layout(
    height=380, # 1画面に収めるために高さを少し圧縮
    plot_bgcolor='white',
    legend=dict(x=0.02, y=0.02, bgcolor='rgba(255,255,255,0.7)', bordercolor="black", borderwidth=1, font=dict(size=10)),
    
    xaxis=dict(
        title=dict(text="水素/水蒸気比率 [%]", font=dict(color='black', size=12)),
        range=[0, 100], dtick=10,
        tickfont=dict(color='black', size=10),
        ticks="outside", tickcolor="black",
        minor=dict(dtick=5, showgrid=True, gridcolor='silver'),
        fixedrange=True, gridcolor='black', gridwidth=0.5, showgrid=True,
        linecolor='black', linewidth=2, mirror=True
    ),
    yaxis=dict(
        title=dict(text="OCV [V]", font=dict(color='black', size=12)),
        range=[0.6, 1.3], dtick=0.1,
        tickfont=dict(color='black', size=10),
        ticks="outside", tickcolor="black",
        minor=dict(dtick=0.05, showgrid=True, gridcolor='silver'), 
        fixedrange=True, gridcolor='black', gridwidth=0.5, showgrid=True,
        linecolor='black', linewidth=2, mirror=True
    ),
    margin=dict(l=50, r=10, t=10, b=40)
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 最下部情報のコンパクト化
st.write(f"E0: {E0:.4f}V | 温度: {T_c}℃")
df = pd.DataFrame({"H2_H2O_ratio": h_list, "OCV_V": y_user})
st.download_button("CSV保存", df.to_csv(index=False).encode('utf-8'), f"sofc_{T_c}C.csv")
