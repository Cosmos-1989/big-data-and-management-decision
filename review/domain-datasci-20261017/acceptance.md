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

## 尚在签发的别名证书

`www.datasci.biz` 的 DNS 已生效，但检查时证书尚未覆盖该名称。已在 DNS 配置完成后重新绑定同一主域名，GitHub 报告 `dns_changed`（正在请求新证书）；主域名的 HTTPS 访问正常。访问时使用 https://datasci.biz/。

GitHub 的证书流程可能需要一段时间；本次未跳过任何 TLS 校验，也未将证书申请中的状态记作已通过。参考：[GitHub 证书签发说明](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)。

## 证据文件

- `pages-before.json`、`pages-after.json`：Pages 配置与证书状态。
- `public-dns-check.json`、`preserved-records.json`：公开 DNS 与原有记录保留情况。
- `public-files.json`：19 个文件的公开及本地 SHA-256。
- `deployment-after.json`：成功部署的版本与运行链接。
- `redirects.json`、`http-origin-redirects.json`：跳转及网络限制记录。
- `course-preservation-and-browser.json`：内容保留与浏览器测试。
- `home-live.png`、`sql-live.png`：公开网站截图。
