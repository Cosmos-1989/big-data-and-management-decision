# datasci.biz 发布核验

主站：https://datasci.biz/

## 已验证

- GitHub 账户已验证域名归属，Pages 的 `protected_domain_state` 为 `verified`。
- 根域四条 A 记录为 GitHub Pages 官方地址，原停放记录已替换。
- `www` 的 CNAME 为 `cosmos-1989.github.io`。
- NS、`_domainconnect`、`_dmarc` 及 GitHub 归属验证 TXT 均保留。
- 主域名严格 TLS 校验通过，HTTP 200；强制 HTTPS 已启用，四个源站 IP 均返回 301 到 HTTPS。
- 旧 GitHub Pages 地址自动跳转到主域名。
- 发布分支 `47063222d2c836392136b017bce7c94c6eee5669` 的部署结果为成功。
- 19 个核心公开文件与本地文件逐字节一致，包括幻灯片、案例、术语、字体及 CNAME。
- 与迁移前源码版本 `614e40335e736621d4cd936890d22331c8f5ea22` 相比，全部原课程文件保持不变，仅新增 CNAME。
- 浏览器实测：首页、讲义、幻灯片翻页、Python 实验及 DuckDB-WASM SQL 查询正常。

## WWW HTTPS 与规范地址：已完成

2026-10-17 12:33—12:35（北京时间）完成复核：

- GitHub Pages 的证书状态为 `approved`，证书同时覆盖 `datasci.biz` 和 `www.datasci.biz`，强制 HTTPS 保持启用。
- 实际连接取得的 Let's Encrypt 证书通过严格 TLS 校验，两个域名均列于证书 SAN 中；本次证书有效期至 2027-01-15。
- `https://www.datasci.biz/` 返回 301，跳转至 `https://datasci.biz/`，最终返回 200。四个 GitHub Pages IPv4 地址分别测试均通过证书验证及 301 跳转检查。
- HTTP 主域、HTTP WWW、HTTPS 主域及 HTTPS WWW 均最终到达 HTTPS 主域；子路径与查询参数保留。
- 浏览器从 `https://www.datasci.biz/#/chapter/01_intro?anchor=slides` 进入后，到达同一路由及锚点的主域地址，讲义与幻灯片正常显示。
- 从 WWW 与主域分别读取的 19 个核心文件均与本地发布文件逐字节一致。
- GitHub 最新 DNS health 将 WWW 识别为 GitHub 用户域名，`is_https_eligible`、`responds_to_https` 为 `true`，`https_error` 为 `null`。

本次所有 HTTPS 验收均保留证书验证，未使用跳过 TLS 校验或浏览器安全警告的方式。

## 证据文件

- `pages-before.json`、`pages-after.json`：Pages 配置与证书状态。
- `public-dns-check.json`、`preserved-records.json`：公开 DNS 与原有记录保留情况。
- `public-files.json`、`public-files-www.json`：从主域及 WWW 读取的 19 个文件与本地文件的 SHA-256 比较。
- `deployment-after.json`：成功部署的版本与运行链接。
- `redirects.json`、`http-origin-redirects.json`：首次发布时的历史检查与网络限制记录；其中证书签发前的失败已由以下最终验收取代。
- `www-final-check.json`、`www-edge-check.json`：最终地址跳转、严格 TLS 校验与四个 IPv4 地址检查。
- `www-certificate.json`、`www-active-certificate.pem`：实际连接的证书摘要与公开证书，包含主域及 WWW。
- `www-health-latest.json`、`www-observations.jsonl`、`www-investigation.md`：最终健康状态、恢复过程及判断依据。
- `www-browser-check.json`、`www-browser-live.png`：WWW 入口跳转后保留讲义路由与锚点的浏览器证据。
- `course-preservation-and-browser.json`：内容保留与浏览器测试。
- `home-live.png`、`sql-live.png`：公开网站截图。
