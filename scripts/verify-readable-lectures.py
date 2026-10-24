#!/usr/bin/env python3
"""Audit the first two rewritten lectures against their sources and 4836fc8.

Run after build-readable-lectures.py.  This checks publication fidelity and
preservation; its algebra checks are evidence about the stated finite models,
not a substitute for reviewing the lectures' assumptions and explanations.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "4836fc8"
CHAPTERS = ["01_intro", "02_enterprise_data_model"]
CJK = re.compile(r"[\u3400-\u9fff]")
ALLOWED = {*(chapter + ".json" for chapter in CHAPTERS), "catalog.json", "concept-map.json", "source-manifest.json", "business-cases.json", "case-cards.json", "business-casebook.json", "lecture-slides.json"}
HARD_PATTERNS = {
    "staged_contrast": re.compile(r"不是[^。！？\n]{0,160}而是"),
    "chain_metaphor": re.compile("链条"),
    "closed_loop": re.compile("闭环"),
    "multidimensional_framework": re.compile("多维框架"),
    "unexplained_english": re.compile(r"(?<![A-Za-z0-9_])(?:audit|benchmark|certified|profile|scheme)(?![A-Za-z0-9_])", re.I),
    # U+2013 between digits denotes a range, rather than a prose dash.
    "dash": re.compile(r"—|(?<!\d)–|–(?!\d)"),
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse(html):
    return BeautifulSoup(html, "html.parser")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_bytes(relative):
    result = subprocess.run(["git", "show", f"{BASELINE}:{relative}"], cwd=ROOT, capture_output=True, check=True)
    return result.stdout


def baseline_json(name):
    return json.loads(baseline_bytes("dist/content/" + name))


def clean_publication(html, author_ids=None):
    """Remove generated reading aids without erasing author-owned anchors."""
    soup = parse(html)
    for node in list(soup.select("a.knowledge-link")):
        node.unwrap()
    for node in list(soup.select("[data-knowledge-block], .knowledge-background")):
        node.decompose()
    for node in list(soup.select("[data-knowledge-reference]")):
        if author_ids is not None and node.get("id") not in author_ids:
            node.attrs.pop("id", None)
        node.attrs.pop("data-knowledge-reference", None)
    for node in list(soup.select("[data-knowledge-anchor]")):
        if author_ids is not None and node.get("id") not in author_ids:
            node.decompose()
        else:
            node.attrs.pop("data-knowledge-anchor", None)
    return soup


def normalize_tex(text):
    text = text.strip()
    for left, right in ((r"\[", r"\]"), (r"\(", r"\)")):
        if text.startswith(left) and text.endswith(right):
            text = text[len(left):-len(right)]
    text = re.sub(r"\\(?:left|right|displaystyle)\b", "", text)
    text = text.replace(r"\tfrac", r"\frac").replace(r"\dfrac", r"\frac")
    text = re.sub(r"\\(?:quad|qquad)\b|\\[,;! ]", "", text)
    text = re.sub(r"\\(?:begin|end)\{(?:aligned|align\*?|gathered)\}", "", text)
    text = text.replace("&", "").replace(r"\\", "")
    return re.sub(r"\s+", "", text).rstrip(".,;，。；")


def protected_counters(soup):
    return {
        "pre": Counter(node.get_text() for node in soup.find_all("pre")),
        "math": Counter(normalize_tex(node.get_text()) for node in soup.select(".math")),
        "images": Counter(node.get("src", "") for node in soup.find_all("img")),
        "citations": Counter(key for node in soup.select("[data-cites]") for key in node["data-cites"].split()),
    }


def counter_missing(before, after):
    return [{"value": value, "missing": count} for value, count in sorted((before - after).items())]


def check_protection(before, after):
    original, current = protected_counters(before), protected_counters(after)
    result = {}
    for kind in original:
        missing = original[kind] - current[kind]
        details = {"baseline": sum(original[kind].values()), "current": sum(current[kind].values()), "missing": counter_missing(original[kind], current[kind])}
        if kind == "math":
            covered, unresolved = [], []
            # Added intermediate steps can place an old formula in a longer
            # display.  Count each complete old expression, not isolated tokens.
            for expression, count in missing.items():
                available = sum(value.count(expression) * number for value, number in current[kind].items() if value != expression) if len(expression) >= 8 else 0
                covered_count = min(count, max(0, available))
                if covered_count:
                    covered.append({"value": expression, "count": covered_count})
                if covered_count < count:
                    unresolved.append({"value": expression, "missing": count - covered_count})
            details["coveredAsCompleteFragments"] = covered
            details["unresolved"] = unresolved
            details["passed"] = not unresolved
        else:
            details["passed"] = not missing
        result[kind] = details
    return result


def plain_for_audit(node):
    fragment = parse(str(node))
    for unwanted in list(fragment.select("pre, code, .math, svg, script, style, .citation, .footnote-ref, .footnote-backref, a.knowledge-source")):
        unwanted.decompose()
    # An externally linked source title is a title, not the author's diction.
    for external in list(fragment.select('a[href^="https://"], a[href^="http://"]')):
        external.decompose()
    text = fragment.get_text("", strip=False)
    return re.sub(r"https?://\S+", "", text).strip()


def reading_units(soup):
    for node in soup.find_all(["p", "td", "li", "dd", "h2", "h3", "summary"]):
        if node.find(["p", "td", "li", "dd"]):
            continue
        if node.find_parent("details") and node.name != "summary" and not node.find_parent("details").has_attr("open"):
            continue
        yield node


def quantile(values, numerator, denominator):
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[((len(ordered) - 1) * numerator) // denominator]


def readability(chapter, full_soup, author_soup):
    lengths, long_paragraphs = [], []
    for paragraph in author_soup.find_all("p"):
        text = plain_for_audit(paragraph)
        length = len(CJK.findall(text))
        lengths.append(length)
        if length > 220:
            long_paragraphs.append({"anchor": paragraph.get("id"), "chineseCharacters": length, "text": text})
    forbidden, sentences = [], defaultdict(list)
    # Check the visible body and the optional definitions as separate units.
    # A closed details element still contains prose requiring editorial review.
    for node in full_soup.find_all(["p", "td", "li", "dd", "h2", "h3", "summary"]):
        if node.find(["p", "td", "li", "dd"]):
            continue
        text = plain_for_audit(node)
        anchor = node.get("id") or next((parent.get("id") for parent in node.parents if isinstance(parent, Tag) and parent.get("id")), None)
        for label, pattern in HARD_PATTERNS.items():
            for match in pattern.finditer(text):
                forbidden.append({"pattern": label, "match": match.group(), "anchor": anchor, "text": text})
    for node in reading_units(author_soup):
        text = plain_for_audit(node)
        for sentence in re.split(r"[。！？；]", text):
            normalized = re.sub(r"\s+", "", sentence)
            if len(CJK.findall(normalized)) >= 30:
                sentences[normalized].append({"chapter": chapter, "anchor": node.get("id")})
    bins = {"0-30": 0, "31-60": 0, "61-120": 0, "121-180": 0, "181-220": 0, "221+": 0}
    for length in lengths:
        bucket = next((name for bound, name in ((30, "0-30"), (60, "31-60"), (120, "61-120"), (180, "121-180"), (220, "181-220")) if length <= bound), "221+")
        bins[bucket] += 1
    headings = [{"level": int(node.name[1]), "id": node.get("id"), "title": node.get_text("", strip=True)} for node in author_soup.find_all(["h2", "h3"])]
    return {"paragraphChineseLength": {"count": len(lengths), "min": min(lengths, default=0), "median": quantile(lengths, 1, 2), "p90": quantile(lengths, 9, 10), "max": max(lengths, default=0), "bins": bins}, "longParagraphCandidates": long_paragraphs, "headingOrder": headings, "forbiddenPatterns": forbidden}, sentences


class Poly:
    """Small exact Laurent polynomial ring used for independent identities."""
    names = ("alpha", "beta", "e", "c", "r", "s2", "v", "u", "D", "eps")

    def __init__(self, terms=None):
        self.terms = {key: F(value) for key, value in (terms or {}).items() if value}

    @classmethod
    def scalar(cls, value):
        return cls({(0,) * len(cls.names): F(value)})

    @classmethod
    def variable(cls, name, exponent=1):
        powers = [0] * len(cls.names)
        powers[cls.names.index(name)] = exponent
        return cls({tuple(powers): F(1)})

    def __add__(self, other):
        other = other if isinstance(other, Poly) else self.scalar(other)
        result = self.terms.copy()
        for key, value in other.terms.items():
            result[key] = result.get(key, F(0)) + value
        return Poly(result)

    __radd__ = __add__

    def __neg__(self):
        return Poly({key: -value for key, value in self.terms.items()})

    def __sub__(self, other):
        return self + (-other if isinstance(other, Poly) else -F(other))

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        other = other if isinstance(other, Poly) else self.scalar(other)
        result = defaultdict(F)
        for left, a in self.terms.items():
            for right, b in other.terms.items():
                result[tuple(x + y for x, y in zip(left, right))] += a * b
        return Poly(result)

    __rmul__ = __mul__

    def square(self):
        return self * self

    def substitute(self, variable, replacement):
        index = self.names.index(variable)
        result = self.scalar(0)
        for powers, coefficient in self.terms.items():
            exponent = powers[index]
            if exponent < 0:
                raise ValueError("Substitution into inverse monomial is not used")
            remaining = list(powers)
            remaining[index] = 0
            term = Poly({tuple(remaining): coefficient})
            for _ in range(exponent):
                term *= replacement
            result += term
        return result

    def equals(self, other):
        return not (self - other).terms


def algebra_checks():
    prior, true_positive, false_positive = F(1, 5), F(4, 5), F(1, 10)
    joint = {(1, "+"): prior * true_positive, (1, "-"): prior * (1 - true_positive), (0, "+"): (1 - prior) * false_positive, (0, "-"): (1 - prior) * (1 - false_positive)}
    losses = {"keep": {0: F(0), 1: F(100)}, "transfer": {0: F(15), 1: F(25)}}
    # Enumerate state/signal cells and choose the least joint-weighted loss in
    # each signal column.  No posterior formula is needed for this calculation.
    before = min(sum((prior if state else 1 - prior) * loss[state] for state in (0, 1)) for loss in losses.values())
    signal_losses = {signal: min(sum(joint[state, signal] * loss[state] for state in (0, 1)) for loss in losses.values()) for signal in ("+", "-")}
    after = sum(signal_losses.values())
    threshold = F(losses["transfer"][0] - losses["keep"][0], (losses["keep"][1] - losses["keep"][0]) - (losses["transfer"][1] - losses["transfer"][0]))
    finite = {"priorBestLoss": str(before), "signalPositiveJointLoss": str(signal_losses["+"]), "signalNegativeJointLoss": str(signal_losses["-"]), "informationLoss": str(after), "EVSI": str(before - after), "threshold": str(threshold)}
    checks = {"informationLoss": after == F(46, 5), "EVSI": before - after == F(39, 5), "threshold": threshold == F(1, 6)}
    a, b, e, c, r, s2, v, u, D, eps = [Poly.variable(name) for name in Poly.names]
    ci, Di, si = Poly.variable("c", -1), Poly.variable("D", -1), Poly.variable("s2", -1)
    ce = a + b * e - F(1, 2) * c * e.square() - F(1, 2) * r * b.square() * s2
    completed_agent = a + F(1, 2) * b.square() * ci - F(1, 2) * r * b.square() * s2 - F(1, 2) * c * (e - b * ci).square()
    effort = b * ci
    fixed_wage = u - F(1, 2) * b.square() * ci + F(1, 2) * r * b.square() * s2
    checks["effortCompletingSquareIdentity"] = ce.equals(completed_agent)
    checks["bindingParticipationIdentity"] = ce.substitute("e", effort).substitute("alpha", fixed_wage).equals(u)
    expected_wage = fixed_wage + b * effort
    principal = v * effort - expected_wage
    principal_by_D = v * b * ci - F(1, 2) * D * b.square() * ci - u
    checks["principalObjectiveIdentity"] = principal.equals(principal_by_D.substitute("D", 1 + r * c * s2))
    completed_principal = F(1, 2) * v.square() * ci * Di - u - F(1, 2) * D * ci * (b - v * Di).square()
    checks["optimalBetaCompletingSquareIdentity"] = principal_by_D.equals(completed_principal)
    gaussian_exponent = -r * b * eps - F(1, 2) * eps.square() * si
    completed_gaussian = -F(1, 2) * (eps + r * b * s2).square() * si + F(1, 2) * r.square() * b.square() * s2
    checks["normalExponentialMomentIdentity"] = gaussian_exponent.equals(completed_gaussian)
    beta_values = {}
    for noise, label in ((F(3), "sigmaSquared3"), (F(1), "sigmaSquared1")):
        # With v=c=r=1 the objective has linear coefficient 1 and negative
        # quadratic coefficient -(1+noise)/2; use its vertex, not a replay of
        # the printed closed-form expression for beta.
        quadratic_magnitude = F(1, 2) + noise * F(1, 2)
        linear_coefficient = F(1)
        beta_values[label] = linear_coefficient / (2 * quadratic_magnitude)
    checks["betaSigmaSquared3"] = beta_values["sigmaSquared3"] == F(1, 4)
    checks["betaSigmaSquared1"] = beta_values["sigmaSquared1"] == F(1, 2)
    maintenance = {"withoutMaintenance": F(0) + F(1, 5) * 100, "withMaintenance": F(10) + F(1, 20) * 100}
    checks["twoPeriodMaintenanceEnumeration"] = maintenance["withoutMaintenance"] == 20 and maintenance["withMaintenance"] == 15
    return {"passed": all(checks.values()), "checks": checks, "finiteDecision": finite, "twoPeriodMaintenance": {key: str(value) for key, value in maintenance.items()}, "betaValues": {key: str(value) for key, value in beta_values.items()}, "conditions": ["c>0", "r>0", "v>0", "sigmaSquared>=0", "e>=0 and beta>=0", "normal additive noise", "no extra lower bound on fixed wage", "principal compares expected profit"], "interpretation": "Exact finite arithmetic and polynomial identities verify the displayed examples under their assumptions; they do not establish model applicability or pedagogical completeness."}


def verify(content_dir, source_dir):
    errors, warnings = [], []
    baseline_sha = subprocess.run(["git", "rev-parse", BASELINE], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    config = read(source_dir / "config.json")
    if config["baseline"] != BASELINE or config["chapters"] != CHAPTERS:
        errors.append("Author configuration differs from the fixed baseline or chapter scope")
    knowledge = read(ROOT / config["conceptSource"])
    all_soups, all_ids = {}, {}
    for path in content_dir.glob("*.json"):
        data = read(path)
        if isinstance(data, dict) and isinstance(data.get("html"), str):
            soup = parse(data["html"])
            all_soups[path.stem] = soup
            all_ids[path.stem] = Counter(node["id"] for node in soup.find_all(id=True))
    chapter_results, all_sentences = {}, defaultdict(list)
    for chapter in CHAPTERS:
        author = read(source_dir / "chapters" / (chapter + ".json"))
        author_soup = parse(author["html"])
        author_ids = {node["id"] for node in author_soup.find_all(id=True)}
        current = read(content_dir / (chapter + ".json"))
        soup = all_soups[chapter]
        cleaned = clean_publication(current["html"], author_ids)
        source_matches = str(cleaned) == str(author_soup)
        if not source_matches:
            errors.append(f"{chapter}: published body differs from its author source after generated aids are removed")
        for field in ("id", "title", "source", "kind"):
            if current[field] != author[field]:
                errors.append(f"{chapter}: published metadata differs from author source: {field}")
        old = clean_publication(baseline_json(chapter + ".json")["html"])
        protection = check_protection(old, cleaned)
        for kind, detail in protection.items():
            if not detail["passed"]:
                errors.append(f"{chapter}: baseline {kind} not fully preserved")
        duplicates = [anchor for anchor, count in all_ids[chapter].items() if count != 1]
        if duplicates:
            errors.append(f"{chapter}: duplicate anchors: {duplicates}")
        old_ids = {node["id"] for node in old.find_all(id=True)}
        lost_ids = sorted(old_ids - set(all_ids[chapter]))
        if lost_ids:
            errors.append(f"{chapter}: baseline body anchors lost: {lost_ids}")
        invalid_toc = [item["id"] for item in current["toc"] if all_ids[chapter][item["id"]] != 1]
        if invalid_toc:
            errors.append(f"{chapter}: absent or ambiguous TOC targets: {invalid_toc}")
        link_errors = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if not href.startswith("#/chapter/"):
                if href.startswith("#") and not href.startswith("#/") and all_ids[chapter][unquote(href[1:])] != 1:
                    link_errors.append({"href": href, "reason": "local anchor is absent or ambiguous"})
                continue
            route = urlsplit(href[1:])
            target = unquote(route.path.removeprefix("/chapter/"))
            query = parse_qs(route.query)
            anchor = query.get("anchor", [None])[0]
            if target not in all_ids:
                link_errors.append({"href": href, "reason": "chapter has no published HTML"})
            elif anchor and anchor != "slides" and all_ids[target][anchor] != 1:
                link_errors.append({"href": href, "reason": "target anchor is absent or ambiguous"})
            if "from" in query or "at" in query:
                origin, at = query.get("from", [None])[0], query.get("at", [None])[0]
                if origin not in all_ids or all_ids[origin][at] != 1:
                    link_errors.append({"href": href, "reason": "reading return anchor is absent or ambiguous"})
                elif origin != chapter or not any(parent.get("id") == at for parent in link.parents if isinstance(parent, Tag)):
                    link_errors.append({"href": href, "reason": "return anchor does not identify the source passage"})
        if link_errors:
            errors.append(f"{chapter}: {len(link_errors)} invalid internal/return links")
        if soup.select("a a, pre a.knowledge-link, code a.knowledge-link, .math a.knowledge-link"):
            errors.append(f"{chapter}: nested links or concept links inside code/math")
        metrics, sentences = readability(chapter, soup, author_soup)
        for sentence, locations in sentences.items():
            all_sentences[sentence].extend(locations)
        if metrics["forbiddenPatterns"]:
            errors.append(f"{chapter}: {len(metrics['forbiddenPatterns'])} forbidden prose-pattern matches")
        if metrics["longParagraphCandidates"]:
            warnings.append(f"{chapter}: {len(metrics['longParagraphCandidates'])} paragraphs exceed 220 Chinese characters")
        chapter_results[chapter] = {"authorSourceMatches": source_matches, "baselineProtection": protection, "baselineAnchors": len(old_ids), "lostAnchors": lost_ids, "duplicateAnchors": duplicates, "invalidTocTargets": invalid_toc, "linkErrors": link_errors, "readability": metrics}
    missing_concepts = []
    for entry in knowledge["concepts"]:
        if all_ids.get(entry["chapter"], Counter())[entry["anchor"]] != 1:
            missing_concepts.append(entry["id"])
    for entry in knowledge["background"]:
        for chapter in entry["chapters"]:
            if all_ids.get(chapter, Counter())["term-" + entry["id"]] != 1:
                missing_concepts.append(entry["id"] + ":" + chapter)
    if missing_concepts:
        errors.append(f"Missing or ambiguous concept/background targets: {missing_concepts}")
    unchanged = []
    tracked = subprocess.run(["git", "ls-tree", "-r", "--name-only", BASELINE, "dist/content"], cwd=ROOT, capture_output=True, text=True, check=True)
    for name in tracked.stdout.splitlines():
        relative = Path(name).relative_to("dist/content")
        if str(relative) in ALLOWED:
            continue
        path = content_dir / relative
        if not path.exists() or path.read_bytes() != baseline_bytes(name):
            errors.append("Out-of-scope content differs from baseline: " + str(relative))
        else:
            unchanged.append(str(relative))
    scopes = scoped_assets(content_dir, source_dir, errors)
    manifest = read(content_dir / "source-manifest.json").get("readabilityEdition", {})
    required = {str(path.relative_to(ROOT)) for path in [source_dir / "config.json", *(source_dir / "chapters" / (chapter + ".json") for chapter in CHAPTERS), source_dir / "business-cases.json", source_dir / "case-cards.json", ROOT / config["conceptSource"]]}
    recorded = {entry["path"]: entry["sha256"] for entry in manifest.get("sources", [])}
    bad_hashes = sorted(path for path in required if path not in recorded or not (ROOT / path).is_file() or sha(ROOT / path) != recorded[path])
    if bad_hashes or set(recorded) != required:
        errors.append("Readability manifest source set/hash mismatch")
    if manifest.get("baseline") != BASELINE or manifest.get("chapters") != CHAPTERS:
        errors.append("Readability manifest has a different baseline or chapter scope")
    repetitions = [{"sentence": sentence, "occurrences": locations} for sentence, locations in all_sentences.items() if len(locations) > 1]
    algebra = algebra_checks()
    if not algebra["passed"]:
        errors.append("An exact arithmetic or algebraic identity check failed")
    return {"passed": not errors, "baseline": baseline_sha, "chapters": chapter_results, "scope": {"otherContentFilesUnchanged": len(unchanged), **scopes}, "conceptTargets": {"core": len(knowledge["concepts"]), "background": len(knowledge["background"]), "missing": missing_concepts}, "manifest": {"requiredSources": sorted(required), "mismatches": bad_hashes}, "repeatedLongSentenceCandidates": repetitions, "algebra": algebra, "warnings": warnings, "errors": errors}


def scoped_assets(content_dir, source_dir, errors):
    original_cases = baseline_json("business-cases.json")
    cases = read(content_dir / "business-cases.json")
    source_cases = read(source_dir / "business-cases.json")
    allowed_cases = {item["id"] for item in source_cases}
    expected_cases = {f"b{lesson:02d}-{index:02d}" for lesson in (1, 2) for index in range(1, 6)}
    if allowed_cases != expected_cases:
        errors.append("Author business-case scope must contain exactly the first two lectures' ten cases")
    if [item["id"] for item in original_cases] != [item["id"] for item in cases]:
        errors.append("Business-case membership/order changed")
    old_by_id, by_id = {item["id"]: item for item in original_cases}, {item["id"]: item for item in cases}
    changed_cases = [key for key in old_by_id if by_id.get(key) != old_by_id[key]]
    if set(changed_cases) - allowed_cases:
        errors.append("A business case outside lectures 1/2 changed")
    if any(by_id.get(item["id"]) != item for item in source_cases):
        errors.append("Published business cases differ from their author source")
    original_cards = baseline_json("case-cards.json")
    cards, source_cards = read(content_dir / "case-cards.json"), read(source_dir / "case-cards.json")
    allowed_cards = {item["caseId"] for item in source_cards}
    expected_cards = {"airbus-skywise-maintenance", "oracle-red-bull-simulation", "palantir-ontology-lot", "atlan-nasdaq-catalog"}
    if allowed_cards != expected_cards:
        errors.append("Author case-card scope must contain the four specified first-two-lecture cards")
    if [item["caseId"] for item in original_cards] != [item["caseId"] for item in cards]:
        errors.append("Case-card membership/order changed")
    old_cards, new_cards = {item["caseId"]: item for item in original_cards}, {item["caseId"]: item for item in cards}
    changed_cards = [key for key in old_cards if new_cards.get(key) != old_cards[key]]
    if set(changed_cards) - allowed_cards:
        errors.append("A case card outside the four allowed cards changed")
    if any(new_cards.get(item["caseId"]) != item for item in source_cards):
        errors.append("Published case cards differ from their author source")
    case_prose_patterns = []
    for item in source_cases:
        fields = {key: item[key] for key in ("title", "company", "context", "decision", "analysis", "limits") if key in item}
        fields.update({f"fact:{index}": value for index, value in enumerate(item["facts"], 1)})
        for index, question in enumerate(item["questions"], 1):
            fields.update({f"question:{index}:{key}": value for key, value in question.items()})
        for field, text in fields.items():
            for label, pattern in HARD_PATTERNS.items():
                if pattern.search(text):
                    case_prose_patterns.append({"id": item["id"], "field": field, "pattern": label, "text": text})
    for item in source_cards:
        fields = {key: item[key] for key in ("context", "takeaway", "sourceCaveat")}
        fields.update({f"flow:{index}": value for index, value in enumerate(item["flow"], 1)})
        for field, text in fields.items():
            for label, pattern in HARD_PATTERNS.items():
                if pattern.search(text):
                    case_prose_patterns.append({"id": item["caseId"], "field": field, "pattern": label, "text": text})
    if case_prose_patterns:
        errors.append(f"First-two-lecture case prose contains {len(case_prose_patterns)} forbidden pattern matches")
    old_decks, decks = baseline_json("lecture-slides.json"), read(content_dir / "lecture-slides.json")
    other_decks_unchanged = []
    if set(old_decks) != set(decks):
        errors.append("Slide-deck membership changed")
    for key, old in old_decks.items():
        new = decks.get(key)
        if key not in CHAPTERS:
            if new != old:
                errors.append("Out-of-scope slide deck changed: " + key)
            else:
                other_decks_unchanged.append(key)
        else:
            old_copy, new_copy = copy.deepcopy(old), copy.deepcopy(new)
            for deck in (old_copy, new_copy):
                for slide in deck["slides"]:
                    slide.get("detailRef", {}).pop("section", None)
                    slide.get("detailRef", {}).pop("subsection", None)
            if old_copy != new_copy:
                errors.append("Slide content changed beyond allowed reading-section labels: " + key)
            headings = {item["id"]: item["title"] for item in read(content_dir / (key + ".json"))["toc"]}
            for number, slide in enumerate(new["slides"], 1):
                reference = slide.get("detailRef", {})
                anchor = reference.get("anchor")
                if anchor not in headings:
                    errors.append(f"Slide reading target is missing: {key}:{number}")
                elif reference.get("section") != headings[anchor] or (reference.get("subsection") and reference["subsection"] != headings[anchor]):
                    errors.append(f"Slide reading label differs from its target heading: {key}:{number}")
    old_book, book = baseline_json("business-casebook.json"), read(content_dir / "business-casebook.json")
    old_soup, soup = parse(old_book["html"]), parse(book["html"])
    unrelated_book_changes = []
    for item in original_cases:
        if item["id"] in allowed_cases:
            continue
        if str(old_soup.find(id=item["id"])) != str(soup.find(id=item["id"])):
            unrelated_book_changes.append(item["id"])
    if unrelated_book_changes:
        errors.append("Out-of-scope casebook articles changed")
    for field in set(old_book) - {"html", "toc"}:
        if book.get(field) != old_book[field]:
            errors.append("Casebook metadata changed: " + field)
    old_toc = {entry["id"]: entry for entry in old_book["toc"]}
    for entry in book["toc"]:
        if entry["id"] not in allowed_cases and entry != old_toc.get(entry["id"]):
            errors.append("Out-of-scope casebook TOC entry changed: " + entry["id"])
    return {"changedBusinessCases": changed_cases, "unchangedBusinessCases": len(original_cases) - len(changed_cases), "changedCaseCards": changed_cards, "unchangedCaseCards": len(original_cards) - len(changed_cards), "otherSlideDecksUnchanged": other_decks_unchanged, "casebookUnrelatedArticleChanges": unrelated_book_changes, "caseProseForbiddenPatterns": case_prose_patterns}


def render_report(result):
    lines = ["# 前两讲重写版技术复核\n", "本报告区分源稿一致性、资料保留、导航有效性、修改范围与有限模型计算。自动验收可发现结构和算例错误，不能证明讲义论证充分、语言自然或模型适用于真实企业。\n", f"基线：`{result['baseline']}`。本次自动验收：**{'通过' if result['passed'] else '未通过'}**。\n", "## 自动验收结果\n"]
    for chapter, detail in result["chapters"].items():
        metrics = detail["readability"]["paragraphChineseLength"]
        lines.append(f"### {chapter}\n")
        lines.append(f"作者源一致：{detail['authorSourceMatches']}；原正文锚点 {detail['baselineAnchors']} 个，丢失 {len(detail['lostAnchors'])} 个；失效或歧义链接 {len(detail['linkErrors'])} 处。闭合 details 中的定义照常作为真实目标检查。\n")
        for kind, protection in detail["baselineProtection"].items():
            lines.append(f"- {kind}：基线 {protection['baseline']}，当前 {protection['current']}；保留检查 {protection['passed']}。")
        lines.append("\n正文段落可见中文字符数（不计公式、代码、引用标记和来源标题）：" + json.dumps(metrics, ensure_ascii=False) + "。\n")
        lines.append("二、三级标题次序：\n")
        lines.extend(f"- {'  ' if item['level'] == 3 else ''}{item['title']}（`{item['id']}`）" for item in detail["readability"]["headingOrder"])
        lines.append("\n词法强禁匹配与未覆盖资料：\n")
        findings = {"forbiddenPatterns": detail["readability"]["forbiddenPatterns"], "longParagraphCandidates": detail["readability"]["longParagraphCandidates"], "unresolvedMath": detail["baselineProtection"]["math"]["unresolved"], "lostAnchors": detail["lostAnchors"], "linkErrors": detail["linkErrors"]}
        lines.append("```json\n" + json.dumps(findings, ensure_ascii=False, indent=2) + "\n```\n")
    lines.append("修改范围：\n```json\n" + json.dumps(result["scope"], ensure_ascii=False, indent=2) + "\n```\n")
    lines.append("源哈希核验：\n```json\n" + json.dumps(result["manifest"], ensure_ascii=False, indent=2) + "\n```\n")
    lines.append("重复长句候选（仅提示人工检查，不以重复本身判错）：\n```json\n" + json.dumps(result["repeatedLongSentenceCandidates"], ensure_ascii=False, indent=2) + "\n```\n")
    lines.append(ALGEBRA_NOTE)
    lines.append("精确算术与恒等式实际结果：\n```json\n" + json.dumps(result["algebra"], ensure_ascii=False, indent=2) + "\n```\n")
    lines.append(CROSS_REVIEW_NOTE)
    lines.append("## 仍需人工判断的内容\n\n手审应核对：概念首次出现是否得到解释；跨节过渡是否说明所回答的问题；案例事实、教学假设和推断是否分开；公式各符号的范围、单位和决策时点是否明确；经济模型中的正态扰动、风险厌恶、固定工资无额外下界和参与约束是否与结论配套。段落长度与词法扫描仅提供定位，不能评价解释是否充分，也不能代替逐段阅读。\n\n数学保留检查忽略排版空格、定界符尺寸、对齐环境及结尾标点，检查完整公式或其在更长公式中的完整片段；无法覆盖的原式逐项列出。新增中间步骤并不自动证明旧条件得到保留。\n")
    lines.append("## 错误与提醒\n\n```json\n" + json.dumps({"errors": result["errors"], "warnings": result["warnings"]}, ensure_ascii=False, indent=2) + "\n```\n")
    return "\n".join(lines)


ALGEBRA_NOTE = r"""## 有限决策算例与激励模型的独立核验

信息算例按四个“状态—信号”单元直接枚举联合概率，不复写讲义的后验概率公式。每个信号下，分别计算维持与转移的联合加权损失并取较小者。阳性列的最优贡献为 (26/5)，阴性列为 (4)，合计 (46/5=9.2)。事前最小损失为 (17)，故信息价值为 (39/5=7.8)。令两项行动损失相等，有 (100p=15+10p)，从而阈值为 (1/6)。

激励模型采用 (c,r,v>0)、(sigma^2ge0)、(e,etage0)，正态加性扰动与无额外固定工资下界。令 (Z=alpha+eta e-ce^2/2+etaarepsilon)。正态密度指数中的配方为

[
-retaarepsilon-rac{arepsilon^2}{2sigma^2}
=-rac{(arepsilon+retasigma^2)^2}{2sigma^2}
+rac{r^2eta^2sigma^2}{2}.
]

当 (sigma^2>0) 时，将平移后的正态密度积分为1，得到指数效用的期望；再按确定性等价的定义解出
[
operatorname{CE}=alpha+eta e-rac c2e^2-rac r2eta^2sigma^2.
]

零方差时随机项为零，得到同一公式。关于努力配方：
[
operatorname{CE}=alpha+rac{eta^2}{2c}-rac r2eta^2sigma^2
-rac c2left(e-rac{eta}{c}ight)^2.
]

因为 (c>0)，经理的最优努力为 (e^*=eta/c)。参与约束取等号时，
[
alpha=ar u-rac{eta^2}{2c}+rac r2eta^2sigma^2,qquad
mathbb E[w]=ar u+rac{eta^2}{2c}+rac r2eta^2sigma^2.
]

设 (D=1+rcsigma^2>0)，将企业利润写成另一配方：
[
Pi(eta)=rac{veta}{c}-rac{Deta^2}{2c}-ar u
=rac{v^2}{2cD}-ar u-rac{D}{2c}left(eta-rac vDight)^2.
]

由 (D,c>0) 得到唯一最优激励 (eta^*=v/D)。在 (v=c=r=1) 时，(sigma^2=3) 与 (1) 分别给出 (1/4=0.25) 与 (1/2=0.5)。脚本以有理数系数的 Laurent 多项式逐项验证这些配方恒等式，并将最优努力及固定工资代回参与约束；这项核验说明代数关系一致，不证明现实中的噪声、效用、工资边界等假设成立。

"""


CROSS_REVIEW_NOTE = r"""## 交叉审查修订的复读

已依据 `cross-review-01`、`cross-review-02` 的关注点复读主线修订。

- 第一讲将订单决策限定为客户订单粒度及承诺交期前72小时；预测概率与行动效果分别说明，避免把风险排序直接作为加急排序。
- 维护比较分别处理维护消除风险与维护后存在残余风险的情形。后一情形比较维护费用加残余故障损失，与推迟维护的故障损失；停场和资源竞争费用计入相应行动。
- 新增两期维护例先规定第二期状态成本，再计算第一期两项行动的总期望成本。独立复算得到20与15，维护方案较优；该例与所述终止成本约定一致。
- 可积性、可测策略及有限状态情形的补充说明，与 Bellman 递推的概率和最优解条件配套。新增解释性建模说明区分研究目的与因果识别依据，没有将模型拟合本身当作机制成立的证明。
- 信息价值采用行动前计算的期望比较，应用后的经营改善另需实际行动、参照和结果记录。重复出现的表格分别承担分析定义与应用例示的功能，仍应结合课堂使用继续审阅其必要性。
- 第二讲的事件状态固定在事件发生时，后续活动另记事件；同一时点库存金额汇总要求币种与核算口径一致，数量汇总还要求单位和业务含义相容。
- 操纵分析段区分每次提交时分配的代理键与业务事件身份：新代理键只能区分记录，仍需根据业务事件唯一性及请求标识检查重复。相应说明已在作者源与发布正文中核对。

这些判断来自对相应新增段落的复读与有限算例复算，不由构建成功或文件哈希相同推出。

"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-dir", type=Path, default=ROOT / "dist/content")
    parser.add_argument("--source-dir", type=Path, default=ROOT / "content-source/readability-20261024")
    parser.add_argument("--report", type=Path, default=ROOT / "review/readability-20261024/technical-review.md")
    args = parser.parse_args()
    result = verify(args.content_dir, args.source_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
