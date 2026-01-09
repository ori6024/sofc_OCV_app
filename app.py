import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. ページレイアウト設定
st.set_page_config(page_title="SOFC Analyzer", layout="wide")

# 余白とサイズを極限までカットするCSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stSlider { margin-bottom: -1.0rem; }
    h3 { font-size: 1.2rem !important; margin-bottom: 0rem; margin-top: 0rem; }
    div[data-testid="stMarkdownContainer"] > p { font-size: 0.8rem; margin-bottom: 0.1rem; }
    </style>
    """, unsafe_allow_html=True)

st.write("### ⚙️ 条件変更")

# スライダーを3列に配置
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
fig.add_trace(go.Scatter(x=h_list, y=y_1, name='1atm', line=dict(color='lightgray', dash='dot')))
fig.add_trace(go.Scatter(x=h_list, y=y_5, name='5atm', line=dict(color='black', dash='dash')))
fig.add_trace(go.Scatter(x=h_list, y=y_user, name='現在', line=dict(color='red', width=4)))

fig.update_layout(
    height=400,
    plot_bgcolor='white',
    legend=dict(x=0.02, y=0.02, bgcolor='rgba(255,255,255,0.7)'),
    # 【修正点】ラベル名の変更と、目盛りを10%刻み(dtick=10)に設定
    xaxis=dict(
        title="水素/水蒸気比率 [%]", 
        range=[0, 100], 
        dtick=10, 
        fixedrange=True, 
        gridcolor='lightgray',
        linecolor='black',
        mirror=True
    ),
    yaxis=dict(
        title="OCV [V]", 
        range=[0.6, 1.3], 
        dtick=0.05, 
        fixedrange=True, 
        gridcolor='lightgray',
        linecolor='black',
        mirror=True
    ),
    margin=dict(l=50, r=10, t=10, b=40)
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 最下部
st.write(f"**E0:** {E0:.4f}V | **温度:** {T_c}℃")
df = pd.DataFrame({"水素/水蒸気比率[%]": h_
