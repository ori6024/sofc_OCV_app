import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. ページのレイアウト設定
st.set_page_config(page_title="SOFC Analyzer", layout="wide")

st.title("SOFC OCV 解析シミュレーター")

# --- メイン画面上部に「条件変更」スライダーを配置 ---
st.markdown("### ⚙️ 条件変更")
st.write("スライダーを動かすと、下のグラフがリアルタイムに変化します。")

# 列を分けてスライダーを横に並べる（PCで見やすくなり、スマホでは縦に並びます）
col1, col2, col3 = st.columns(3)

with col1:
    T_c = st.slider("温度 (°C)", 400, 1100, 800)

with col2:
    P_fuel_user = st.slider("燃料極 全圧 (atm)", 0.5, 10.0, 1.0, 0.5)

with col3:
    P_air_user = st.slider("空気極 全圧 (atm)", 0.5, 10.0, 1.0, 0.5)

st.write("---") # 区切り線

# --- 定数計算 ---
T_k = T_c + 273.15
R, F = 8.314, 96485
E0 = 1.2844 - 0.0002521 * T_k 
O2_ratio = 0.21

def get_ocv(h2_ratio, p_f, p_a):
    x = max(min(h2_ratio / 100.0, 0.9999), 0.0001)
    p_h2 = x * p_f
    p_h2o = (1 - x) * p_f
    p_o2 = O2_ratio * p_a
    term = (R * T_k / (2 * F)) * np.log((p_h2 * (p_o2**0.5)) / p_h2o)
    return E0 + term

# --- データ作成 ---
h_list = np.arange(1, 100, 1)
y_user = [get_ocv(h, P_fuel_user, P_air_user) for h in h_list]
y_1 = [get_ocv(h, 1.0, 1.0) for h in h_list]
y_3 = [get_ocv(h, 3.0, 3.0) for h in h_list]
y_5 = [get_ocv(h, 5.0, 5.0) for h in h_list]

# --- グラフ描画 ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=h_list, y=y_1, name='1atm平衡', line=dict(color='lightgray', dash='dot')))
fig.add_trace(go.Scatter(x=h_list, y=y_3, name='3atm平衡', line=dict(color='gray', dash='dash')))
fig.add_trace(go.Scatter(x=h_list, y=y_5, name='5atm平衡', line=dict(color='black', dash='dash')))
fig.add_trace(go.Scatter(x=h_list, y=y_user, name='現在の設定', line=dict(color='red', width=4)))

fig.update_layout(
    height=600,
    plot_bgcolor='white',
    legend=dict(x=0.02, y=0.02, bgcolor='rgba(255,255,255,0.8)', bordercolor="black", borderwidth=1),
    xaxis=dict(
        title="水素容量比率 [%]",
        dtick=10, range=[0, 100],
        showgrid=True, gridcolor='DarkGray', showline=True, linewidth=2, linecolor='black', mirror=True,
        fixedrange=True
    ),
    yaxis=dict(
        title="開回路電圧 OCV [V]",
        dtick=0.05, # 0.05V刻み
        range=[0.6, 1.3],
        showgrid=True, gridcolor='DarkGray', showline=True, linewidth=2, linecolor='black', mirror=True,
        autorange=False,
        fixedrange=True
    ),
    margin=dict(l=60, r=20, t=20, b=60)
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- 下部に情報表示 ---
st.info(f"**標準電極電位 E0:** {E0:.4f} V （温度 {T_c}℃）")

df = pd.DataFrame({"H2_ratio_%": h_list, "OCV_V": y_user})
st.download_button("計算データをCSV保存", df.to_csv(index=False).encode('utf-8'), f"sofc_data_{T_c}C.csv")
