# LaTeX 讲义项目通用模板

本文档给出一套可复用的中文数学讲义 LaTeX 章节模板。它不绑定任何具体课程或学科，可用于微分几何、泛函分析、代数、概率、数论、数学物理等不同讲义项目。模板的目标是：每章可以独立编译，未来也可以较自然地合并为全书；正文朴素，定理和定义清楚；章节开头说明主线；需要连接现代观点时使用统一的“现代接口”框。

实际使用时，把本文中的占位符替换为项目自己的名称、章节标题、作者、文献数据库和学科关键词即可。

## 总体原则

一份讲义项目建议保持以下约定：

- 每章是可独立编译的 `ctexbook` 文档。
- 第一章不需要手动设置章节计数器；从第 `X` 章开始，独立编译时使用 `\setcounter{chapter}{X-1}`。
- 使用 `amsthm` 定义数学环境，再用 `tcolorboxenvironment` 给定义、定理、命题等关键环境加轻量色块。
- 章节开头使用 `chapterbox` 交代本章主线、依赖和目标。
- 当需要说明经典理论如何进入现代发展或学科前沿时，使用 `modernbox`。
- 术语尽量保持全书一致；人名、经典定理名和标准缩写可保留原文。
- 若全书有统一 `.bib` 文件，优先使用 `natbib`；若当前项目仍为单章草稿，也可以暂时使用 `thebibliography`。

## 文档类与页面

推荐文档类如下：

```tex
\documentclass[UTF8,fontset=fandol,openany,zihao=-4]{ctexbook}

\usepackage[a4paper,margin=2.6cm]{geometry}
```

说明：

- `ctexbook` 适合中文书籍和讲义结构。
- `fontset=fandol` 避免依赖本机中文系统字体，便于在不同机器上编译。
- `zihao=-4` 给出适合讲义正文的字号。
- `openany` 允许独立章节从任意页开始。
- A4 页面四周边距 `2.6cm` 较为舒展，适合含公式的数学讲义。

## 基础宏包

推荐基础宏包：

```tex
\usepackage{amsmath,amssymb,amsthm,mathtools,bm}
\usepackage{xcolor}
\usepackage[most]{tcolorbox}
\usepackage{booktabs}
\usepackage{array}
\usepackage{enumitem}
\usepackage{hyperref}
```

如果使用 BibTeX 和作者-年份引用，可增加：

```tex
\usepackage[round,authoryear]{natbib}
```

用途简述：

- `amsmath, amssymb, amsthm`：公式、数学符号和定理环境。
- `mathtools`：补充 `amsmath` 的公式工具。
- `bm`：加粗数学符号。
- `xcolor, tcolorbox`：定理块、章节提示框、接口框。
- `booktabs, array`：表格排版。
- `enumitem`：列表间距和缩进。
- `hyperref`：目录、引用和超链接。
- `natbib`：作者-年份文献引用。

## 超链接与元数据

通用超链接配置：

```tex
\hypersetup{
  colorlinks=true,
  linkcolor=blue!60!black,
  citecolor=blue!60!black,
  urlcolor=blue!60!black,
  pdftitle={课程或书名：第X章},
  pdfauthor={作者名},
  pdfsubject={课程或学科名}
}
```

如果章节文件仍处于草稿阶段，可先只保留颜色设置，合并全书时再统一设置 `pdftitle`、`pdfauthor` 和 `pdfsubject`。

## 列表样式

推荐使用紧凑但不拥挤的列表样式：

```tex
\setlist[itemize]{leftmargin=2em,itemsep=0.25em,topsep=0.25em}
\setlist[enumerate]{leftmargin=2em,itemsep=0.25em,topsep=0.25em}
```

## 定理环境

建议让主要数学环境共享同一个按章编号的计数器：

```tex
\theoremstyle{definition}
\newtheorem{definition}{定义}[chapter]
\newtheorem{example}[definition]{例}
\newtheorem{exercise}[definition]{习题}
\newtheorem{convention}[definition]{约定}

\theoremstyle{remark}
\newtheorem{remark}[definition]{评注}

\theoremstyle{plain}
\newtheorem{theorem}[definition]{定理}
\newtheorem{proposition}[definition]{命题}
\newtheorem{lemma}[definition]{引理}
\newtheorem{corollary}[definition]{推论}
```

编号效果为“章号.序号”，例如第二章第一个定义为 `定义 2.1`。

## 定理块样式

模板采用 `amsthm` 负责语义和编号，`tcolorboxenvironment` 负责视觉样式。

定义块：

```tex
\tcolorboxenvironment{definition}{
  colback=blue!2!white,
  colframe=blue!45!black,
  boxrule=0.4pt,
  arc=1.2mm,
  breakable
}
```

定理块：

```tex
\tcolorboxenvironment{theorem}{
  colback=orange!3!white,
  colframe=orange!55!black,
  boxrule=0.4pt,
  arc=1.2mm,
  breakable
}
```

命题块：

```tex
\tcolorboxenvironment{proposition}{
  colback=orange!2!white,
  colframe=orange!50!black,
  boxrule=0.4pt,
  arc=1.2mm,
  breakable
}
```

如需突出引理、推论，也可为 `lemma`、`corollary` 增加相同或更淡的色块。默认情况下，例、习题、约定和评注可保持普通 `amsthm` 风格。

## 章节导读框与接口框

章节导读框：

```tex
\newtcolorbox{chapterbox}{
  colback=gray!5!white,
  colframe=gray!55!black,
  boxrule=0.4pt,
  arc=1.2mm,
  breakable
}
```

现代接口框：

```tex
\newtcolorbox{modernbox}{
  colback=green!3!white,
  colframe=green!45!black,
  boxrule=0.4pt,
  arc=1.2mm,
  title={现代接口},
  fonttitle=\bfseries,
  breakable
}
```

`chapterbox` 用于章节开头的路线说明；`modernbox` 用于连接经典理论、当代发展和学科前沿。若课程不是数学，也可以将标题改为“应用接口”“历史说明”“研究前沿”等。

## 常用命令

建议把跨章节公共命令放入统一导言文件或 `.sty` 文件；章节专用命令保留在本章导言区。

基础数域与常用符号：

```tex
\newcommand{\K}{\mathbb K}
\newcommand{\R}{\mathbb R}
\newcommand{\C}{\mathbb C}
\newcommand{\Q}{\mathbb Q}
\newcommand{\Z}{\mathbb Z}
\newcommand{\N}{\mathbb N}
\newcommand{\eps}{\varepsilon}
\newcommand{\dd}{\,\mathrm d}
\newcommand{\ii}{\mathrm i}
\newcommand{\ee}{\mathrm e}
```

线性代数、几何和分析常用命令：

```tex
\newcommand{\inner}[2]{\left\langle #1,#2\right\rangle}
\newcommand{\norm}[1]{\left\lVert #1\right\rVert}
\newcommand{\abs}[1]{\left\lvert #1\right\rvert}
\newcommand{\Span}{\operatorname{span}}
\newcommand{\rank}{\operatorname{rank}}
\newcommand{\tr}{\operatorname{tr}}
\newcommand{\Id}{\operatorname{Id}}
\newcommand{\grad}{\operatorname{grad}}
\newcommand{\diver}{\operatorname{div}}
```

范畴、代数或几何项目可按需补充：

```tex
\newcommand{\Hom}{\operatorname{Hom}}
\newcommand{\End}{\operatorname{End}}
\newcommand{\Aut}{\operatorname{Aut}}
\newcommand{\Spec}{\operatorname{Spec}}
\newcommand{\Mod}{\operatorname{Mod}}
\newcommand{\SO}{\operatorname{SO}}
\newcommand{\GL}{\operatorname{GL}}
```

## 单章骨架

单章文件的基本结构如下：

```tex
\documentclass[UTF8,fontset=fandol,openany,zihao=-4]{ctexbook}

% 公共宏包与命令

\title{课程或书名\\[0.5em]\large 第X章：章节标题}
\author{作者名或讲义草稿}
\date{\today}

\begin{document}

\maketitle
\tableofcontents

% 第一章可省略；第 X 章独立编译时保留：
\setcounter{chapter}{X-1}

\chapter{章节标题}
\label{ch:chapter-label}

\begin{chapterbox}
本章导读文字：说明对象、主线、依赖和目标。
\end{chapterbox}

\section{第一节标题}
\label{sec:first-section}

正文。

\section*{本章小结}
\addcontentsline{toc}{section}{本章小结}

小结文字。

\section*{习题}
\addcontentsline{toc}{section}{习题}

\begin{exercise}
题目。
\end{exercise}

\section*{文献说明}
\addcontentsline{toc}{section}{文献说明}

文献说明文字。

\end{document}
```

## 参考文献

若项目使用统一 `.bib` 文件，可采用：

```tex
\usepackage[round,authoryear]{natbib}

\setcitestyle{
  authoryear,
  round,
  aysep={,\nobreak\hspace{0.18em}},
  yysep={;\nobreak\hspace{0.18em}},
  citesep={;\nobreak\hspace{0.25em}}
}

\renewcommand{\bibname}{参考文献}
```

章节末尾：

```tex
\bibliographystyle{plainnat}
\bibliography{项目文献库名}
```

若尚未建立 `.bib` 文件，单章草稿可暂用：

```tex
\begin{thebibliography}{99}

\bibitem{Key}
Author,
\emph{Title},
Publisher, Year.

\end{thebibliography}
```

合并全书时，建议迁移到统一 `.bib` 文件。

## 编译方式

如果章节文件已经写入 `fontset=fandol`，可直接运行：

```bash
PATH=/Library/TeX/texbin:$PATH latexmk -xelatex -interaction=nonstopmode -halt-on-error chapterX.tex
```

若不想修改源文件，也可在命令行传入字体选项：

```bash
PATH=/Library/TeX/texbin:$PATH xelatex -interaction=nonstopmode -halt-on-error '\PassOptionsToClass{fontset=fandol}{ctexbook}\input{chapterX.tex}'
```

使用 BibTeX 时，典型顺序为：

```bash
xelatex chapterX.tex
bibtex chapterX
xelatex chapterX.tex
xelatex chapterX.tex
```

`latexmk -xelatex` 通常会自动处理多次编译。

## 日志检查

编译后建议检查：

```bash
rg -n "Undefined|undefined|Citation|Reference|Rerun|Label\\(s\\)|Package natbib Warning|Warning--|I couldn't|There were|multiply defined|LaTeX Warning|Package rerunfilecheck Warning" chapterX.log chapterX.blg
rg -n "Missing character|Token not allowed|Overfull|Font Warning" chapterX.log
```

一般应修复：

- 未定义引用或文献键。
- 字符缺失。
- 明显 `Overfull \hbox`。
- 需要重跑的交叉引用或目录警告。

通常可以容忍但应留意：

- 少量 `Underfull \vbox`。
- 非关键字体替代提示。

## 维护建议

项目进入稳定阶段后，建议：

1. 抽取公共导言区为 `project_preamble.tex` 或 `.sty` 文件。
2. 每章只保留本章标题、章节计数器、章节专用命令和正文。
3. 统一文献数据库、符号表、索引命令和交叉引用前缀。
4. 在合并全书前，统一检查章节编号、环境编号、目录层级和参考文献格式。
