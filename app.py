import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. ページの設定
st.set_page_config(page_title="SOFC OCV Calculator", layout="wide")

# 2. サイドバーの設定
st.sidebar.markdown("### ⚙️ 条件変更")
st.sidebar.write("こちらでパラメータを調整できます")

# 入力スライダー
temp_c = st.sidebar.slider('温度 (°C)', 400.0, 1000.0, 700.0)
p_h2 = st.sidebar.slider('水素分圧 H2 (atm)', 0.01, 1.0, 0.97)
p_h2o = st.sidebar.slider('水蒸気分圧 H2O (atm)', 0.01, 0.5, 0.03)
p_o2 = st.sidebar.slider('酸素分圧 O2 (atm)', 0.01, 1.0, 0.21)

# 3. ネルンストの式による計算
R = 8.314  # 気体定数 [J/mol·K]
F = 96485  # ファラデー定数 [C/mol]
T = temp_c + 273.15

# 標準ギブズエネルギー変化（概算式）
# ΔG = -247500 + 55.8 * T (J/mol)
delta_g = -247500 + 55.8 * T
E0 = -delta_g / (2 * F)

# ネルンストの式: E = E0 + (RT/2F) * ln( (P_H2 * P_O2^0.5) / P_H2O )
ocv = E0 + (R * T / (2 * F)) * np.log((p_h2 * np.sqrt(p_o2)) / p_h2o)

# グラフ用データ（温度変化に伴う推移）
t_range = np.linspace(400, 1000, 100)
t_kelvin = t_range + 273.15
ocv_range = (-(-247500 + 55.8 * t_kelvin) / (2 * F)) + \
            (R * t_kelvin / (2 * F)) * np.log((p_h2 * np.sqrt(p_o2)) / p_h2o)

# 4. グラフ作成
fig = go.Figure()

# メインの曲線
fig.add_trace(go.Scatter(
    x=t_range, y=ocv_range, 
    mode='lines', name='OCV推移', 
    line=dict(color='firebrick', width=3)
))

# 現在の動作点（青いドット）
fig.add_trace(go.Scatter(
    x=[temp_c], y=[ocv], 
    mode='markers', name='現在の動作点', 
    marker=dict(size=12, color='blue', symbol='circle')
))

# 5. レイアウト設定（ズーム禁止を確実に適用）
fig.update_layout(
    xaxis_title="Temperature (°C)",
    yaxis_title="OCV (V)",
    xaxis=dict(range=[400, 1000], fixedrange=True), # 横軸固定
    yaxis=dict(range=[0.8, 1.2], fixedrange=True), # 縦軸固定
    height=500,
    margin=dict(l=20, r=20, t=20, b=20),
    showlegend=False
)

# 6. 画面への表示
st.title('SOFC OCV シミュレーター')
st.subheader(f'計算された開回路電圧 (OCV): {ocv:.4f} V')

# ズーム禁止の設定 (config) はこの st.plotly_chart の中で指定します
st.plotly_chart(
    fig, 
    use_container_width=True, 
    config={'displayModeBar': False, 'staticPlot': False, 'scrollZoom': False}
)

st.write(f"**現在の設定:** 温度 {temp_c}°C, H₂ {p_h2}atm, H₂O {p_h2o}atm, O₂ {p_o2}atm")
st.info("スライダーを動かすと現在の動作点が移動します。グラフはタップしても動かないよう固定されています。")
