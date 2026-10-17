"""Regression cases for destructive spacing edits and broken footnote routes."""
import json
import unittest

import markdown
from bs4 import BeautifulSoup

from content_typography import normalize_document, normalize_text


class TypographyTests(unittest.TestCase):
    def document(self, html):
        document, _ = normalize_document({"id": "lesson", "title": "数据 分析", "html": html, "toc": []})
        return document, BeautifulSoup(document["html"], "html.parser")

    def test_chinese_soft_wraps_and_thin_spaces(self):
        self.assertEqual(normalize_text("设备\n状态；还需要估计 各方案。数据\u2009仓库"), "设备状态；还需要估计各方案。数据仓库")

    def test_english_words_and_mixed_script_spaces(self):
        source = "Business Intelligence 使用 SQL 查询，第 1 章讨论 95% 区间。"
        self.assertEqual(normalize_text(source), source)

    def test_inline_markup_boundary(self):
        _, soup = self.document("<p>设备 <em>状态</em> 与<strong>客户</strong> 行为。</p>")
        self.assertEqual(soup.p.get_text(), "设备状态与客户行为。")

    def test_block_boundaries_stay_separate(self):
        _, soup = self.document("<p>设备</p>\n<p>状态</p>")
        self.assertEqual(str(soup), "<p>设备</p>\n<p>状态</p>")

    def test_protected_code_math_and_attributes(self):
        html = '<p data-label="设备 状态">设备 状态 <code>设备 状态</code> <span class="math">\\(\\text{设备 状态}\\)</span></p><pre>SELECT  a, b\nFROM x</pre><svg><text>设备 状态</text></svg>'
        _, soup = self.document(html)
        self.assertEqual(soup.p["data-label"], "设备 状态")
        self.assertEqual(soup.code.get_text(), "设备 状态")
        self.assertEqual(soup.select_one('.math').get_text(), r"\(\text{设备 状态}\)")
        self.assertEqual(soup.pre.get_text(), "SELECT  a, b\nFROM x")
        self.assertEqual(soup.svg.get_text(), "设备 状态")

    def test_pandoc_note_forward_and_back_links(self):
        doc, soup = self.document('<p>仓库<a href="#fn1" class="footnote-ref" id="fnref1" role="doc-noteref"><sup>1</sup></a>。</p><section class="footnotes"><hr><ol><li id="fn1"><p>用于 分析的数据集合。<a href="#fnref1" class="footnote-back">↩︎</a></p></li></ol></section>')
        self.assertEqual(soup.select_one('.footnote-ref')["href"], "#/chapter/lesson?anchor=fn1")
        self.assertEqual(soup.select_one('.footnote-back')["href"], "#/chapter/lesson?anchor=fnref1")
        self.assertEqual(soup.select_one('.footnote-ref')["title"], "用于分析的数据集合。")
        self.assertEqual(doc["toc"][-1]["title"], "注释")

    def test_markdown_repeated_footnotes(self):
        source = "仓库[^warehouse]与仓库[^warehouse]。\n\n[^warehouse]: 用于分析的数据集合。"
        html = markdown.markdown(source, extensions=["footnotes"])
        doc, soup = self.document(html)
        self.assertEqual(len(soup.select('a[role="doc-noteref"]')), 2)
        for anchor in soup.select('a[role="doc-noteref"],a[role="doc-backlink"]'):
            self.assertTrue(anchor["href"].startswith("#/chapter/lesson?anchor="))
        again, _ = normalize_document(json.loads(json.dumps(doc)))
        self.assertEqual(again, doc)


if __name__ == "__main__":
    unittest.main()
