// 理工科课程习题解答与实验推导统一 Typst 模板 (Typst 0.15+)
// 适用课程：半导体物理学、电子电力技术、通信原理、微机原理、单片机、电子线路等

#let ink = rgb("#1E293B")
#let navy = rgb("#1E3A5F")
#let muted = rgb("#64748B")
#let blue-bg = rgb("#F0F6FC")
#let blue-border = rgb("#93C5FD")
#let green-bg = rgb("#F0FDF4")
#let green-border = rgb("#16A34A")
#let green-ink = rgb("#15803D")
#let amber-bg = rgb("#FFFBEB")
#let amber-border = rgb("#D97706")
#let amber-ink = rgb("#B45309")
#let code-bg = rgb("#F8FAFC")
#let code-border = rgb("#CBD5E1")
#let rule-gray = rgb("#CBD5E1")

#let sans-cjk = ("Times New Roman", "Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC", "Source Han Sans SC")
#let serif-cjk = ("Times New Roman", "SimSun", "Songti SC", "Noto Serif CJK SC", "Source Han Serif SC")
#let mono-cjk = ("Consolas", "SF Mono", "JetBrains Mono", "DejaVu Sans Mono", "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC")

#let ee-doc(
  title: "",
  subtitle: none,
  course: none,
  author: none,
  date: none,
  body,
) = {
  set document(title: title, author: if author != none { author } else { () })

  set page(
    paper: "a4",
    margin: (top: 2.2cm, bottom: 2.1cm, left: 2.0cm, right: 2.0cm),
    header: context {
      if counter(page).get().first() > 1 {
        set text(font: serif-cjk, size: 8.5pt, fill: muted)
        grid(
          columns: (1fr, auto),
          align: (left, right),
          if course != none { course } else { "" },
          title,
        )
        v(-0.45em)
        line(length: 100%, stroke: 0.45pt + rule-gray)
      }
    },
    footer: context {
      set text(font: serif-cjk, size: 8.5pt, fill: muted)
      align(center)[
        #counter(page).display("第 1 页 / 共 1 页", both: true)
      ]
    },
  )

  set text(
    font: serif-cjk,
    size: 10.5pt,
    lang: "zh",
    region: "cn",
    fill: ink,
  )

  // Windows 下 SimSun 缺少真粗体，显式映射到黑体/雅黑等无衬线字体保证中文加粗清晰
  show strong: set text(font: sans-cjk, weight: "bold")

  set par(
    leading: 0.78em,
    spacing: 0.85em,
    justify: true,
  )

  set heading(numbering: none)
  show heading: set text(font: sans-cjk, weight: "bold", fill: navy)
  show heading: set block(sticky: true)
  show heading.where(level: 1): it => {
    v(0.65em)
    block(width: 100%, sticky: true, below: 0.6em)[
      #text(font: sans-cjk, size: 13pt, weight: "bold", fill: navy)[#it.body]
      #v(-0.45em)
      #line(length: 100%, stroke: 0.9pt + navy)
    ]
  }
  show heading.where(level: 2): it => {
    v(0.4em)
    block(sticky: true, below: 0.45em)[
      #text(font: sans-cjk, size: 11.2pt, weight: "bold", fill: navy)[#it.body]
    ]
  }
  show heading.where(level: 3): it => {
    block(sticky: true, below: 0.35em)[
      #text(font: sans-cjk, size: 10.5pt, weight: "bold", fill: navy)[#it.body]
    ]
  }

  show raw: set text(font: mono-cjk, size: 9.2pt)
  show math.equation.where(block: true): set block(spacing: 0.8em, breakable: true)
  set enum(indent: 0.8em, body-indent: 0.5em)
  set list(indent: 0.8em, body-indent: 0.5em)

  // 首页标题横幅
  if title != "" {
    let meta-parts = ()
    if course != none { meta-parts.push([课程：#course]) }
    if author != none { meta-parts.push([作者：#author]) }
    if date != none { meta-parts.push([日期：#date]) }

    block(
      width: 100%,
      inset: (bottom: 0.75em),
      below: 0.9em,
      stroke: (bottom: 1.4pt + navy),
    )[
      #align(center)[
        #text(font: sans-cjk, size: 16pt, weight: "bold", fill: navy)[#title]
        #if subtitle != none {
          v(0.3em)
          text(font: serif-cjk, size: 10.5pt, fill: muted)[#subtitle]
        }
        #if meta-parts.len() > 0 {
          v(0.35em)
          text(font: serif-cjk, size: 9.5pt, fill: muted)[#meta-parts.join("   |   ")]
        }
      ]
    ]
  }

  body
}

#let constants-box(title: "常用物理常数与基准参数", body) = {
  block(
    width: 100%,
    breakable: true,
    fill: blue-bg,
    stroke: (left: 3pt + navy, top: 0.5pt + blue-border, right: 0.5pt + blue-border, bottom: 0.5pt + blue-border),
    radius: (right: 3pt),
    inset: (x: 11pt, y: 9pt),
    above: 0.6em,
    below: 0.85em,
  )[
    #text(font: sans-cjk, size: 10.5pt, weight: "bold", fill: navy)[#title]
    #v(0.35em)
    #body
  ]
}

#let problem(num, title: none, body) = {
  v(0.45em)
  block(
    width: 100%,
    sticky: true,
    above: 0.5em,
    below: 0pt,
    fill: navy,
    radius: (top: 3pt),
    inset: (x: 10pt, y: 5.5pt),
  )[
    #text(font: sans-cjk, size: 10.5pt, weight: "bold", fill: white)[
      #num#if title != none { [ · #title] }
    ]
  ]
  block(
    width: 100%,
    breakable: true,
    above: 0pt,
    below: 0.65em,
    fill: blue-bg,
    stroke: (left: 0.8pt + blue-border, right: 0.8pt + blue-border, bottom: 0.8pt + blue-border),
    radius: (bottom: 3pt),
    inset: (x: 10pt, y: 8pt),
  )[
    #text(font: sans-cjk, weight: "bold", fill: navy)[【题目】]
    #body
  ]
}

#let solution(label: "【详细解答】", body) = {
  block(
    width: 100%,
    sticky: true,
    above: 0.3em,
    below: 0.48em,
  )[
    #text(font: sans-cjk, size: 10.5pt, weight: "bold", fill: navy)[#label]
  ]
  block(
    width: 100%,
    breakable: true,
    above: 0pt,
    below: 0.7em,
    inset: (left: 2pt),
  )[#body]
}

#let answer-box(label: "答：", breakable: false, body) = {
  block(
    width: 100%,
    breakable: breakable,
    fill: green-bg,
    stroke: (left: 3pt + green-border, top: 0.5pt + rgb("#BBF7D0"), right: 0.5pt + rgb("#BBF7D0"), bottom: 0.5pt + rgb("#BBF7D0")),
    radius: (right: 3pt),
    inset: (x: 10pt, y: 7.5pt),
    above: 0.45em,
    below: 0.75em,
  )[
    #text(font: sans-cjk, weight: "bold", fill: green-ink)[#label]#body
  ]
}

#let note-box(title: "注 / 易错点", body) = {
  block(
    width: 100%,
    breakable: true,
    fill: amber-bg,
    stroke: (left: 3pt + amber-border, top: 0.5pt + rgb("#FDE68A"), right: 0.5pt + rgb("#FDE68A"), bottom: 0.5pt + rgb("#FDE68A")),
    radius: (right: 3pt),
    inset: (x: 10pt, y: 7.5pt),
    above: 0.45em,
    below: 0.75em,
  )[
    #text(font: sans-cjk, weight: "bold", fill: amber-ink)[#title：]#body
  ]
}

#let code-block(title: none, body) = {
  block(
    width: 100%,
    breakable: true,
    fill: code-bg,
    stroke: 0.6pt + code-border,
    radius: 3pt,
    inset: (x: 10pt, y: 8pt),
    above: 0.45em,
    below: 0.75em,
  )[
    #if title != none {
      block(sticky: true, below: 0.4em)[
        #text(font: sans-cjk, size: 9.5pt, weight: "bold", fill: navy)[#title]
      ]
    }
    #body
  ]
}

#let three-line-table(
  columns: auto,
  align: center + horizon,
  header: (),
  ..rows,
) = {
  let cols = if columns == auto {
    if header.len() > 0 { header.len() } else { auto }
  } else {
    columns
  }
  let flat-cells = rows.pos().map(r => if type(r) == array { r } else { (r,) }).flatten()
  let header-cells = header.map(h => text(font: sans-cjk, size: 9.5pt, weight: "bold", fill: navy)[#h])

  block(width: 100%, above: 0.45em, below: 0.65em)[
    #set text(size: 9.5pt)
    #table(
      columns: cols,
      align: align,
      stroke: none,
      inset: (x: 6pt, y: 5pt),
      ..if header-cells.len() > 0 {
        (
          table.header(
            table.hline(stroke: 1.2pt + navy),
            ..header-cells,
            table.hline(stroke: 0.6pt + navy),
          ),
        )
      } else {
        (table.hline(y: 0, stroke: 1.2pt + navy),)
      },
      ..flat-cells,
      table.hline(stroke: 1.2pt + navy),
    )
  ]
}
