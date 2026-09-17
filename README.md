# 大数据与管理决策基础 · 交互式课程网站

静态课程网站，采用章节导航、正文与页内目录布局，阅读界面参考香蕉空间，以淡蓝色顶栏、注记和定理区块组织内容。所有计算在访客的浏览器执行；不需要后端 Python 服务或 API 密钥。

## 内容来源

- 正式正文：`../docs/textbook/` 的 **2026 年 9 月学术复校版**，10 章、3 附录、前言和全书结构。
- 18 幅图使用原始 TikZ 导出 SVG；表格、公式、练习与引用从 TeX 转换。
- 119 条引用与 217 个主题索引词。
- 第 11–14 单元、课程大纲、作业、综合项目、报告模板、行业案例，以及原有课件。
- 第 12、13 单元的原文件仅含空白提纲，网页将其整理为已有章节与实验的专题阅读入口。
- `../src/bdm_decision/` 的 42 个源文件，包括 29 个已实现 Python 模块、2 个 SQL 脚本、1 个 YAML 配置与 10 个待实现模板。模板不代表已实现算法。
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
```

验证覆盖内部内容链接、图片、超过 1,100 个数学表达式、14 个 Python 实验、全部已实现 Python 模块，以及阈值敏感性、置信区间宽度和优化约束。浏览器另行验证 SQL、交互操作、错误恢复、WebMCP 和移动布局。

## 发布

公开课程网站：https://cosmos-1989.github.io/big-data-and-management-decision/

GitHub 使用现有课程仓库 `Cosmos-1989/big-data-and-management-decision`。网站源码单独保存在 `codex/course-website` 分支；`gh-pages` 分支的根目录保存 `dist/` 静态文件。课程仓库 `main` 分支不受网站发布影响。

网站已适配根域名及项目子目录，资源、下载、Python 和 SQL Worker 均使用相对路径。更新网站并完成验证、提交后，可从本网站 Git 仓库执行：

```sh
git push github HEAD:refs/heads/codex/course-website
git subtree split --prefix=dist -b codex/pages-dist
git push github codex/pages-dist:refs/heads/gh-pages
```

Pages 设置为从 `gh-pages` 分支的根目录发布。`.nojekyll` 保留运行依赖中的下划线文件。首次发布完成后，后续推送自动触发部署。

`.openai/hosting.json` 保留原 Sites 身份及静态目录，可用于同步更新原站。不要提交父课程仓库中尚未审阅的改动。

## 授权

数智化企业运营与优化微专业。教学内容采用 CC BY 4.0；原始下载资料保留其来源与授权信息。网页设计参考 QuantEcon 的阅读结构，未复制其品牌素材。第三方运行组件采用各自许可证，随网站保存于 `dist/vendor/licenses/`。

东北大学校标使用[学校官网](https://www.neu.edu.cn/xygk/dxwh.htm)的原始透明图，保留其颜色和比例，来源记录见 `dist/assets/SOURCES.md`。
