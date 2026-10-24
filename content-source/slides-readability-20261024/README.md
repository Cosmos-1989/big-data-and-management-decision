# 第二、第三讲幻灯片修订

本目录保存网页页顶幻灯片的完整作者源。第二讲固定为 47 页，第三讲固定为 52 页。讲义正文不由此目录生成。

```sh
npm run build:slides-reviewed
node scripts/verify-readable-slides.mjs
node scripts/verify-slides.mjs
python3 scripts/verify-teaching.py
```

构建仅替换 `dist/content/lecture-slides.json` 中这两讲，校对讲义参考位置，并同步 `lecture-terms.json` 中的页标题。`source-manifest.json` 记录作者源哈希。完整教学内容重建也会在最后应用此修订。

`takeaway` 是可选字段；正文已经说明的内容不再另设“结论”面板。原图解的数值、公式、代码、案例资料和讲义锚点保持不变。

修订前内容、独立审读记录、逐页版式检查及发布核验位于 `review/slides-readability-20261024/`。
