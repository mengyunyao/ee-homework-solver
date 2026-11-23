# 理工科高频课程验算清单与绘图规范

在输出最终解答前，按对应课程逐项用 Python / SymPy 做符号、数值与量纲核对。

---

## 1. 半导体物理学（刘恩科 第 8 版 / 第 7 版对照）

- **教材版本与常数双精度核对**（第 8 版与第 7 版部分实验基准值不同，若题目未指定需在 `#constants-box` 与结论中说明）：
  - 电子电量：$q = 1.602 \times 10^{-19}\text{ C}$（教辅近似取 $1.6 \times 10^{-19}\text{ C}$）
  - 玻耳兹曼常数：$k_0 = 1.380 \times 10^{-23}\text{ J/K} = 8.617 \times 10^{-5}\text{ eV/K}$
  - 室温热电压（$T = 300\text{ K}$）：$k_0 T / q \approx 0.02585\text{ V}$（常近似取 $0.0259\text{ V}$ 或 $0.026\text{ V}$）
  - $300\text{ K}$ 本征载流子浓度 $n_i$：
    - 第 8 版：$n_i(\text{Si}) = 1.02 \times 10^{10}\text{ cm}^{-3}$，$n_i(\text{Ge}) = 2.33 \times 10^{13}\text{ cm}^{-3}$
    - 第 7 版/旧教辅：$n_i(\text{Si}) = 1.5 \times 10^{10}\text{ cm}^{-3}$，$n_i(\text{Ge}) = 2.4 \times 10^{13}\text{ cm}^{-3}$
  - 硅单晶原子浓度：$N_{\text{Si}} = 5.00 \times 10^{22}\text{ cm}^{-3}$
- **高频验算陷阱**：
  - **CGS/cm 单位**：迁移率 $\text{cm}^2/(\text{V}\cdot\text{s})$、电阻率 $\Omega\cdot\text{cm}$、浓度 $\text{cm}^{-3}$ 三者天然闭合（$1/(\Omega\cdot\text{cm} \cdot \text{C} \cdot \text{cm}^2/(\text{V}\cdot\text{s})) = \text{cm}^{-3}$），切勿误乘 $10^{-4}$ 或 $10^{-6}$；但算到能量 $\text{J} \leftrightarrow \text{eV}$、介电常数 $\varepsilon_0 = 8.854 \times 10^{-14}\text{ F/cm}$ 时务必统一到 $\text{cm}$ 或 $\text{m}$。
  - **质量作用定律与电中性**：$n_0 p_0 = n_i^2$ 与 $n_0 + N_A^- = p_0 + N_D^+$ 联立时，高掺杂低温度先检验全电离假设与是否仍处于非简并近似（$|E_F - E_{c,v}| > 2 k_0 T$）。

---

## 2. 电子电力技术（整流 / 逆变 / 斩波）

- **角度与电抗参数**：
  - 区分触发延迟角 $\alpha$、有源逆变超前角 $\beta = \pi - \alpha$、换相重叠角 $\gamma$；有换相电感 $L_B$ 时必须扣除换相压降 $\Delta U_d$。
  - 反电动势负载先算临界导通角 / 熄弧角 $\theta$（区分连续导通 CCM 与断续导通 DCM，两种模态平均电压与有效值积分区间完全不同）。
- **平均值 vs 有效值（RMS）vs 谐波因数**：
  - 平均电流 $I_d$ 算电枢转矩/充电量，有效值电流 $I$ 算发热损耗与器件选型（晶闸管通态平均电流 $I_{T(\text{AV})} = I / 1.57$ 并留 1.5~2 倍安全裕量）。
  - 交流侧功率因数：位移因数 $\cos\varphi_1$、基波电流畸变因数 $\nu = I_1 / I$、总功率因数 $\lambda = \nu \cos\varphi_1$、$\text{THD}_i = \sqrt{I^2 - I_1^2} / I_1$。
  - 验算方法：用 `scipy.integrate.quad` 或傅里叶级数数值积分直接核对波形的平均值、RMS 与各次谐波幅值。

---

## 3. 通信原理（模拟调制 / 数字基带 / PCM）

- **采样与 PCM 速率**：
  - 奈奎斯特采样 $f_s \ge 2 f_H$；$M$ 进制/量化级数 $l = \log_2 M$；PCM 信息速率 $R_b = l \cdot f_s$，TDM-$n$ 路复接 $R_b = n \cdot l \cdot f_s$。
- **A 律 13 折线 8 位折叠二进码（极性码 $C_1$ + 段落码 $C_2 C_3 C_4$ + 段内码 $C_5 C_6 C_7 C_8$）**：
  - 归一化范围 $\pm 2048\Delta$：先判定极性 $C_1$（正 1 负 0），取绝对值查段落起始电平 $I_{Bi} \in \{0, 16, 32, 64, 128, 256, 512, 1024\}$ 与段内间隔 $\Delta_i \in \{1, 1, 2, 4, 8, 16, 32, 64\}$。
  - 验算核心：编码后译码电平 $I_{\text{dec}} = \pm(I_{Bi} + k \cdot \Delta_i + \Delta_i / 2)$（按教材/PPT 约定取段内量化中点或下边界，务必与课件一致），检验 $|I_{\text{dec}} - I_s| \le \Delta_i / 2$（或 $\Delta_i$）。
- **调制与分贝换算**：
  - AM 带宽 $2 f_m$（调制效率 $\eta \le 1/3$）、DSB 带宽 $2 f_m$、SSB 带宽 $f_m$、FM 卡森带宽 $B_{\text{FM}} = 2(\Delta f + f_m) = 2(m_f + 1)f_m$。
  - 功率比 $10\log_{10}(P_2/P_1)$，电压/场强比 $20\log_{10}(V_2/V_1)$；注意信噪比公式中的真值 vs $\text{dB}$ 值切换。

---

## 4. 微机原理与单片机（8086 / 8051 / STM32）

- **二进制 / 补码 / 标志位**：
  - 8 位有符号范围 $[-128, +127]$，16 位 $[-32768, +32767]$；用 Python 按位掩码 `& 0xFF` / `& 0xFFFF` 逐位核对 `CF`（无符号进借位）、`OF`（有符号溢出：同号相加异号或异号相减）、`ZF`、`SF`、`PF`（仅看低 8 位 1 的个数的奇偶性）。
- **寻址与定时器**：
  - 8086 物理地址 $= \text{Segment} \times 16 + \text{Offset}$（注意十六进制左移 1 位补 0）。
  - 51 单片机机器周期 $T_{\text{cy}} = 12 / f_{\text{osc}}$，模式 1（16 位）初值 $X = 65536 - t_{\text{target}} / T_{\text{cy}}$；STM32 定时器溢出频率 $f_{\text{out}} = f_{\text{clk}} / ((\text{PSC} + 1)(\text{ARR} + 1))$。

---

## 5. 电子线路（模电 / 高频 / 信号与系统）

- **先直流（Q 点）后交流（小信号）**：求 $r_{be} = r_{bb'} + (1+\beta) V_T / I_{EQ}$ 前必须先算准 $I_{CQ}, I_{EQ}, V_{CEQ}$ 并验证处于放大区。
- **频率响应**：时间常数法求主极点 $f_H, f_L$，验算单位增益带宽积 $f_T$ 与波特图斜率（$\pm 20\text{ dB/dec}$）。

---

## 6. Matplotlib 工程附图规范（当波形/曲线能显著提升理解时）

```python
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False  # 避免负号变方块
fig, ax = plt.subplots(figsize=(6.4, 3.2), dpi=300)
# 推荐使用矢量 SVG（Typst 原生支持）或 300 DPI PNG
fig.savefig("wave.svg", bbox_inches="tight")
```
- 图件存入当前作业目录（如 `figures/wave.svg`），并在 `.typ` 中用 `#image("figures/wave.svg", width: 88%)` 引用；`build_homework_pdf.py` 会自动收集并打包进编译根目录。
