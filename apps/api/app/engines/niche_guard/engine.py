import re
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.core.database import AsyncSessionLocal
from app.engines.core.base import (
    BaseEngine,
    EngineContext,
    EngineExplanation,
    EngineHealth,
    EngineResult,
)
from app.engines.niche_guard.contracts import (
    NicheGuardFactor,
    NicheGuardInput,
    NicheGuardVerdict,
)
from app.models.niche import NicheProfile, SINGLETON_NICHE_ID
from sqlalchemy import select


class NicheGuardEngine(BaseEngine):
    """Niche Guard Engine: Deterministic, explainable filtering against the single active niche profile."""

    def __init__(self, engine_dir: Optional[Path] = None):
        if engine_dir is None:
            engine_dir = Path(__file__).resolve().parent
        super().__init__(engine_dir=engine_dir)
        self._execution_history: Dict[str, NicheGuardVerdict] = {}

    def validate_config(self) -> None:
        if not self.rules:
            raise ValueError("NicheGuardEngine rules cannot be empty.")
        if "thresholds" not in self.rules:
            raise ValueError("NicheGuardEngine rules missing 'thresholds' block.")
        if "min_pass_score" not in self.rules["thresholds"]:
            raise ValueError("NicheGuardEngine rules missing 'min_pass_score'.")
        if "weights" not in self.rules:
            raise ValueError("NicheGuardEngine rules missing 'weights' block.")

    def health(self) -> EngineHealth:
        try:
            self.validate_config()
            return EngineHealth(
                status="healthy",
                message="NicheGuardEngine is operational with valid taxonomy rules.",
                details={
                    "version": self.version,
                    "min_pass_score": self.rules.get("thresholds", {}).get("min_pass_score", 55.0),
                },
            )
        except Exception as e:
            return EngineHealth(
                status="failing",
                message=f"NicheGuardEngine health check failed: {str(e)}",
                details={"error": str(e)},
            )

    @staticmethod
    def get_fallback_taxonomy() -> Dict[str, Any]:
        """Isolated deterministic sample taxonomy for offline tests and documentation."""
        return {
            "name": "AI Engineering & Coding Automation",
            "one_sentence_definition": "Practical AI coding agents, developer automation workflows, and local LLM tooling tested on production tasks.",
            "audience": "Software developers, technical founders, and automation engineers.",
            "target_skill_levels": ["Intermediate Software Engineer", "Senior Fullstack / DevOps Engineer"],
            "audience_goals": [
                "Automate repetitive coding tasks safely",
                "Deploy local models with minimal latency",
                "Objectively evaluate agent benchmarks",
            ],
            "allowed_topics": [
                "coding agents", "local LLMs", "developer tools",
                "AI engineering", "IDE integrations", "evals and benchmarks", "workflow automation"
            ],
            "adjacent_topics": ["software architecture", "DevOps", "vector databases", "open source models"],
            "blocked_topics": [
                "crypto/web3 trading", "general consumer gadgets",
                "passive income schemes", "clickbait AI news without code/tests"
            ],
            "topic_exceptions": [
                {
                    "topic_or_keyword": "passive income schemes",
                    "allowed_contexts": ["debunking", "criticism", "quotation"],
                },
                {
                    "topic_or_keyword": "replaced all coders",
                    "allowed_contexts": ["negation", "criticism", "quotation"],
                },
            ],
            "must_have_signals": ["code repository", "reproducible benchmark", "documentation or paper", "practical tool release"],
            "negative_keywords": ["get rich quick", "secret trick", "replaced all coders", "100x money"],
            "content_pillars": [
                {
                    "id": "agent_benchmarks",
                    "name": "Coding Agent Stress Tests",
                    "keywords": ["agent", "benchmark", "coding", "stress test", "evals"],
                    "synonyms": ["coding agent benchmarks"],
                },
                {
                    "id": "local_tooling",
                    "name": "Local Models & Tooling",
                    "keywords": ["ollama", "vllm", "local", "deepseek", "inference"],
                    "synonyms": ["local llm tooling"],
                },
                {
                    "id": "automation_recipes",
                    "name": "Production Automation Recipes",
                    "keywords": ["automation", "recipe", "workflow", "developer productivity"],
                    "synonyms": ["coding workflows"],
                },
            ],
            "primary_problems": [
                "Agent benchmark claims do not match real-world coding performance.",
                "High API costs and token limits for agentic workflows.",
                "Difficulty integrating local LLMs with developer IDEs.",
                "Maintaining deterministic control over non-deterministic models.",
            ],
            "commercial_intent_topics": ["developer productivity tools", "cloud GPU hosting", "IDE extensions"],
            "evergreen_topics": ["how to set up local coding assistant", "evaluating LLM code quality", "building deterministic AI pipelines"],
            "policy_version": 1,
            "policy_fingerprint": None,
        }

    async def _get_active_niche_data(
        self,
        override: Optional[Dict[str, Any]] = None,
        allow_fallback: bool = False,
    ) -> Dict[str, Any]:
        """Fetch active singleton NicheProfile from SQLite or use provided override.
        In production mode (allow_fallback=False), missing database record raises an error
        to prevent silent fallback to demonstration taxonomy.
        """
        if override:
            return override

        try:
            async with AsyncSessionLocal() as session:
                stmt = select(NicheProfile).where(NicheProfile.id == SINGLETON_NICHE_ID)
                result = await session.execute(stmt)
                niche = result.scalar_one_or_none()
                if niche:
                    return {
                        "name": niche.name,
                        "one_sentence_definition": niche.one_sentence_definition,
                        "audience": niche.audience,
                        "target_skill_levels": niche.target_skill_levels or [],
                        "audience_goals": niche.audience_goals or [],
                        "allowed_topics": niche.allowed_topics or [],
                        "adjacent_topics": niche.adjacent_topics or [],
                        "blocked_topics": niche.blocked_topics or [],
                        "topic_exceptions": niche.topic_exceptions or [],
                        "must_have_signals": niche.must_have_signals or [],
                        "negative_keywords": niche.negative_keywords or [],
                        "content_pillars": niche.content_pillars or [],
                        "primary_problems": niche.primary_problems or [],
                        "commercial_intent_topics": niche.commercial_intent_topics or [],
                        "evergreen_topics": niche.evergreen_topics or [],
                        "policy_version": niche.policy_version or 1,
                        "policy_fingerprint": niche.policy_fingerprint,
                    }
        except Exception as e:
            if not allow_fallback:
                raise RuntimeError(f"Database error while loading active niche profile: {str(e)}") from e

        if allow_fallback:
            return self.get_fallback_taxonomy()

        raise RuntimeError(
            "Active NicheProfile 'primary' is not configured in SQLite. "
            "Complete initial niche setup in Studio Settings before evaluating content."
        )

    def _normalize_text(self, text: str) -> str:
        """Unicode NFKC normalization and lowercasing."""
        if not text:
            return ""
        return unicodedata.normalize("NFKC", text).lower().strip()

    MULTILINGUAL_ALIASES: Dict[str, List[str]] = {
        "coding agents": ["কোডিং এজেন্ট", "কোডিং এজেন্টস", "coding agent", "ai agents", "code agents"],
        "coding agent": ["কোডিং এজেন্ট", "কোডিং এজেন্টস", "coding agents", "ai agent", "code agent"],
        "local llms": ["লোকাল llm", "লোকাল এলএলএম", "local llm", "local models"],
        "local llm": ["লোকাল llm", "লোকাল এলএলএম", "local llms", "local model"],
        "developer tools": ["ডেভেলপার টুলস", "ডেভেলপার টুল", "developer tool"],
        "developer tool": ["ডেভেলপার টুলস", "ডেভেলপার টুল", "developer tools"],
        "benchmarks": ["বেঞ্চমার্ক", "বেঞ্চমার্কস", "benchmark", "benchmarking"],
        "benchmark": ["বেঞ্চমার্ক", "বেঞ্চমার্কস", "benchmarks", "benchmarking"],
        "benchmarking": ["বেঞ্চমার্ক", "বেঞ্চমার্কস", "benchmark", "benchmarks"],
        "evals and benchmarks": ["বেঞ্চমার্ক", "evals", "benchmark", "benchmarks"],
        "evals": ["ইভ্যাল", "eval", "evaluation", "evaluations"],
        "eval": ["ইভ্যাল", "evals", "evaluation"],
        "code repository": ["কোড রিপোজিটরি", "code repo", "code repositories", "repositories", "repository"],
        "code repositories": ["কোড রিপোজিটরি", "code repo", "code repository", "repositories", "repository"],
        "reproducible benchmark": ["রিপ্রোডিউসিবল বেঞ্চমার্ক", "বেঞ্চমার্ক", "reproducible benchmarks"],
        "crypto/web3 trading": ["ক্রিপ্টো ট্রেডিং", "ক্রিপ্টো", "web3 trading", "crypto trading", "crypto"],
        "passive income": ["প্যাসিভ ইনকাম"],
        "get rich quick": ["বড়লোক হওয়ার", "দ্রুত বড়লোক", "সহজে বড়লোক", "গেট রিচ কুইক"],
    }

    def _get_term_variations(self, term: str) -> List[str]:
        cleaned = self._normalize_text(term)
        if not cleaned:
            return []
        variations = {cleaned}
        for k, v in self.MULTILINGUAL_ALIASES.items():
            if k == cleaned or k in cleaned or cleaned in k:
                variations.update(v)
        for v in list(variations):
            if v.isascii():
                if v.endswith("ies") and len(v) > 4:
                    variations.add(v[:-3] + "y")
                elif v.endswith("y") and len(v) > 2:
                    variations.add(v[:-1] + "ies")
                elif v.endswith("s") and len(v) > 3:
                    variations.add(v[:-1])
                elif not v.endswith("s") and len(v) > 2:
                    variations.add(v + "s")
        return list(variations)

    def _match_term(self, term: str, text: str) -> bool:
        """Boundary-aware case-insensitive matching for words, aliases, and inflections.
        Prevents accidental substring matches (e.g. 'rust' matching 'trust').
        """
        variations = self._get_term_variations(term)
        if not variations:
            return False

        for var in variations:
            escaped = re.escape(var)
            if var.isascii():
                pattern = rf"(?:\b|^|\s){escaped}(?:\b|$|\s|[.,!?:;/\-\(\)\[\]])"
            else:
                pattern = rf"(?:^|\s|[.,!?:;/\-\(\)\[\]]){escaped}(?:$|\s|[.,!?:;/\-\(\)\[\]])"
            if re.search(pattern, text):
                return True
        return False

    def _extract_quoted_spans(self, text: str) -> List[str]:
        """Extract text segments enclosed in standard or typographical quotation marks."""
        quotes = re.findall(r'["\'“‘](.*?)["\'”’]', text)
        return [q.strip().lower() for q in quotes if q.strip()]

    def _is_contextual_critique_or_negation(
        self,
        term: str,
        corpus: str,
        raw_text: str,
        niche: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Detect whether a matched sensitive term or blocked topic occurs within:
        1. An educational critique or debunking discussion
        2. A negated claim or disclaimer
        3. A direct quotation of a marketing/third-party claim
        4. An explicitly configured topic exception
        """
        norm_term = self._normalize_text(term)

        # 1. Check explicitly configured topic exceptions in active niche profile
        exceptions = niche.get("topic_exceptions", [])
        for exc in exceptions:
            exc_term = self._normalize_text(exc.get("topic_or_keyword", ""))
            if exc_term and (exc_term in norm_term or norm_term in exc_term):
                allowed_ctxs = exc.get("allowed_contexts", [])
                # If exception exists, check if context matches
                if any(ctx in corpus for ctx in ["debunk", "myth", "critic", "not", "fail", "cannot"]):
                    return True, f"Configured topic exception for '{term}' in analytical/critique context."

        # 2. Check if the phrase is inside quoted text
        quoted_spans = self._extract_quoted_spans(raw_text)
        for span in quoted_spans:
            if norm_term in span:
                # Quotation detected: check if surrounding text contains skeptical or testing language
                skeptical_markers = [
                    "claim", "claims", "marketing", "purport", "supposed",
                    "could not reproduce", "unable to reproduce", "test", "investigat",
                    "debunk", "myth", "doubt", "unverified", "false"
                ]
                if any(m in corpus for m in skeptical_markers):
                    return True, f"Quoted claim '{term}' investigated with empirical skepticism."

        # 3. Check for negation or debunking markers in sentences containing the term
        # Split into sentence-like clauses
        clauses = re.split(r"[.!?;\n]", corpus)
        debunk_keywords = {
            "debunk", "debunking", "debunked", "myth", "cannot guarantee", "can't guarantee",
            "does not guarantee", "why ... cannot", "no guarantee", "fail", "failed", "failure",
            "flaws", "unproven", "misleading", "scam", "hoax", "investigating", "testing claims",
            "we could not reproduce", "does not prove", "do not prove", "did not prove",
            "has not replaced", "have not replaced", "did not replace", "cannot replace",
            "will not replace", "not true", "unrealistic", "overhyped", "dissecting",
            "সম্ভব নয়", "ভুল", "প্রতারণা", "ক্ষতি", "বিশ্লেষণ",
        }

        negation_markers = {
            "not", "cannot", "can't", "never", "do not", "does not", "did not",
            "has not", "have not", "isn't", "aren't", "wasn't", "weren't", "no evidence",
            "neither", "nor", "unfounded", "disproven", "নয়", "না",
        }

        term_variations = self._get_term_variations(term)

        for clause in clauses:
            matched_var = next((tv for tv in term_variations if tv in clause), None)
            if matched_var:
                # Check for debunk keywords
                for dk in debunk_keywords:
                    if dk in clause:
                        return True, f"Educational critique/debunking marker '{dk}' detected for '{term}'."
                # Check for negation markers within 8 words of the term
                clause_words = clause.split()
                try:
                    term_first_word = matched_var.split()[0]
                    if term_first_word in clause_words:
                        idx = clause_words.index(term_first_word)
                        window_start = max(0, idx - 8)
                        window_end = min(len(clause_words), idx + 8)
                        window_text = " ".join(clause_words[window_start:window_end])
                        for nm in negation_markers:
                            if nm in window_text:
                                return True, f"Negation or disclaimer marker '{nm}' detected near '{term}'."
                except Exception:
                    pass

        return False, ""

    def evaluate_item(self, item: NicheGuardInput, niche: Dict[str, Any]) -> NicheGuardVerdict:
        """Deterministically evaluate text against active niche rules with context-aware semantic analysis."""
        thresholds = self.rules.get("thresholds", {})
        weights = self.rules.get("weights", {})
        behavior = self.rules.get("behavior", {})

        min_pass_score = float(thresholds.get("min_pass_score", 55.0))
        neg_penalty = float(thresholds.get("negative_keyword_penalty", 25.0))
        adjacent_penalty = float(thresholds.get("adjacent_penalty", 10.0))
        missing_must_have_pen = float(thresholds.get("missing_must_have_penalty", 15.0))
        ambiguous_margin = float(thresholds.get("ambiguous_margin", 8.0))

        instant_block_blocked = behavior.get("instant_block_on_blocked_topic", True)
        require_allowed_or_pillar = behavior.get("require_allowed_or_pillar", True)

        policy_version = int(niche.get("policy_version") or 1)
        policy_fingerprint = niche.get("policy_fingerprint")

        # Build raw and normalized corpus
        raw_combined = f"{item.title} {item.text} {' '.join(item.tags)}".strip()
        corpus = self._normalize_text(raw_combined)

        factors: List[NicheGuardFactor] = []
        raw_score = 0.0
        requires_review = False
        review_reasons: List[str] = []

        # 1. Blocked Topics Check (with contextual critique / negation handling)
        blocked_topics = niche.get("blocked_topics", [])
        hard_blocked_detected: List[str] = []
        critique_exceptions_detected: List[str] = []

        for bt in blocked_topics:
            if self._match_term(bt, corpus):
                is_critique, critique_reason = self._is_contextual_critique_or_negation(
                    term=bt, corpus=corpus, raw_text=raw_combined, niche=niche
                )
                if is_critique:
                    critique_exceptions_detected.append(bt)
                    requires_review = True
                    review_reasons.append(
                        f"Educational discussion/debunking of blocked topic '{bt}': {critique_reason}"
                    )
                    factors.append(NicheGuardFactor(
                        criterion="contextual_critique_exception",
                        points=0.0,
                        detail=f"Sensitive topic '{bt}' detected in educational critique or quotation context. Flagged for review rather than blocked.",
                        matched_items=[bt],
                    ))
                else:
                    hard_blocked_detected.append(bt)

        # If unmitigated hard-blocked topic is detected, instant reject
        if hard_blocked_detected and instant_block_blocked:
            verdict_id = f"ngv-{uuid.uuid4().hex[:12]}"
            factors.append(NicheGuardFactor(
                criterion="blocked_topics",
                points=-100.0,
                detail=f"Content matched strictly blocked topic(s): {', '.join(hard_blocked_detected)}",
                matched_items=hard_blocked_detected,
            ))
            verdict = NicheGuardVerdict(
                id=verdict_id,
                input_id=item.id,
                passed=False,
                score=0.0,
                reason=f"Rejected: strictly blocked topic detected [{', '.join(hard_blocked_detected)}].",
                classification="blocked",
                requires_review=False,
                review_reasons=[],
                primary_pillar=None,
                is_adjacent=False,
                is_blocked=True,
                audience_relevance=0.0,
                policy_version=policy_version,
                policy_fingerprint=policy_fingerprint,
                blocked_topics_detected=hard_blocked_detected,
                factors=factors,
                audience_value_breakdown={
                    "topic_relevance": 0.0,
                    "audience_fit": 0.0,
                    "problem_relevance": 0.0,
                    "practical_value": 0.0,
                    "evidence_potential": 0.0,
                },
                platform_warning_metadata={
                    "blocked_policy_alert": f"Blocked topic violation: {', '.join(hard_blocked_detected)}",
                    "action_required": "Editorial rejection: off-limits commercial, financial, or unverified claims.",
                },
            )
            self._execution_history[verdict.id] = verdict
            return verdict

        # 2. Content Pillars Matching (using pillar name, keywords, and synonyms)
        pillars = niche.get("content_pillars", [])
        matched_pillars: List[str] = []
        pillar_match_max = float(weights.get("pillar_match_max", 35.0))
        pillar_unit_weight = float(weights.get("pillar_unit_weight", 20.0))

        for p in pillars:
            p_name = p.get("name") if isinstance(p, dict) else str(p)
            matched = False

            if self._match_term(p_name, corpus):
                matched = True

            if not matched and isinstance(p, dict):
                # Check dedicated pillar keywords
                keywords = p.get("keywords", [])
                for kw in keywords:
                    if self._match_term(kw, corpus):
                        matched = True
                        break

            if not matched and isinstance(p, dict):
                # Check synonyms
                synonyms = p.get("synonyms", [])
                for syn in synonyms:
                    if self._match_term(syn, corpus):
                        matched = True
                        break

            if not matched:
                # Tokenize pillar name into meaningful words (length > 3)
                name_words = [w.lower() for w in re.findall(r"\b\w+\b", p_name) if len(w) > 3]
                if name_words:
                    matched_words = sum(1 for nw in name_words if self._match_term(nw, corpus))
                    if matched_words >= 2 or (len(name_words) == 1 and matched_words == 1):
                        matched = True

            if matched:
                matched_pillars.append(p_name)

        pillar_points = min(pillar_match_max, len(matched_pillars) * pillar_unit_weight)
        if pillar_points > 0:
            raw_score += pillar_points
            factors.append(NicheGuardFactor(
                criterion="content_pillars",
                points=pillar_points,
                detail=f"Matched {len(matched_pillars)} content pillar(s): {', '.join(matched_pillars)}",
                matched_items=matched_pillars,
            ))

        # 3. Allowed Topics Matching
        allowed_topics = niche.get("allowed_topics", [])
        matched_allowed: List[str] = []
        allowed_max = float(weights.get("allowed_topic_max", 40.0))
        allowed_unit = float(weights.get("allowed_topic_unit_weight", 15.0))

        for topic in allowed_topics:
            if self._match_term(topic, corpus):
                matched_allowed.append(topic)

        allowed_points = min(allowed_max, len(matched_allowed) * allowed_unit)
        if allowed_points > 0:
            raw_score += allowed_points
            factors.append(NicheGuardFactor(
                criterion="allowed_topics",
                points=allowed_points,
                detail=f"Matched {len(matched_allowed)} allowed topic(s): {', '.join(matched_allowed)}",
                matched_items=matched_allowed,
            ))

        # 4. Adjacent Topics Check
        adjacent_topics = niche.get("adjacent_topics", [])
        matched_adjacent: List[str] = []
        for adj in adjacent_topics:
            if self._match_term(adj, corpus):
                matched_adjacent.append(adj)

        if matched_adjacent:
            if len(matched_allowed) == 0 and len(matched_pillars) == 0:
                # Relevant adjacent topic without core: allow contextual pass with creator review
                adj_points = min(20.0, len(matched_adjacent) * 10.0)
                adj_score_contribution = 45.0 + adj_points - adjacent_penalty
                raw_score += adj_score_contribution
                factors.append(NicheGuardFactor(
                    criterion="relevant_adjacent_topics",
                    points=adj_score_contribution,
                    detail=f"Relevant adjacent topic(s) [{', '.join(matched_adjacent)}] recognized for contextual coverage (-{adjacent_penalty} adjacent penalty).",
                    matched_items=matched_adjacent,
                ))
                requires_review = True
                review_reasons.append(f"Relevant adjacent topic ({', '.join(matched_adjacent)}) requires creator review.")
            else:
                factors.append(NicheGuardFactor(
                    criterion="adjacent_topics_context",
                    points=5.0,
                    detail=f"Matched adjacent context: {', '.join(matched_adjacent)}",
                    matched_items=matched_adjacent,
                ))
                raw_score += 5.0

        # Educational Critique Bonus (if debunking/critique of blocked or negative claims was detected)
        if critique_exceptions_detected:
            critique_bonus = 25.0
            raw_score += critique_bonus
            factors.append(NicheGuardFactor(
                criterion="educational_critique_bonus",
                points=critique_bonus,
                detail=f"Educational debunking/critique credit for analyzing claims: {', '.join(critique_exceptions_detected)}",
                matched_items=critique_exceptions_detected,
            ))

        # 5. Must-Have Signals (reproducibility & evidence)
        must_haves = niche.get("must_have_signals", [])
        matched_must_haves: List[str] = []
        must_have_max = float(weights.get("must_have_signal_max", 15.0))
        must_have_unit = float(weights.get("must_have_unit_weight", 8.0))

        for mh in must_haves:
            if self._match_term(mh, corpus):
                matched_must_haves.append(mh)

        if matched_must_haves:
            mh_points = min(must_have_max, len(matched_must_haves) * must_have_unit)
            raw_score += mh_points
            factors.append(NicheGuardFactor(
                criterion="must_have_signals",
                points=mh_points,
                detail=f"Validated {len(matched_must_haves)} must-have signal(s): {', '.join(matched_must_haves)}",
                matched_items=matched_must_haves,
            ))
        elif must_haves and (len(matched_allowed) > 0 or len(matched_pillars) > 0) and not matched_adjacent:
            raw_score -= missing_must_have_pen
            factors.append(NicheGuardFactor(
                criterion="missing_must_have_signals",
                points=-missing_must_have_pen,
                detail=f"Missing required verifiable signals (-{missing_must_have_pen})",
                matched_items=[],
            ))

        # 6. Primary Problems & Audience Needs
        problems = niche.get("primary_problems", [])
        matched_problems: List[str] = []
        problem_max = float(weights.get("primary_problem_max", 10.0))
        problem_unit = float(weights.get("primary_problem_unit_weight", 5.0))

        for prob in problems:
            prob_keywords = [w for w in prob.split() if len(w) > 4]
            for kw in prob_keywords:
                if self._match_term(kw, corpus):
                    matched_problems.append(kw)
                    break

        if matched_problems:
            prob_points = min(problem_max, len(matched_problems) * problem_unit)
            raw_score += prob_points
            factors.append(NicheGuardFactor(
                criterion="audience_problems",
                points=prob_points,
                detail=f"Addressed audience problem keywords: {', '.join(set(matched_problems))}",
                matched_items=list(set(matched_problems)),
            ))

        # 7. Negative Keywords (with critique/negation exception handling)
        neg_keywords = niche.get("negative_keywords", [])
        matched_neg: List[str] = []
        for nk in neg_keywords:
            if self._match_term(nk, corpus):
                is_critique, critique_reason = self._is_contextual_critique_or_negation(
                    term=nk, corpus=corpus, raw_text=raw_combined, niche=niche
                )
                if is_critique:
                    factors.append(NicheGuardFactor(
                        criterion="negative_keyword_critique_exception",
                        points=0.0,
                        detail=f"Negative keyword '{nk}' detected in critique context: {critique_reason}",
                        matched_items=[nk],
                    ))
                    requires_review = True
                    review_reasons.append(f"Negative keyword '{nk}' used in critical discussion.")
                else:
                    matched_neg.append(nk)

        if matched_neg:
            total_neg_penalty = len(matched_neg) * neg_penalty
            raw_score -= total_neg_penalty
            factors.append(NicheGuardFactor(
                criterion="negative_keywords",
                points=-total_neg_penalty,
                detail=f"Matched negative keyword(s): {', '.join(matched_neg)} (-{total_neg_penalty} points)",
                matched_items=matched_neg,
            ))

        # 8. Audience Fit & Practical Value Scoring
        target_audience_desc = niche.get("audience") or ""
        audience_words = [w.lower() for w in re.findall(r"\b\w+\b", target_audience_desc) if len(w) > 4]
        matched_aud_words = [w for w in audience_words if w in corpus]
        aud_skill_levels = niche.get("target_skill_levels") or []
        has_skill_match = any(sl.lower() in corpus for sl in aud_skill_levels)

        if matched_allowed or matched_pillars or matched_adjacent:
            aud_points = min(15.0, round(len(matched_aud_words) * 5.0 + (5.0 if has_skill_match else 0.0), 1))
            if aud_points > 0:
                raw_score += aud_points
                factors.append(NicheGuardFactor(
                    criterion="audience_fit",
                    points=aud_points,
                    detail=f"Audience persona alignment: {', '.join(matched_aud_words[:3])}",
                    matched_items=matched_aud_words[:3],
                ))

            practical_signals = {
                "recipe", "workflow", "tutorial", "code", "setup", "guide", "benchmark",
                "benchmarks", "benchmarking", "teardown", "tools", "script", "config",
                "architecture", "design", "indexing", "strategies", "evaluating", "optimization",
                "monitoring", "hardened", "implementation", "repo", "repository", "docker",
                "pipeline", "comparison", "analysis", "audit", "security", "dissection", "tests",
            }
            practical_matches = sum(1 for ps in practical_signals if ps in corpus)
            prac_points = min(10.0, round(practical_matches * 5.0, 1))
            if prac_points > 0:
                raw_score += prac_points
                factors.append(NicheGuardFactor(
                    criterion="practical_value",
                    points=prac_points,
                    detail="Practical technical or workflow implementation indicators present.",
                    matched_items=[ps for ps in practical_signals if ps in corpus][:3],
                ))

        # Collect all positive niche terms across allowed, adjacent, pillars, and must-haves
        all_positive_terms: List[str] = list(allowed_topics) + list(adjacent_topics) + list(must_haves)
        for p in pillars:
            p_name = p.get("name") if isinstance(p, dict) else str(p)
            all_positive_terms.append(p_name)
            if isinstance(p, dict):
                all_positive_terms.extend(p.get("keywords", []))
                all_positive_terms.extend(p.get("synonyms", []))

        # Build niche domain vocabulary
        stopwords = {
            "and", "the", "for", "with", "from", "that", "this", "these", "into", "over",
            "under", "about", "your", "their", "when", "where", "what", "which", "more",
            "most", "than", "have", "been", "will", "does", "only", "also", "some", "such"
        }
        niche_vocab_text = " ".join(
            [niche.get("name") or "", niche.get("one_sentence_definition") or "", niche.get("audience") or ""]
            + allowed_topics + adjacent_topics + must_haves + (niche.get("audience_goals") or []) + (niche.get("primary_problems") or [])
        )
        for p in pillars:
            if isinstance(p, dict):
                niche_vocab_text += " " + " ".join([p.get("name", "")] + p.get("keywords", []) + p.get("synonyms", []))
        domain_vocab = {
            w.lower() for w in re.findall(r"\b\w+\b", niche_vocab_text) if len(w) > 2 and w.lower() not in stopwords
        }
        # Add technical domain abbreviations and multilingual tokens
        domain_vocab.update({
            "ai", "llm", "llms", "rag", "ast", "pr", "git", "repo", "eval", "evals",
            "swe", "claude", "qwen", "cursor", "windsurf", "deepseek", "docker", "repl",
            "qlora", "sql", "coder", "coders", "neovim", "ollama", "vllm", "কোডিং",
            "এজেন্ট", "বেঞ্চমার্ক", "মডেল", "রিভিউ", "টুল", "টুলস"
        })

        # 9. Quality Defect Detection: Tag Stuffing, Keyword Stuffing, Title/Body Mismatch
        title_body_corpus = self._normalize_text(f"{item.title} {item.text}")
        title_corpus = self._normalize_text(item.title)
        body_corpus = self._normalize_text(item.text)

        # Check Tag Stuffing:
        # Tag stuffing occurs when niche terms appear ONLY in metadata tags,
        # while title and body contain ZERO niche topics, content pillars, must-have signals, or domain vocabulary.
        if item.tags:
            has_multi_word = any(
                self._match_term(term, title_body_corpus) for term in all_positive_terms
            )
            tb_words = set(re.findall(r"\b\w+\b", title_body_corpus))
            has_domain_vocab = bool(tb_words.intersection(domain_vocab))

            if not has_multi_word and not has_domain_vocab and not critique_exceptions_detected:
                raw_score = 10.0
                factors.append(NicheGuardFactor(
                    criterion="tag_stuffing",
                    points=-50.0,
                    detail="Tag stuffing detected: niche keywords present only in tags while title and body text are unrelated.",
                    matched_items=item.tags,
                ))

        # Check Keyword Stuffing: very low unique word ratio in text
        corpus_words = [w for w in corpus.split() if len(w) > 2]
        if len(corpus_words) >= 12:
            unique_ratio = len(set(corpus_words)) / len(corpus_words)
            if unique_ratio < 0.35:
                raw_score = min(raw_score, 30.0)
                factors.append(NicheGuardFactor(
                    criterion="keyword_stuffing",
                    points=-30.0,
                    detail=f"Repetitive keyword stuffing detected (unique word ratio {unique_ratio:.2f}).",
                    matched_items=list(set(corpus_words))[:5],
                ))

        # Check Title / Body Mismatch (Clickbait Detection)
        body_words = [w for w in body_corpus.split() if len(w) > 3]
        if len(body_words) >= 15:
            title_has_niche = any(
                self._match_term(term, title_corpus) for term in allowed_topics + [p.get("name") if isinstance(p, dict) else str(p) for p in pillars]
            )
            body_has_niche = any(
                self._match_term(term, body_corpus) for term in all_positive_terms + matched_problems
            )
            if title_has_niche and not body_has_niche and not critique_exceptions_detected:
                raw_score = min(raw_score, 25.0)
                factors.append(NicheGuardFactor(
                    criterion="title_body_mismatch",
                    points=-25.0,
                    detail="Title contains niche keyword but body text is completely unrelated to niche.",
                    matched_items=[],
                ))

        final_score = max(0.0, min(100.0, round(raw_score, 1)))

        # Determine pass/fail & classification
        passed = True
        reasons: List[str] = []

        is_adjacent_only = bool(matched_adjacent and not matched_allowed and not matched_pillars)

        if require_allowed_or_pillar and len(matched_allowed) == 0 and len(matched_pillars) == 0:
            if is_adjacent_only:
                if final_score >= min_pass_score:
                    passed = True
                else:
                    passed = False
                    reasons.append("Adjacent topic relevance below cutoff")
            else:
                passed = False
                reasons.append("Does not match any defined content pillars or core allowed topics")

        if final_score < min_pass_score:
            passed = False
            reasons.append(f"Score {final_score} is below cutoff {min_pass_score}")

        # Classification Categorization
        if is_adjacent_only:
            classification = "adjacent"
        elif len(matched_allowed) > 0 or len(matched_pillars) > 0:
            if passed:
                classification = "core_niche"
            else:
                classification = "ambiguous"
        else:
            classification = "off_niche"

        # Check for ambiguity margin
        if passed and abs(final_score - min_pass_score) <= ambiguous_margin:
            requires_review = True
            review_reasons.append(
                f"Borderline score ({final_score}/100) within {ambiguous_margin} points of cutoff."
            )
            classification = "ambiguous"

        if critique_exceptions_detected:
            requires_review = True
            classification = "ambiguous"
            passed = True

        # Audience Value Dimensions Assessment (0.0 to 100.0)
        target_audience_desc = niche.get("audience") or ""
        audience_words = [w.lower() for w in re.findall(r"\b\w+\b", target_audience_desc) if len(w) > 4]
        matched_aud_words = [w for w in audience_words if w in corpus]

        # 1. Topic Relevance
        topic_relevance = min(100.0, round((len(matched_pillars) * 35.0) + (len(matched_allowed) * 25.0) + (len(matched_adjacent) * 15.0), 1))

        # 2. Audience Fit
        aud_skill_levels = niche.get("target_skill_levels") or []
        skill_matches = sum(1 for sl in aud_skill_levels if any(w in corpus for w in sl.lower().split() if len(w) > 4))
        base_aud = 50.0 if passed else 20.0
        audience_fit = min(100.0, round(base_aud + (len(matched_aud_words) * 15.0) + (skill_matches * 15.0), 1))

        # 3. Problem Relevance
        problem_relevance = min(100.0, round(len(matched_problems) * 30.0, 1))

        # 4. Practical Value
        practical_signals = {"recipe", "workflow", "tutorial", "code", "setup", "guide", "benchmark", "teardown", "tools", "script", "config"}
        practical_matches = sum(1 for ps in practical_signals if ps in corpus)
        practical_value = min(100.0, round(30.0 + (practical_matches * 15.0), 1))

        # 5. Evidence Potential
        evidence_signals = {"benchmark", "data", "paper", "github", "repo", "test", "experiment", "latency", "measurement"}
        evidence_matches = sum(1 for es in evidence_signals if es in corpus)
        evidence_potential = min(100.0, round(20.0 + (evidence_matches * 15.0) + (len(matched_must_haves) * 20.0), 1))

        audience_value_breakdown = {
            "topic_relevance": topic_relevance,
            "audience_fit": audience_fit,
            "problem_relevance": problem_relevance,
            "practical_value": practical_value,
            "evidence_potential": evidence_potential,
        }

        # Overall audience relevance composite
        aud_rel_score = round(
            (audience_fit * 0.4) + (problem_relevance * 0.3) + (practical_value * 0.3), 1
        )

        factors.append(NicheGuardFactor(
            criterion="audience_relevance",
            points=round(aud_rel_score * 0.1, 1),
            detail=f"Audience relevance evaluated at {aud_rel_score}% based on persona target keywords, problems, and practical value.",
            matched_items=matched_aud_words,
        ))

        # Platform Advisory Guidance
        platform_advisories: Dict[str, Any] = {}
        if any(w in corpus for w in ["ai generated", "synthetic", "cloned voice", "deepfake"]):
            platform_advisories["synthetic_disclosure"] = "YouTube/Meta/TikTok guidance: Verify synthetic content labels if using realistic generated scenes."
        if any(w in corpus for w in ["sponsor", "affiliate", "partner", "discount"]):
            platform_advisories["commercial_disclosure"] = "Ensure proper commercial and sponsorship disclosures on publishing platform."
        if len(matched_neg) > 0 or "secret" in corpus:
            platform_advisories["repetition_risk"] = "Low-value pattern warning: verify original evidence to prevent duplicate or repetitive content."

        # Summary Reason Construction
        if passed:
            if is_adjacent_only:
                summary_reason = (
                    f"Approved (Adjacent Topic): Score {final_score}/100 meets requirements "
                    f"({', '.join(matched_adjacent)}). Incurs adjacent topic penalty."
                )
            elif requires_review:
                summary_reason = (
                    f"Conditional Pass (Review Recommended): Score {final_score}/100. "
                    f"Requires human check: {'; '.join(review_reasons)}."
                )
            else:
                summary_reason = (
                    f"Approved: Relevance score {final_score}/100 meets requirements "
                    f"({len(matched_pillars)} pillar(s), {len(matched_allowed)} topic(s))."
                )
        else:
            summary_reason = f"Rejected: {'; '.join(reasons)}."

        verdict_id = f"ngv-{uuid.uuid4().hex[:12]}"
        verdict = NicheGuardVerdict(
            id=verdict_id,
            input_id=item.id,
            passed=passed,
            score=final_score,
            reason=summary_reason,
            classification=classification,
            requires_review=requires_review,
            review_reasons=review_reasons,
            primary_pillar=matched_pillars[0] if matched_pillars else None,
            is_adjacent=is_adjacent_only,
            is_blocked=False,
            audience_relevance=aud_rel_score,
            policy_version=policy_version,
            policy_fingerprint=policy_fingerprint,
            pillar_matches=matched_pillars,
            matched_allowed_topics=matched_allowed,
            matched_adjacent_topics=matched_adjacent,
            matched_must_have_signals=matched_must_haves,
            matched_negative_keywords=matched_neg,
            blocked_topics_detected=[],
            factors=factors,
            audience_value_breakdown=audience_value_breakdown,
            platform_warning_metadata=platform_advisories,
        )
        self._execution_history[verdict.id] = verdict
        return verdict

    async def run(self, context: EngineContext) -> EngineResult:
        start_time = datetime.now(timezone.utc)
        t0 = time.perf_counter()

        niche_override = context.parameters.get("niche_profile")
        # In run context, use configured profile or explicit override
        niche = await self._get_active_niche_data(niche_override, allow_fallback=False)

        raw_inputs = []
        if "input" in context.parameters:
            raw_inputs.append(context.parameters["input"])
        elif "items" in context.parameters:
            raw_inputs.extend(context.parameters["items"])
        elif "candidates" in context.parameters:
            raw_inputs.extend(context.parameters["candidates"])

        if not raw_inputs:
            duration_ms = int((time.perf_counter() - t0) * 1000)
            return EngineResult(
                engine_id=self.id,
                engine_version=self.version,
                run_id=context.run_id,
                success=True,
                started_at=start_time,
                ended_at=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                input_count=0,
                output_count=0,
                rejected_count=0,
                error_count=0,
                cost=0.0,
                summary="No input items provided to Niche Guard runner.",
                outputs=[],
                explanations=[],
            )

        verdicts: List[NicheGuardVerdict] = []
        rejected_count = 0
        explanations: List[Dict[str, Any]] = []

        for raw in raw_inputs:
            item = NicheGuardInput(**raw) if isinstance(raw, dict) else raw
            verdict = self.evaluate_item(item, niche)
            verdicts.append(verdict)
            if not verdict.passed:
                rejected_count += 1

            explanations.append({
                "verdict_id": verdict.id,
                "input_id": verdict.input_id,
                "passed": verdict.passed,
                "score": verdict.score,
                "classification": verdict.classification,
                "requires_review": verdict.requires_review,
                "reason": verdict.reason,
                "blocked": verdict.blocked_topics_detected,
                "pillars": verdict.pillar_matches,
                "allowed": verdict.matched_allowed_topics,
            })

        duration_ms = int((time.perf_counter() - t0) * 1000)
        end_time = datetime.now(timezone.utc)
        passed_count = len(verdicts) - rejected_count

        return EngineResult(
            engine_id=self.id,
            engine_version=self.version,
            run_id=context.run_id,
            success=True,
            started_at=start_time,
            ended_at=end_time,
            duration_ms=duration_ms,
            input_count=len(verdicts),
            output_count=passed_count,
            rejected_count=rejected_count,
            error_count=0,
            cost=0.0,
            summary=f"Niche Guard evaluated {len(verdicts)} item(s): {passed_count} passed, {rejected_count} rejected.",
            outputs=[v.model_dump() for v in verdicts],
            explanations=explanations,
        )

    async def dry_run(self, context: EngineContext) -> EngineResult:
        context.dry_run = True
        result = await self.run(context)
        result.summary = f"[DRY RUN] {result.summary}"
        return result

    def explain(self, result_id: str) -> EngineExplanation:
        verdict = self._execution_history.get(result_id)
        if not verdict:
            return EngineExplanation(
                result_id=result_id,
                summary=f"No execution history found for verdict '{result_id}'.",
                factors=[],
            )

        factors_data = [f.model_dump() for f in verdict.factors]
        status_text = "PASSED" if verdict.passed else "REJECTED"
        return EngineExplanation(
            result_id=result_id,
            summary=f"Verdict {result_id} {status_text} with score {verdict.score}/100. {verdict.reason}",
            factors=factors_data,
        )
