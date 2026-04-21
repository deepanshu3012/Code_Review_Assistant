"""
Code Analyzer using CodeBERT and CodeT5.
- CodeBERT  : embeddings + code quality classification
- CodeT5    : docstring / comment generation
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

import torch
from transformers import (
    AutoTokenizer,
    AutoModel,
    RobertaTokenizer,
    T5ForConditionalGeneration,
)


# ── Data classes ─────────────────────────────────────────────────────────

@dataclass
class CodeQualityResult:
    overall_score:       float
    complexity_score:    float
    documentation_score: float
    naming_score:        float
    issues:              list[str] = field(default_factory=list)
    suggestions:         list[str] = field(default_factory=list)
    generated_docstring: str       = ""
    embedding:           Optional[list] = None


# ── Heuristic helpers ─────────────────────────────────────────────────────

def _has_docstrings(code: str) -> bool:
    return '"""' in code or "'''" in code

def _count_comments(code: str) -> int:
    return len([l for l in code.splitlines() if l.strip().startswith("#")])

def _avg_name_length(code: str) -> float:
    names = re.findall(r'\b([a-zA-Z_]\w*)\s*(?:\(|=)', code)
    meaningful = [n for n in names if n not in {
        "if", "else", "for", "while", "def", "class",
        "return", "import", "from", "True", "False", "None",
    }]
    if not meaningful:
        return 5.0
    return sum(len(n) for n in meaningful) / len(meaningful)

def _detect_issues(code: str) -> list[str]:
    issues = []
    lines = code.splitlines()

    long = [i + 1 for i, l in enumerate(lines) if len(l) > 79]
    if long:
        issues.append(f"Lines exceeding PEP-8 limit (79 chars): {long[:5]}")

    if re.search(r'(?<![.\w])\d{2,}(?![\w.])', code):
        issues.append("Magic numbers detected — use named constants")

    if re.search(r'except\s*:', code):
        issues.append("Bare `except:` clause — catch specific exceptions")

    if re.search(r'^global\s+\w+', code, re.MULTILINE):
        issues.append("Use of `global` — consider refactoring")

    defs = re.findall(r'def\s+\w+\(([^)]*)\)', code)
    if [d for d in defs if d and ':' not in d]:
        issues.append("Function parameters missing type hints")

    if re.search(r'#\s*(TODO|FIXME|HACK)', code, re.IGNORECASE):
        issues.append("TODO/FIXME comments found — resolve before production")

    return issues

def _score_documentation(code: str) -> float:
    score = 40.0
    if _has_docstrings(code):
        score += 40.0
    comment_density = _count_comments(code) / max(len(code.splitlines()), 1)
    score += min(comment_density * 200, 20.0)
    return min(score, 100.0)

def _score_naming(code: str) -> float:
    avg = _avg_name_length(code)
    if avg < 2:   return 30.0
    if avg < 4:   return 55.0
    if avg <= 20: return 85.0 + min((avg - 4) * 1.5, 15.0)
    return 60.0

def _score_complexity(code: str) -> float:
    lines = code.splitlines()
    branches = sum(
        1 for l in lines
        if re.search(r'\b(if|elif|for|while|try|except|with)\b', l)
    )
    nesting = max(
        (len(l) - len(l.lstrip())) // 4 for l in lines if l.strip()
    ) if lines else 0
    penalty = branches * 3 + nesting * 5
    return max(100 - penalty, 10.0)


# ── Main analyzer class ───────────────────────────────────────────────────

class CodeReviewAnalyzer:
    CODEBERT_MODEL = "microsoft/codebert-base"
    CODET5_MODEL   = "Salesforce/codet5-base-codexglue-sum-python"

    def __init__(self, use_gpu: bool = False):
        self.device = torch.device(
            "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        )
        self._bert_tokenizer = None
        self._bert_model     = None
        self._t5_tokenizer   = None
        self._t5_model       = None

    def _load_codebert(self):
        if self._bert_model is None:
            print("Loading CodeBERT ...")
            self._bert_tokenizer = AutoTokenizer.from_pretrained(self.CODEBERT_MODEL)
            self._bert_model     = AutoModel.from_pretrained(self.CODEBERT_MODEL)
            self._bert_model.to(self.device).eval()

    def _load_codet5(self):
        if self._t5_model is None:
            print("Loading CodeT5 ...")
            self._t5_tokenizer = RobertaTokenizer.from_pretrained(self.CODET5_MODEL)
            self._t5_model     = T5ForConditionalGeneration.from_pretrained(
                self.CODET5_MODEL
            )
            self._t5_model.to(self.device).eval()

    def get_embedding(self, code: str) -> list[float]:
        self._load_codebert()
        tokens = self._bert_tokenizer(
            code,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        )
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        with torch.no_grad():
            out = self._bert_model(**tokens)
        return out.last_hidden_state.mean(dim=1).squeeze().tolist()

    def generate_docstring(self, code: str) -> str:
        self._load_codet5()
        inputs = self._t5_tokenizer(
            code,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        ).to(self.device)
        with torch.no_grad():
            outputs = self._t5_model.generate(
                **inputs,
                max_new_tokens=128,
                num_beams=4,
                early_stopping=True,
            )
        raw = self._t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return f'"""\n{raw.strip()}\n"""'

    def analyze(
        self,
        code: str,
        language: str = "python",
        generate_doc: bool = True,
        get_embedding: bool = False,
    ) -> CodeQualityResult:
        issues     = _detect_issues(code)
        doc_score  = _score_documentation(code)
        name_score = _score_naming(code)
        comp_score = _score_complexity(code)
        overall    = (doc_score * 0.35 + name_score * 0.30 + comp_score * 0.35)

        suggestions = []
        if doc_score  < 60: suggestions.append("Add docstrings to all public functions")
        if name_score < 60: suggestions.append("Use descriptive variable names (4+ chars)")
        if comp_score < 50: suggestions.append("Reduce nesting — aim for complexity <= 10")
        suggestions.append("Run `black` for formatting and `flake8` for linting")

        docstring = ""
        if generate_doc:
            try:
                docstring = self.generate_docstring(code)
            except Exception as exc:
                docstring = f"# Could not generate: {exc}"

        embedding = None
        if get_embedding:
            try:
                embedding = self.get_embedding(code)
            except Exception:
                pass

        return CodeQualityResult(
            overall_score       = round(overall, 1),
            complexity_score    = round(comp_score, 1),
            documentation_score = round(doc_score, 1),
            naming_score        = round(name_score, 1),
            issues              = issues,
            suggestions         = suggestions,
            generated_docstring = docstring,
            embedding           = embedding,
        )