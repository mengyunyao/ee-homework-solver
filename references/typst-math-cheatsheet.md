# Typst 0.15 数学公式与排版速查表

## 1. 常见 LaTeX → Typst 陷阱对照

| 需求 | 错误写法（LaTeX 习惯） | 正确写法（Typst 0.15） |
| :--- | :--- | :--- |
| 行内 vs 独立公式 | `\( x \)` / `\[ x \]` | 行内不留空格：`$x$`；独立居中前后必须留空格：`$ x $` |
| 分式 | `\frac{a}{b}` | `a / b` 或 `(a + b) / (c + d)`；强制分式 `frac(a, b)` |
| 负指数 / 复合上标 | `10^{-19}`, `x^{2n}` | `10^(-19)`, `x^(2n)`（括号防止解析成多字符文本） |
| 上下标同时出现 | `n_i^2`, `C_5^2` | `n_i^2`, `C_5^2`（注意标识符多字母时用引号：`n_"eff"`, `"cm"^(-3)`） |
| 物理单位（正体） | `\Omega \cdot \text{cm}` | `Omega dot.c "cm"`, `"cm"^2 / ("V" dot.c "s")`, `"kbit/s"` |
| 相量 / 角度 | `220\angle 30^\circ` | `220 angle 30 degree` 或 `220 angle 30^circle` |
| 乘法与点乘 | `\times`, `\cdot` | `times`, `dot.c`（注意：`dot` 是字母上加点，`dot.c` 才是居中点乘 `·`） |
| 希腊字母 | `\mu`, `\alpha`, `\Omega` | `mu`, `alpha`, `Omega`（直接写名字，不加反斜杠） |
| 分段函数 | `\begin{cases}...\end{cases}` | `cases(x + 1 & x >= 0, 0 & x < 0)` |
| 矩阵 / 行列式 | `\begin{bmatrix}...\end{bmatrix}` | `mat(1, 2; 3, 4)`；竖线 `mat(delim: "|", a, b; c, d)` |
| 多行对齐推导 | `\begin{aligned} ... & = ... \end{aligned}` | `$ n_i &= 1 / (rho_i q (mu_n + mu_p)) \ &= 2.37 times 10^(13) "cm"^(-3) $` |
| 积分与求和 | `\int_0^{\pi} ... dx` | `integral_0^pi ... dif x`；`sum_(k=1)^n a_k` |
| 上划线 / 向量 | `\bar{x}`, `\vec{E}` | `overline(x)`, `arrow(E)` |
| 约等号 / 大于等于 | `\approx`, `\ge`, `\le` | `approx`, `>=`, `<=` |
| 正文转义特殊字符 | `#`, `$`, `@`, `*`, `_` | 正文中字面量需写 `\#`, `\$`, `\@`, `\*`, `\_` |
| 中文加粗 | 默认 `SimSun` 无粗体 | 模板已映射 `strong` 到无衬线粗体（如 `Microsoft YaHei / PingFang SC`），直接写 `*加粗内容*` |

## 2. 模板组件 (`ee_homework_tpl.typ`) 用法速览

```typst
#import "ee_homework_tpl.typ": *

#show: ee-doc.with(
  title: "《课程名称》第 X 章课后习题解答",
  subtitle: "习题 1、2、3",
  course: "课程名称",
  author: "学号/姓名（可选）",
  date: "2026-11-23",
)

#constants-box(title: "常用物理常数与基准参数")[
  - 电子电量：$q = 1.602 times 10^(-19) "C"$（近似值 $1.6 times 10^(-19) "C"$）
]

#problem("第 1 题", title: "本征载流子浓度计算")[
  已知 $300 "K"$ 时 Ge 的本征电阻率为 $47 Omega dot.c "cm"$……
]

#solution()[
  （1）基本公式……
  $ n_i &= 1 / (rho_i q (mu_n + mu_p)) \
        &= 2.37 times 10^(13) "cm"^(-3) $
  #answer-box[本征载流子浓度 $n_i approx 2.37 times 10^(13) "cm"^(-3)$。]
  #note-box(title: "单位易错点")[迁移率单位中已含 $"cm"^2$，切勿重复乘以 $10^(-4)$。]
]

#three-line-table(
  header: ("段落序号", [段落码 $C_2 C_3 C_4$], "起始电平", "量化间隔"),
  ("1", `000`, "0", "1"),
  ("2", `001`, "16", "1"),
)

#code-block(title: "Python 验算代码")[
  ```python
  ni = 1.0 / (47 * 1.602e-19 * (3800 + 1800))
  ```
]
```

## 3. 版面避坑守则
- 数学公式中连续字母会被 Typst 解析成内置函数或斜体变量串联，单位和文字下标务必加双引号（如 `"V"`, `"Hz"`, `"eff"`, `"rms"`）。
- `block(breakable: true)` 已用于 `#problem`、`#solution`、`#constants-box`、`#note-box`、`#code-block`；若某道题很短，切勿随意手写 `#pagebreak()` 导致末页只剩两行字。
- 多行推导换行在 Typst 数学模式里用单独反斜杠 `\`（后面跟空格或换行），不要写成 `\\`。
