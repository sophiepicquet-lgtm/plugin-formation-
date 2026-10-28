#!/usr/bin/env python3
"""
detect.py - a five-check panel that scores how machine-written a draft looks.

What this is:  five local heuristics modelled on the signals public AI
detectors actually measure - sentence-length variation, concreteness, stock
vocabulary, typographic fingerprint, and voice. Every score is computed on
your machine from the text alone. Nothing is uploaded.

What this is NOT:  GPTZero, Originality, Copyleaks, Winston or Turnitin.
It does not call their APIs and it cannot promise their verdict. It catches
the things they all key on, which is why fixing them tends to move their
numbers too - but the only honest claim is the one on this line.

Each check returns a HUMAN score from 0 to 100. Higher is better.

Usage
  python3 detect.py draft.txt
  pbpaste | python3 detect.py -
  python3 detect.py draft.txt --json
  python3 detect.py before.txt after.txt      # compare two drafts
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")
LEX_FR = os.path.join(HERE, "slop_fr.json")

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-z']+")
CONTRACTIONS = re.compile(r"\b\w+'(?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE)
PRONOUNS = re.compile(r"\b(i|me|my|mine|we|us|our|you|your)\b", re.IGNORECASE)
NUMBERS = re.compile(r"\b\d[\d,.]*%?\b|\$\d")
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b", re.MULTILINE)

# French mode (added for French LinkedIn posts).
WORD_RE_FR = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")
PRONOUNS_FR = re.compile(r"(?<!\w)(je|j['’]|moi|mon|ma|mes|nous|notre|nos|on|tu|toi|ton|ta|tes"
                         r"|vous|votre|vos)(?!\w)", re.IGNORECASE)
NUMBERS_FR = re.compile(r"\b\d[\d,.   ]*\s?(?:%|€|k€|M€)?|\b\d+(?:h|min)\b")
PROPER_FR = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿœ]{2,}\b", re.MULTILINE)
FR_STOP = {"le", "la", "les", "des", "un", "une", "est", "et", "je", "pour",
           "dans", "que", "qui", "pas", "sur", "avec", "vous", "nous", "ce",
           "du", "au", "mais", "ne", "il", "elle", "sont", "plus", "aux", "cette"}
EN_STOP = {"the", "and", "is", "to", "of", "that", "it", "for", "you", "with",
           "this", "are", "was", "but", "not", "be", "have", "we", "my", "your"}
LANG = "en"


def detect_lang(text):
    """'fr' when French function words clearly outnumber English ones."""
    toks = re.findall(r"[^\W\d_]+", text.lower())
    fr = sum(t in FR_STOP for t in toks)
    en = sum(t in EN_STOP for t in toks)
    return "fr" if fr >= 3 and fr > en else "en"


def _find_pattern(find, lang="en"):
    """French: word-bounded on accents, matches ' and ’ alike.
    English: the original pattern, unchanged."""
    if lang != "fr":
        return re.compile(r"\b" + re.escape(find).replace(r"\ ", r"\s+") + r"\b", re.IGNORECASE)
    esc = re.escape(find).replace(r"\ ", r"\s+").replace("'", "['’]")
    return re.compile(r"(?<!\w)" + esc + r"(?!\w)", re.IGNORECASE)


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Map value onto 0-100 where `human` -> 100 and `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return (WORD_RE_FR if LANG == "fr" else WORD_RE).findall(text)


def check_burstiness(text):
    """Humans vary sentence length hard. Models write even."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, "too short to judge"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, f"variation {cv:.2f} across {len(lens)} sentences (want 0.55+)"


def check_specificity(text):
    """Numbers, names and concrete nouns. Slop is abstract."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "too short to judge"
    per100 = 100 / len(w)
    if LANG == "fr":
        hits = len(NUMBERS_FR.findall(text)) + len(set(PROPER_FR.findall(text)))
    else:
        hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * per100
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} concrete markers, {density:.1f} per 100 words (want 4+)"


def check_slop(text, lex):
    """Stock vocabulary density against the lexicon."""
    w = words(text)
    if not w:
        return 50.0, "empty"
    hits, found = 0, []
    for entry in lex["words"] + lex["phrases"]:
        pattern = _find_pattern(entry["find"], LANG)
        n = len(pattern.findall(text))
        if n:
            hits += n
            found.append(entry["find"])
    density = hits * 100 / len(w)
    score = scale(density, human=0.0, machine=4.0)
    detail = f"{hits} stock terms, {density:.1f} per 100 words"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Characters a phone keyboard does not produce."""
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    if LANG == "fr":
        em -= len(re.findall(r"(?m)^[ \t]*—", text))   # dialogue / list dash
    ellip = text.count("…")
    if LANG == "fr":
        # ’ and the no-break spaces of : ; ! ? « » are normal French typography.
        curly = sum(text.count(c) for c in "\u2018\u201c\u201d")
        nbsp = sum(text.count(c) for c in "\u2009\u2007\u2003\u2002")
    else:
        curly = sum(text.count(c) for c in "\u2018\u2019\u201c\u201d")
        nbsp = sum(text.count(c) for c in "\u00a0\u202f\u2009")
    total = invisible * 4 + em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisible, {em} em dash, {curly} curly quote, "
              f"{ellip} ellipsis, {nbsp} hard space")
    return score, detail


def check_voice(text, lex):
    """Contractions, person, and the shapes models default to."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "too short to judge"
    per100 = 100 / len(w)
    contractions = len(CONTRACTIONS.findall(text)) * per100
    person = len((PRONOUNS_FR if LANG == "fr" else PRONOUNS).findall(text)) * per100
    tells = 0
    names = []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    if LANG == "fr":
        # Elisions (j', l', c') are compulsory in French: they say nothing
        # about who wrote the text, so person and tells carry the check.
        score = (scale(person, human=8.0, machine=1.0) * 0.55
                 + clamp(100 - tells * 22) * 0.45)
    else:
        score = (scale(contractions, human=3.0, machine=0.0) * 0.35
                 + scale(person, human=8.0, machine=1.0) * 0.35
                 + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("uniform-bullets")
    if LANG == "fr":
        detail = (f"{person:.1f} pronoms personnels pour 100 mots, "
                  f"{tells} tic(s) de structure")
    else:
        detail = (f"{contractions:.1f} contractions, {person:.1f} personal pronouns "
                  f"per 100 words, {tells} structural tell(s)")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["BURSTINESS", "SPECIFICITY", "SLOP DENSITY", "FINGERPRINT", "VOICE"]


def run(text, lex):
    results = {}
    results["BURSTINESS"] = check_burstiness(text)
    results["SPECIFICITY"] = check_specificity(text)
    results["SLOP DENSITY"] = check_slop(text, lex)
    results["FINGERPRINT"] = check_fingerprint(text)
    results["VOICE"] = check_voice(text, lex)
    scores = [results[c][0] for c in CHECKS]
    # The weakest check drags the verdict: a detector only needs one signal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "PASS" if overall >= 70 and min(scores) >= 55 else (
        "REVIEW" if overall >= 50 else "FLAGGED")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "AI DETECTION PANEL" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'HUMAN SCORE':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "PASS":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Weakest signal: {weakest}. Fix that first.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Score how machine-written a draft looks.")
    ap.add_argument("input", nargs="?", default="-", help="file, or - for stdin")
    ap.add_argument("compare", nargs="?", help="second file, to show before/after")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=None,
                    help="path to the lexicon (default: slop.json, or slop_fr.json in French)")
    ap.add_argument("--lang", choices=["auto", "en", "fr"], default="auto",
                    help="language of the draft (default: auto-detect)")
    args = ap.parse_args()

    read = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    global LANG
    LANG = detect_lang(targets[0][1]) if args.lang == "auto" else args.lang
    lex = json.load(open(args.lexicon or (LEX_FR if LANG == "fr" else LEX), encoding="utf-8"))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex)
        payload.append({
            "source": name,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
            "lang": LANG,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex)
        render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(f"  {a['human_score']:.1f} {a['verdict']}  ->  "
              f"{b['human_score']:.1f} {b['verdict']}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
