# WWW 证书复查

## 2026-10-17 11:44—11:47（北京时间）

- Google 与 Cloudflare 公共 DNS 结果一致：根域四条 A、WWW CNAME 均符合 GitHub Pages 官方配置；未发现限制 Let's Encrypt 的 CAA 或冲突记录。
- Pages API 的证书状态由 `dns_changed` 转为 `approved`，但域名列表仍仅含 `datasci.biz`。严格 TLS 复验确认 WWW 尚未通过，因此不将此状态计作完成。
- 11:47 的 Pages health 已将根域识别为 GitHub 地址并允许 HTTPS；WWW 仍显示有 CNAME，但未识别为 GitHub 用户域名，故尚不允许 HTTPS。
- 原 WWW 记录为 `CNAME datasci.biz`，TTL 3600 秒；约 11:29 改为 `cosmos-1989.github.io`。当前 health 字段与仍读取旧别名链的情况相符，但该结果不能证明缓存的具体位置。保持正确 DNS，等待其更新；不修改主域名或关闭 HTTPS。

## 依据与范围

- [官方配置说明](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)：根域与 WWW 配置正确时，应自动跳转。
- [GitHub 双域名 HTTPS 公告](https://github.blog/changelog/2021-04-08-github-pages-can-now-automatically-secure-the-www-variant-of-your-custom-domain/)：正确配置时可同时保护根域和 WWW。
- [官方 health-check 源码](https://github.com/github/pages-health-check/blob/master/lib/github-pages-health-check/domain.rb)：一般有效性检查与 HTTPS 签发条件不同；不将 `is_valid` 等同于证书有效。
- [GitHub 员工对重试机制的说明](https://github.com/orgs/community/discussions/31030)：访问 Pages 设置页会自动重试签发流程。
- [近期相同故障的第一手恢复报告](https://github.com/orgs/community/discussions/206519)：仅打开设置页并等待 DNS 检查后，证书纳入 WWW；这是具体成功个案，不保证本次必然采用相同时间或机制完成。

`www-observations.jsonl` 保存本次定时检查；`www-final-check.json` 保存验收脚本最新结果。只有严格 TLS 验证和规范域名跳转均通过后，才记录本项完成。

## 2026-10-17 12:29—12:35（北京时间）：恢复与最终验收

- 12:29 再次读取 Google 与 Cloudflare 公共 DNS，根域四条 A 记录及 WWW CNAME 保持正确。
- 12:31 只读访问 Pages 设置页，页面显示 DNS 检查成功。12:31:53 的 API 记录显示证书进入 `authorized`，域名列表首次同时包含主域与 WWW；12:32:53 转为 `approved`。
- 12:33 实际取得的证书同时包含 `datasci.biz` 与 `www.datasci.biz`，严格 TLS 校验通过。WWW 的 HTTPS 请求返回 301 至 HTTPS 主域，最终 200；四个 GitHub Pages IPv4 地址逐一检查均通过。
- HTTP 与 HTTPS 的两个域名入口、资源子路径及查询参数检查全部通过；WWW 与主域各 19 个公开文件均与发布版本一致。
- 12:35 浏览器从 WWW 的讲义链接进入，最终地址为 `https://datasci.biz/#/chapter/01_intro?anchor=slides`，路由及锚点保留，课程内容正常显示。同期 GitHub health 返回 WWW 可使用 HTTPS、能响应 HTTPS，且无 HTTPS 错误。

检查期间曾向 Cloudflare 官方公开 DNS 缓存工具提交 WWW 的 CNAME、A、AAAA 刷新请求，工具回报已排队。这只涉及公共递归解析缓存，不修改权威 DNS；现有证据不能证明缓存刷新或某次设置页访问是恢复的直接原因。确定的结果是双域名证书已签发，实际 TLS 与跳转验收全部通过。
