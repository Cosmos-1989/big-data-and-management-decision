# Course Material Standards

本文档记录《大数据与管理决策基础》课程材料的当前开发标准，用于后续各周讲义、slides、代码、作业与 PDF 成品的一致性检查。

## 1. 讲义标准

1. 讲义使用 `ctexbook` 和 XeLaTeX 编写，每讲作为可独立编译的单章文件，源文件保存为 `docs/lecture_notes/NN_topic.tex`。
2. 讲义公共导言统一放入 `docs/latex/bdm_lecture_preamble.tex`。单讲文件只保留文档类、公共导言输入、标题元数据、章节计数器、章节标题和正文。
3. 每讲开头使用 `chapterbox` 给出章节导读，说明本讲对象、主线、依赖和目标；使用 `modernbox` 说明本讲与课程主线、现代企业数据系统或管理决策实践的接口。
4. 正文中文字体使用常规宋体风格，不使用显式加粗正文；公共导言在 `fontset=fandol` 基础上显式绑定 TeX Live 的 Fandol OTF 文件，并将 `BoldFont` 映射到 regular 字重，以保证 PDF 渲染和本机预览稳定。
5. 讲义叙述应 self-contained：先说明管理问题，再引入数据结构、统计或算法表达，最后回到可执行行动与反馈治理。
6. 每讲至少包含学习目标、核心概念、形式化表达、企业案例、代码或实验入口、练习题、常见误区和参考文献。
7. 文献应优先使用经典教材、标准、官方文档和可核查论文；不得留下占位引用。
8. 数学、统计、规则、习题和案例环境优先使用 `amsthm` 语义环境，并由 `tcolorbox` 提供轻量视觉样式，避免用纯段落标题替代可引用结构。

## 2. Slides 标准

1. Slides 使用 `ctexbeamer` 和 XeLaTeX 编写，公共导言统一放入 `slides/common/bdm_beamer_preamble.tex`，源文件保存到对应周次目录。
2. Slides 不是讲义的简单摘抄，而应服务课堂讲解节奏：目标、核心命题、概念图、公式、SQL/代码片段、案例讨论和小结。
3. 页内文本保持克制，避免长段正文；重要概念通过表格、流程、公式或最小代码片段呈现。
4. Beamer 中文字体同样使用 regular 字重，避免标题、block 或正文出现不必要的粗黑效果。
5. 每份 slides 至少包含标题页、学习目标、课程主线定位、关键技术页、案例或代码页、课堂讨论页和总结页。

## 3. 代码与实验标准

1. 每周代码应放入 `src/bdm_decision/cases/` 或相应功能模块，并能够被学生直接阅读和运行。
2. 样例数据放入 `data/sample/`，字段名稳定、粒度清晰、可被 SQL 与 Python 共同使用。
3. 指标、数据字典、SQL 脚本和 Python 计算应互相一致，避免“讲义口径”和“代码口径”分离。
4. 对关键函数和指标计算补充轻量测试。若外部依赖尚未安装，至少提供纯 Python smoke test。

## 4. 编译与验收标准

1. 每次完成讲义和 slides 后，用 XeLaTeX 至少编译两遍 PDF，以稳定目录、章节编号、页码和内部引用。
2. 检查编译日志，重点排除 `fontspec Error`、`Missing $`、`Undefined control sequence`、明显 `Overfull`、unresolved label 和需要重跑的引用警告。
3. 使用 PDF 渲染检查封面、目录页、章节开头页、中间页和末页，确认中文显示正常、正文不加粗、表格和代码不溢出。
4. 生成的 PDF 与源文件一并保留，临时渲染文件放入 `tmp/` 并由 `.gitignore` 忽略。
