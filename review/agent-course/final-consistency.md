# 企业 Agent 专题最终一致性核查

日期：2026-10-12。只读核查范围为当前 `website` 工作树及其关联的课程源文件；未修改源文件，未重复运行已通过的 48 项和 159 项测试。对照基准为网站仓库 Git 提交 `5cff00bc9555d6c524831cf0539e46234de0711d`。

## 数量与保留性

- 目录注册 14 个数字编号课程章节，01—14 均具有实际 JSON 页面。
- 第十四章有 15 个二级教学节，55 页授课幻灯片，4 个实验。
- 55 页中包含 **38 个结构化图解**：21 个关系/流程图、15 个矩阵、1 个条形图、1 个曲线图。此外，讲义正文插入 8 个图解；“38 图”指幻灯片图解，不能写成讲义正文有 38 图。
- 原 10 讲幻灯片页数为 37、33、38、43、45、44、39、42、37、45，共 **403 页**。当前 JSON 中这 10 个讲次对象与基准提交逐项反序列化比较完全相等，未覆盖或修改原页面。
- 当前幻灯片合计 458 页（403 + 55）。原 10 个讲义页面的 HTML 原文仍为当前 HTML 的完整前缀；其原目录项保持顺序及内容，第十章仅在末尾附加专题入口。
- 新章幻灯片源文件与发布 JSON 的 55 个标题和顺序一致。4 个发布实验与 `experiments.json` 去除说明字段后的对象完全一致，实验说明中的注释代码也与实际可执行代码一致。

## 源码一致性

以下模块副本的 SHA-256 完全一致：

```text
191268253ba6d68df1208093bc863a54edf9f31dd2df97751183b019d16f902e
```

1. 课程主源：`src/bdm_decision/cases/week14_enterprise_agents.py`。
2. 网站镜像：`website/content-source/agent-course/week14_enterprise_agents.py`。
3. 程序目录：`dist/content/catalog.json` 中 `week14_enterprise_agents` 的源码字符串。
4. 浏览器运行文件：`dist/data/files.json` 中该模块源码。
5. 单文件下载：`dist/downloads/enterprise-agent-experiments.py`。
6. 专题 ZIP 内模块。
7. 总课程代码 ZIP 内模块。
8. 独立检查 JSON、网站保存的检查 JSON，以及独立解压包检查 JSON 所记录的被测源码 SHA。三个记录均为 159/159，且所测源码与以上最终源码相同。

专题 ZIP 内两份测试脚本分别与网站 `content-source/agent-course/tests` 中对应文件字节相同。专题讲义和结课项目的主源与网站镜像字节相同；单独下载的专题讲义也与网站源文件相同。

## 下载包与说明

- `enterprise-agent-kit.zip`：76,847 字节，**17 个条目**，名称无重复，`ZipFile.testzip()` 返回 `None`，CRC 检查通过。
- `course-code-data.zip`：72 个条目，CRC 检查通过，含最终 Agent 模块。
- 专题包中的 README 与镜像 README 字节一致。最初发现其误称包中附带 `enterprise-agent-experiments.py`，根代理已修正并重打包。最终说明正确指向包中 `src/bdm_decision/cases/week14_enterprise_agents.py`，使用 `PYTHONPATH=src`，并明确单文件程序在网站另外下载。该说明矛盾已经解决。

## 字体与引用

- 字体 manifest 的内容 SHA 与当前完整 `lecture-slides.json` 的 SHA 相同。
- 依照字体生成脚本的取字范围重新计算，应包含 1,180 个汉字，与 manifest 一致。
- 400、700 两个字重均登记 `missingCjk=[]`，缺字数为零；发布 WOFF2 文件的字节数及 SHA 与 manifest 一致。
- 对当前全部 **458 个 `detailRef`** 逐一检查：目标章节存在，目标锚点真实存在，错误数为零；其中新章 55 个引用全部有效。
- 对目录中的全部 14 章及专题导航页，检查目录锚点、内部章节路由及章节路由附带锚点，错误数为零。新章没有重复锚点。专题内 `#/lab/agent-*` 路由均对应四个实际实验。

## 结论

当前数量、原课保留性、模块副本、测试记录、下载包、字体 manifest 及内部引用一致。初次发现的 ZIP README 路径矛盾已修复，**无剩余一致性阻断**。

本核查确认的是本地待发布工作树及下载产物；不把这些检查等同于远端发布成功或新网址的在线验收。
