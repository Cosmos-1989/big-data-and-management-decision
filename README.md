# 大数据与管理决策基础 · 交互式课程网站

静态课程网站。采用浅白背景、蓝灰色强调与衬线标题；双层导航、章节侧栏和页内目录参考 Claude 文档页的阅读结构。首页、讲义、幻灯片与实验室使用统一的边框、间距和浅色面板，支持快捷搜索章节、资料及主题词条。支持桌面与移动端，保留东北大学原始校标。所有计算在访客的浏览器执行；不需要后端 Python 服务或 API 密钥。

## 内容来源

- 正式正文：`../docs/textbook/`，10 章、4 附录、前言和全书结构；下载版教材为 194 页。
- 19 幅图使用原始 TikZ 导出 SVG；表格、公式、练习与引用从 TeX 转换。图形在正文中铺满可用宽度；手机端可横向滑动或放大查看。
- 16讲共712页原生HTML授课幻灯片，包含问题定义、概念阐释、公式推导、分步算例、企业案例和结论；每页链接到讲义中对应小节，可独立授课。中文采用随站加载的宋体字形，完整补足术语、推导与可复算例题，支持独立阅读。采用 16:9 授课画布与手机自然高度阅读，支持左右翻页、触屏滑动、页码跳转与全屏授课。每讲新增5个真实商业案例，共80例，均附一手资料、概念分析与证据边界；另设可搜索的案例集，支持从案例跳转至本讲相应幻灯片。
- 21 个交互实验提供背景、任务、输入、输出、约束、示例及评价要点；实验代码、教材片段和源程序提供教学注释。
- 第 11–14 单元、课程大纲、作业、综合项目、报告模板及行业案例。
- 第 12、13 单元的原文件仅含空白提纲，阅读页保留已有章节与实验的专题入口，本轮另补独立的概念阐释与企业案例幻灯片。
- `../src/bdm_decision/` 的 44 个源文件，包括 31 个已实现 Python 模块、2 个已实现 SQL 脚本和 11 个练习模板（含 YAML 配置）。模板不代表已实现算法。
- 13 份课程 CSV，数据与源码下载包。

## 本地启动

```sh
npm ci
npm run build
npm run dev
```

打开 `http://127.0.0.1:4173`。`dist/` 内的网页、内容 JSON 和图形都是已生成且纳入版本管理的交付物，因此独立检出网站也能直接启动。`npm run build` 只重建本地依赖资产，不覆盖网页或正文。

## 更新教材内容

将网站目录放在课程仓库的 `website/` 下。准备 `pandoc`、Python 的 `markdown` 与 `beautifulsoup4`。若要重新导出图形，还需原教材使用的 XeLaTeX、字体及 `pdftocairo`。

```sh
python3 scripts/build_content.py       # 自动使用已有图形
python3 scripts/enrich_content.py      # 统一参考文献、资源及内部链接
# TeX 图形发生变化时
python3 scripts/build_content.py --figures
python3 scripts/enrich_content.py
```

可通过 `PANDOC` 环境变量指定 Pandoc 路径。`dist/content/source-manifest.json` 保存正文来源哈希，更新后应重跑验证。

已有教学注释的发布版本更新正文时，使用以下流程，保留原有代码注释、实验入口和公开章节锚点：

```sh
python3 scripts/sync-reviewed-content.py
npm run build:agent
npm run build:teaching
python3 scripts/normalize-content.py
```

正文转换统一清除中文之间因源文件折行产生的空格，保留英语词间距、混排间距、代码和公式。TeX 的 `\footnote{…}` 和 Markdown 的 `[^term]` 均转为编号注释，支持正文跳转、悬停查看简释和返回原处。企业智能体构建器同样使用 Python 的 `markdown` 与 `beautifulsoup4`，可通过 `PYTHON` 环境变量指定解释器。

## 运行机制

- Python：本地托管 Pyodide 0.27.7（CPython 3.12），Web Worker 隔离执行，虚拟文件系统装载原课程 Python 文件及数据。
- 原程序编辑：写入虚拟包，再通过可见的配套示例调用；不改服务器源文件。每次运行恢复原数据与其余源文件。
- SQL：本地托管 DuckDB WASM 1.29.0，13 份 CSV 注册为视图，预建课程 KPI 视图。多语句脚本显示最后一个查询的结果。
- 图形与表格来自实时运算；支持参数调整、代码修改、图表字段选择、停止、恢复、下载代码和结果。
- 无限循环或计算过长可通过“停止”终止 Worker，120 秒自动停止。
- 输出 HTML 放在不允许脚本的 sandbox iframe；普通输出按文本处理。
- 不依赖第三方 CDN。首次 Python / SQL 运行分别需加载约 12 MB / 39 MB。DuckDB WASM 拆成 3 个静态片段，避免托管单文件体积限制。
- 无跨访客状态，也不上传访客编辑的代码。运行状态只存在于浏览器会话。
- 支持可选 WebMCP `open_course_experiment`，仅打开实验，不自动执行代码。

## 验证

```sh
python3 scripts/verify-content.py
node scripts/verify-math.mjs
node scripts/verify-runtime.mjs
node scripts/verify-slides.mjs
```

验证覆盖内部内容链接、19 幅图、超过 1,200 个数学表达式、原有 Python 实验和已实现 Python 模块，以及阈值敏感性、置信区间宽度和优化约束。新增实验、SQL、课件交互和移动端配图需在浏览器中验证。

## 发布

公开课程网站：https://datasci.biz/

原 GitHub Pages 地址：https://cosmos-1989.github.io/big-data-and-management-decision/ （自动跳转至主域名）。

GitHub 使用现有课程仓库 `Cosmos-1989/big-data-and-management-decision`。网站源码单独保存在 `codex/course-website` 分支；`gh-pages` 分支的根目录保存 `dist/` 静态文件。课程仓库 `main` 分支不受网站发布影响。

网站已适配根域名及项目子目录，资源、下载、Python 和 SQL Worker 均使用相对路径。更新网站并完成验证、提交后，可从本网站 Git 仓库执行：

```sh
git fetch github gh-pages
git subtree merge --prefix=dist github/gh-pages
task_pages_commit=$(git subtree split --prefix=dist --rejoin)
git push --atomic github HEAD:refs/heads/codex/course-website "$task_pages_commit":refs/heads/gh-pages
```

Pages 设置为从 `gh-pages` 分支的根目录发布。发布前合并远端记录，可保留 GitHub 在域名设置中自动生成的 CNAME 提交；若出现冲突，核实并解决后再发布。`.nojekyll` 保留运行依赖中的下划线文件。后续推送自动触发部署。

`.openai/hosting.json` 保留原 Sites 身份及静态目录，可用于同步更新原站。不要提交父课程仓库中尚未审阅的改动。

## 授权

数智化企业运营与优化微专业。教学内容采用 CC BY 4.0；原始下载资料保留其来源与授权信息。网页设计参考 QuantEcon 的阅读结构、香蕉空间的数学内容组织，以及智谱、Claude、Moonshot 的留白、层级与光感；未复制其品牌素材。第三方运行组件采用各自许可证，随网站保存于 `dist/vendor/licenses/`。

东北大学校标使用[学校官网](https://www.neu.edu.cn/xygk/dxwh.htm)的原始透明图，保留其颜色和比例，来源记录见 `dist/assets/SOURCES.md`。

## 幻灯片审核

`review/report.md` 记录十讲逐页内容、公式、构图与实际浏览器检查。`review/index.html` 使用生产渲染器生成全页审查画面；从网站项目根目录启动静态服务器后访问 `/review/`。最终审核记录与45组宋体缩略画面保留在 `review/independent-reading/`，上一轮360页记录保留在 `review/`，不会进入公开课程网页。

## 更新幻灯片字体

`dist/assets/fonts/` 保存当前常规及加粗宋体字形子集、授权与覆盖清单。更新幻灯片文字后，使用官方 Source Han Serif CN 的 Regular/Bold OTF 和 LICENSE.txt 重新生成：

```sh
python3 scripts/subset-slide-fonts.py /path/to/official-fonts
```

脚本需要 `fonttools` 与 `brotli`，会检查中文覆盖、重命名修改后的子集并记录输入与输出哈希。

## 企业Agent专题

第14章扩展为15节完整教学内容，另有65页幻灯片、38幅教学图解、四个可运行规则实验和可下载方案包。方案包包含四份SKILL.md、中立工作流契约、部署验收表、完整程序和测试。它们使用固定虚构数据，不调用真实LLM或企业服务，产品资料与真实生产性能明确分开。新增源保存在content-source/agent-course，镜像课程仓库的讲义、项目与程序；避免重建核心教材时遗失补充内容。

重建专题：`npm run build:agent`；重建字体后运行`node scripts/verify-slides.mjs`与`node scripts/verify-diagrams.mjs`。若从父仓库重新导出全书，先运行原内容脚本，再运行专题脚本。完整覆盖对照与运行、浏览器审核在review/agent-course/。

## 全课程术语与真实案例

`content-source/teaching-20261017/` 保存16讲的审订源、首用术语台账、80例商业案例及来源核查。`npm run build:teaching` 在专题导出后合并审订版本，生成幻灯片、案例集、搜索词条和来源清单。构建器先同步企业Agent源，支持重复运行。各组的旧版基准独立保存或固定到Git提交，避免从已合并页面重复插入内容。

首用解释逐讲独立核对，也包括图示中提前出现的术语。第15、16讲在综合项目页分别呈现。资料原文与课堂解释分别标示；公开案例不作为对收益的独立因果验证。

```sh
BDM_SLIDES_BASELINE=/path/to/pre-edit-slides.json python3 scripts/verify-teaching.py
node scripts/verify-slides.mjs
node scripts/verify-diagrams.mjs
```

逐页渲染、展开讨论、字体覆盖、内容保护与线上验收记录见 `review/teaching-20261017/`。`review/` 使用生产渲染器，可检查全部712页；本轮记录补充此前历史审核。

## 自定义域名

`dist/CNAME` 固定为 `datasci.biz`，每次发布都须保留。域名在GoDaddy管理，根域的四条A记录指向GitHub Pages：185.199.108.153、185.199.109.153、185.199.110.153、185.199.111.153；www的CNAME直接指向Cosmos-1989.github.io，不包含仓库名。DNS和证书核验记录见review/domain-datasci-20261017。不要改动与网站无关的邮件、NS或TXT记录。
