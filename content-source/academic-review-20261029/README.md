# 前五讲学术审订版

本目录保存五份课程讲义、五套网页幻灯片与七则案例的审订源。基线及审读记录保存在 `review/academic-review-20261029/`。构建不会重置其他讲的内容。

```sh
npm run build:academic-review
node scripts/verify-slides.mjs
python3 scripts/verify-teaching.py
python3 scripts/verify-content.py
python3 scripts/verify-concept-links.py --review-dir review/academic-review-20261029/concepts
```

后两项校验需要 Beautiful Soup。第一至第五讲的页数依次为50、47、52、55、59页。案例保留已披露事实、来源和原有适用范围。原讲义的公式、代码、图片、锚点和超链接由构建器核对。
