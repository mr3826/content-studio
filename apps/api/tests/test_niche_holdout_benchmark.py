"""Independent Holdout Benchmark Suite for Niche Foundation V1.02.
This suite was NOT used to tune algorithm weights or keyword dictionaries.
It tests:
1. A completely non-technical legitimate niche profile ("Artisan Sourdough & Fermentation Studio").
2. Distant negations (negation in separate clause/sentence from sensitive claim).
3. Quotation endorsement vs quotation empirical skepticism.
4. Long-form text with mixed topics.
5. Bengali non-technical and technical content.
6. Tag stuffing and title/body mismatch on non-technical profiles.
7. Unconfigured and empty policy profiles.
8. Full confusion matrix and performance statistics generation.
"""

from typing import Any, Dict, List, NamedTuple
import pytest

from app.engines.niche_guard.contracts import NicheGuardInput
from app.engines.niche_guard.engine import NicheGuardEngine


class HoldoutTestCase(NamedTuple):
    id: str
    niche_type: str  # "sourdough" or "ai_systems"
    title: str
    text: str
    tags: List[str]
    expected_classification: str  # "core_niche", "adjacent", "ambiguous", "off_niche", "blocked"
    expected_passed: bool
    expected_requires_review: bool
    notes: str


# Profile 1: Non-technical "Artisan Sourdough & Fermentation Studio"
SOURDOUGH_NICHE: Dict[str, Any] = {
    "name": "Artisan Sourdough & Fermentation Studio",
    "one_sentence_definition": "Empirical bread science, wild yeast fermentation, and rustic hearth baking.",
    "audience": "Home bakers and artisan culinary enthusiasts looking for dependable fermentation science.",
    "target_skill_levels": ["Intermediate Baker", "Advanced Artisan"],
    "allowed_topics": [
        "wild yeast starter",
        "dough hydration",
        "long cold proofing",
        "dutch oven crumb",
        "lactic acid bacteria fermentation",
        "baking temperature curves",
    ],
    "adjacent_topics": [
        "home flour milling",
        "ancient grain nutrition",
        "baking steel heat transfer",
    ],
    "blocked_topics": [
        "commercial fast-rise packet yeast",
        "microwave bread hacks",
        "guaranteed 5-minute sourdough",
    ],
    "topic_exceptions": [
        {
            "topic_or_keyword": "commercial fast-rise packet yeast",
            "allowed_contexts": ["debunk", "comparison", "testing claims", "criticism"],
            "reason": "Educational comparison comparing wild yeast fermentation rates against commercial yeast.",
        }
    ],
    "must_have_signals": ["fermentation time", "hydration percentage", "baking temperature"],
    "negative_keywords": ["instant miracle bread", "lazy keto bread", "secret chemical additive"],
    "content_pillars": [
        {
            "id": "starter_science",
            "name": "Wild Yeast Microbiome",
            "keywords": ["starter maintenance", "wild yeast", "acidification", "microbiome"],
            "synonyms": ["sourdough starter care"],
        },
        {
            "id": "dough_mechanics",
            "name": "Gluten & Hydration Mechanics",
            "keywords": ["autolyse", "bulk fermentation", "dough hydration", "gluten network"],
            "synonyms": ["dough handling techniques"],
        },
        {
            "id": "hearth_baking",
            "name": "Hearth & Dutch Oven Baking",
            "keywords": ["steam injection", "dutch oven crumb", "oven spring", "scoring angle"],
            "synonyms": ["artisan crust development"],
        },
    ],
    "primary_problems": [
        "Overproofing causing dense flat loaves during summer months.",
        "Underdeveloped gluten structure when using high hydration flours.",
        "Pale crust and poor oven spring in standard home kitchen ovens.",
    ],
    "policy_version": 1,
    "policy_fingerprint": "fp_sourdough_holdout_v1",
}

# Profile 2: Technical "AI Systems & Coding Automation"
AI_SYSTEMS_NICHE: Dict[str, Any] = {
    "name": "Local AI Systems & Developer Tooling",
    "one_sentence_definition": "Deterministic evaluations of local LLMs and autonomous coding agent workflows.",
    "audience": "Staff engineers, system architects, and technical lead builders.",
    "target_skill_levels": ["Senior Engineer", "Staff Architect"],
    "allowed_topics": [
        "coding agents",
        "local llms",
        "benchmarking agents",
        "ast static analysis",
        "local model quantization",
    ],
    "adjacent_topics": [
        "devops containerization",
        "database indexing",
        "terminal editors",
    ],
    "blocked_topics": [
        "guaranteed passive income",
        "crypto trading bots",
        "get rich quick with ai",
    ],
    "topic_exceptions": [
        {
            "topic_or_keyword": "crypto trading bots",
            "allowed_contexts": ["debunk", "investigating", "testing claims"],
            "reason": "Exposing vulnerabilities in trading scripts.",
        }
    ],
    "must_have_signals": ["code repository", "reproducible benchmark"],
    "negative_keywords": ["100x money", "passive income", "automated wealth"],
    "content_pillars": [
        {
            "id": "benchmarks",
            "name": "Coding Agent Stress Tests",
            "keywords": ["agent eval", "coding benchmark", "swe-bench"],
            "synonyms": ["coding agent evals"],
        },
        {
            "id": "local_models",
            "name": "Local Model Pipelines",
            "keywords": ["ollama", "vllm", "quantization", "local llm"],
            "synonyms": ["local inference"],
        },
    ],
    "primary_problems": [
        "LLMs producing hallucinated code without runtime verification.",
        "High GPU latency and memory consumption for local models.",
    ],
    "policy_version": 2,
    "policy_fingerprint": "fp_ai_systems_holdout_v2",
}


HOLDOUT_CASES: List[HoldoutTestCase] = [
    # --- Non-Technical Niche: Sourdough Baking ---
    HoldoutTestCase(
        id="sd-01",
        niche_type="sourdough",
        title="Optimizing Tartine-Style 80% Dough Hydration",
        text="A step-by-step experiment testing autolyse duration, bulk fermentation rise, and gluten structure with 80% dough hydration.",
        tags=["hydration percentage", "bulk fermentation"],
        expected_classification="core_niche",
        expected_passed=True,
        expected_requires_review=False,
        notes="Clean core sourdough topic matching pillar and allowed topics.",
    ),
    HoldoutTestCase(
        id="sd-02",
        niche_type="sourdough",
        title="Why You Should Consider Home Flour Milling for Whole Grain Loaves",
        text="An overview of stone mills, bran sifting techniques, and flour milling impact on dough hydration and fermentation rate.",
        tags=["home flour milling"],
        expected_classification="adjacent",
        expected_passed=True,
        expected_requires_review=True,
        notes="Adjacent topic (flour milling) without core bread terms; requires creator review.",
    ),
    HoldoutTestCase(
        id="sd-03",
        niche_type="sourdough",
        title="How to Build High-Yield Crypto Staking Validators on Cloud VPS",
        text="Deploying proof-of-stake blockchain nodes with docker containers and liquid staking yields.",
        tags=["crypto", "validators"],
        expected_classification="off_niche",
        expected_passed=False,
        expected_requires_review=False,
        notes="Completely off-niche topic for bread baking studio.",
    ),
    HoldoutTestCase(
        id="sd-04",
        niche_type="sourdough",
        title="Guaranteed 5-Minute Sourdough Loaf Every Morning",
        text="Skip the fermentation and use this guaranteed 5-minute sourdough powder recipe for instant bakery results.",
        tags=["baking"],
        expected_classification="blocked",
        expected_passed=False,
        expected_requires_review=False,
        notes="Explicitly blocked topic (guaranteed 5-minute sourdough).",
    ),
    HoldoutTestCase(
        id="sd-05",
        niche_type="sourdough",
        title="Why Commercial Fast-Rise Packet Yeast Cannot Replicate Wild Sourdough Complexity",
        text="Debunking commercial bread claims: We measured organic acid profiles and proved commercial fast-rise packet yeast produces zero complex acetic acids.",
        tags=["fermentation time", "testing claims"],
        expected_classification="ambiguous",
        expected_passed=True,
        expected_requires_review=True,
        notes="Educational critique & debunking of blocked topic with explicit topic exception.",
    ),
    HoldoutTestCase(
        id="sd-06",
        niche_type="sourdough",
        title="সাওয়ারডো স্টার্টার বানানোর সঠিক নিয়ম ও ফারমেন্টেশন বিজ্ঞান",
        text="ঘরে বুনো ইস্ট বা ওয়াইল্ড ইস্ট দিয়ে কিভাবে পারফেক্ট সাওয়ারডো স্টার্টার তৈরি করবেন এবং সঠিক গ্লুটেন গঠন করবেন।",
        tags=["starter", "fermentation"],
        expected_classification="core_niche",
        expected_passed=True,
        expected_requires_review=False,
        notes="Bengali sourdough bread science matching wild yeast starter concepts.",
    ),
    HoldoutTestCase(
        id="sd-07",
        niche_type="sourdough",
        title="The Ultimate Guide to Kitchen Countertops and Granite Slabs",
        text="Comparing quartz, marble, and granite countertops for kitchen renovations with price breakdowns.",
        tags=["dough hydration", "wild yeast starter"],
        expected_classification="ambiguous",  # tag stuffing detected
        expected_passed=False,
        expected_requires_review=False,
        notes="Tag stuffing: niche tags appended to unrelated kitchen countertop article.",
    ),
    HoldoutTestCase(
        id="sd-08",
        niche_type="sourdough",
        title="Bread bread bread bread bread bread bread bread bread bread bread bread",
        text="bread bread bread bread bread bread bread bread bread bread bread bread sourdough sourdough sourdough sourdough",
        tags=["bread"],
        expected_classification="ambiguous",  # keyword stuffing detected
        expected_passed=False,
        expected_requires_review=False,
        notes="Keyword stuffing on sourdough profile with very low unique word ratio.",
    ),

    # --- Technical Niche: AI Systems & Coding Automation ---
    HoldoutTestCase(
        id="ai-01",
        niche_type="ai_systems",
        title="Benchmarking Coding Agents on Multi-File Refactoring Tasks",
        text="A rigorous benchmark of autonomous coding agents across 200 repository refactoring scenarios with reproducible benchmark scripts.",
        tags=["reproducible benchmark", "coding agents"],
        expected_classification="core_niche",
        expected_passed=True,
        expected_requires_review=False,
        notes="Core technical topic with must-have signals.",
    ),
    HoldoutTestCase(
        id="ai-02",
        niche_type="ai_systems",
        title="Why Database Indexing Strategy Matters for Large-Scale Vector Search",
        text="Exploring B-tree versus IVFFlat indexes in Postgres when storing millions of embedding records for agent memory retrieval.",
        tags=["database indexing"],
        expected_classification="adjacent",
        expected_passed=True,
        expected_requires_review=True,
        notes="Adjacent topic (database indexing) providing relevant systems context.",
    ),
    HoldoutTestCase(
        id="ai-03",
        niche_type="ai_systems",
        title="How to Make Artisan Sourdough Bread at Home",
        text="Mixing flour and water for wild yeast fermentation with dutch oven baking.",
        tags=["baking"],
        expected_classification="off_niche",
        expected_passed=False,
        expected_requires_review=False,
        notes="Completely off-niche topic for AI engineering studio.",
    ),
    HoldoutTestCase(
        id="ai-04",
        niche_type="ai_systems",
        title="Automated Crypto Trading Bots with Guaranteed Passive Income",
        text="Earn 10% daily yield using our automated crypto trading bots with zero risk guaranteed passive income algorithms.",
        tags=["crypto", "income"],
        expected_classification="blocked",
        expected_passed=False,
        expected_requires_review=False,
        notes="Strictly blocked promotional scam topic.",
    ),
    HoldoutTestCase(
        id="ai-05",
        niche_type="ai_systems",
        title="Testing Claims: Why Crypto Trading Bots Suffer Catastrophic Drawdowns",
        text="Investigating automated trading claims: We audited open source crypto trading bots and demonstrated why these algorithms fail and cannot produce stable returns.",
        tags=["testing claims", "reproducible benchmark"],
        expected_classification="ambiguous",
        expected_passed=True,
        expected_requires_review=True,
        notes="Educational critique investigating blocked topic; requires human review.",
    ),
    HoldoutTestCase(
        id="ai-06",
        niche_type="ai_systems",
        title="Our Rigorous 40-Run Study Does Not Prove That Coding Agents Eliminate Programmers",
        text="We evaluated autonomous tools on legacy codebases. The failure rates demonstrate that these tools do not prove autonomous coders are ready to replace developers.",
        tags=["reproducible benchmark", "coding agents"],
        expected_classification="ambiguous",  # negation & sensitive phrase
        expected_passed=True,
        expected_requires_review=True,
        notes="Distant negation across clauses; properly routed to human review.",
    ),
    HoldoutTestCase(
        id="ai-07",
        niche_type="ai_systems",
        title="The Vendor Claims 'Our Bot Generates Guaranteed Passive Income' and We Endorse It",
        text="We tested the bot and enthusiastically confirm that the vendor is correct in promising guaranteed passive income for all buyers.",
        tags=["ai", "income"],
        expected_classification="blocked",
        expected_passed=False,
        expected_requires_review=False,
        notes="Quotation endorsing a blocked claim without skepticism: strictly blocked.",
    ),
    HoldoutTestCase(
        id="ai-08",
        niche_type="ai_systems",
        title="The Vendor Claims 'Our Bot Generates Guaranteed Passive Income' but Our Audit Revealed Fraud",
        text="The vendor marketing claims 'our bot generates guaranteed passive income' but our code audit proved this is misleading and mathematically impossible.",
        tags=["audit", "reproducible benchmark"],
        expected_classification="ambiguous",
        expected_passed=True,
        expected_requires_review=True,
        notes="Quotation skeptically investigated with empirical skepticism: flagged for review.",
    ),
    HoldoutTestCase(
        id="ai-09",
        niche_type="ai_systems",
        title="কোডিং এজেন্ট বেঞ্চমার্কিং ও লোকাল এলএলএম পারফরম্যান্স টেস্ট",
        text="আমরা লোকাল মডেলে কোডিং এজেন্টের কার্যকারিতা এবং বেঞ্চমার্ক টেস্ট করে দেখেছি কিভাবে ডেভেলপারের সময় বাঁচে।",
        tags=["কোডিং", "বেঞ্চমার্ক"],
        expected_classification="core_niche",
        expected_passed=True,
        expected_requires_review=False,
        notes="Bengali AI systems evaluation matching core pillar and allowed vocabulary.",
    ),
    HoldoutTestCase(
        id="ai-10",
        niche_type="ai_systems",
        title="Building Resilient Coding Agents with Local LLM Quantization and Multi-Step Verification",
        text="""In modern software engineering, evaluating autonomous tools requires careful infrastructure planning.
        In this deep dive, we walk through configuring local LLMs with Ollama and 4-bit quantization.
        We establish deterministic testing loops where coding agents generate abstract syntax trees, execute local unit test suites,
        and inspect error logs before opening a pull request.
        Unlike superficial demo scripts, this architecture handles complex edge cases, network partitioning, and memory constraints.
        All measurement scripts and evaluation harnesses are available in the companion code repository.""",
        tags=["coding agents", "local llms", "reproducible benchmark"],
        expected_classification="core_niche",
        expected_passed=True,
        expected_requires_review=False,
        notes="Long-form mixed engineering text with rich technical vocabulary.",
    ),
    HoldoutTestCase(
        id="ai-11",
        niche_type="ai_systems",
        title="Top 10 Tourist Attractions to Visit in Paris This Summer",
        text="Visit the Eiffel Tower, the Louvre museum, and take a cruise down the Seine river with French wine tastings.",
        tags=["coding agents", "local llms", "developer tools"],
        expected_classification="ambiguous",  # tag stuffing
        expected_passed=False,
        expected_requires_review=False,
        notes="Tag stuffing on technical profile: tourist guide with AI tags.",
    ),
    HoldoutTestCase(
        id="ai-12",
        niche_type="ai_systems",
        title="Coding Agents Benchmark Architecture Guide",
        text="Today we talk about gardening. Tomatoes need plenty of sunshine and daily watering. Carrots prefer loose sandy soil.",
        tags=["coding agents"],
        expected_classification="ambiguous",  # clickbait title/body mismatch
        expected_passed=False,
        expected_requires_review=False,
        notes="Clickbait title/body mismatch: coding title with gardening body text.",
    ),
]


def test_independent_holdout_benchmark_execution():
    """Execute the independent holdout benchmark and generate a rigorous evaluation report."""
    engine = NicheGuardEngine()

    total_cases = len(HOLDOUT_CASES)
    correct_classifications = 0
    correct_pass_decisions = 0
    correct_review_flags = 0

    # Confusion matrix counters: true class vs predicted class
    classes = ["core_niche", "adjacent", "ambiguous", "off_niche", "blocked"]
    confusion_matrix = {c_true: {c_pred: 0 for c_pred in classes} for c_true in classes}

    false_positives = 0  # Off-niche or blocked predicted as pass without review
    false_negatives = 0  # Core niche predicted as blocked or rejected
    blocked_false_negatives = 0  # Blocked promotional content that passed

    for tc in HOLDOUT_CASES:
        niche = SOURDOUGH_NICHE if tc.niche_type == "sourdough" else AI_SYSTEMS_NICHE
        guard_input = NicheGuardInput(
            id=tc.id,
            title=tc.title,
            text=tc.text,
            tags=tc.tags,
        )

        verdict = engine.evaluate_item(guard_input, niche)

        # Record confusion matrix
        pred_class = verdict.classification
        if pred_class in classes and tc.expected_classification in classes:
            confusion_matrix[tc.expected_classification][pred_class] += 1

        # Accuracy checks
        if verdict.classification == tc.expected_classification:
            correct_classifications += 1

        if verdict.passed == tc.expected_passed:
            correct_pass_decisions += 1

        if verdict.requires_review == tc.expected_requires_review:
            correct_review_flags += 1

        # Error tracking
        if tc.expected_classification in ("off_niche", "blocked") and verdict.passed and not verdict.requires_review:
            false_positives += 1

        if tc.expected_classification == "core_niche" and not verdict.passed:
            false_negatives += 1

        if tc.expected_classification == "blocked" and verdict.passed and not verdict.requires_review:
            blocked_false_negatives += 1

    classification_accuracy = (correct_classifications / total_cases) * 100.0
    pass_decision_accuracy = (correct_pass_decisions / total_cases) * 100.0
    review_accuracy = (correct_review_flags / total_cases) * 100.0

    print("\n" + "=" * 75)
    print("        INDEPENDENT HOLDOUT BENCHMARK REPORT (V1.02 NICHE GUARD)")
    print("=" * 75)
    print(f"Total Holdout Test Cases:       {total_cases}")
    print(f"Classification Accuracy:        {classification_accuracy:.1f}% ({correct_classifications}/{total_cases})")
    print(f"Pass/Fail Decision Accuracy:    {pass_decision_accuracy:.1f}% ({correct_pass_decisions}/{total_cases})")
    print(f"Review Flag Accuracy:           {review_accuracy:.1f}% ({correct_review_flags}/{total_cases})")
    print(f"False Positives (Unchecked):    {false_positives}")
    print(f"False Negatives (Core Blocked): {false_negatives}")
    print(f"Blocked False Negatives:        {blocked_false_negatives}")
    print("\nPER-CLASS CONFUSION MATRIX (Rows: Ground Truth, Cols: Predicted):")
    header = f"{'True Class':<15}" + "".join(f"{c:>12}" for c in classes)
    print(header)
    print("-" * len(header))
    for c_true in classes:
        row = f"{c_true:<15}" + "".join(f"{confusion_matrix[c_true][c_pred]:>12}" for c_pred in classes)
        print(row)
    print("=" * 75 + "\n")

    # Print mismatch breakdown
    print("MISMATCHES / DETAILED CASE ANALYSIS:")
    for tc in HOLDOUT_CASES:
        niche = SOURDOUGH_NICHE if tc.niche_type == "sourdough" else AI_SYSTEMS_NICHE
        guard_input = NicheGuardInput(id=tc.id, title=tc.title, text=tc.text, tags=tc.tags)
        verdict = engine.evaluate_item(guard_input, niche)
        if (verdict.classification != tc.expected_classification or 
            verdict.passed != tc.expected_passed or 
            verdict.requires_review != tc.expected_requires_review):
            print(f"[{tc.id}] Expected: class={tc.expected_classification}, pass={tc.expected_passed}, rev={tc.expected_requires_review} | "
                  f"Got: class={verdict.classification}, pass={verdict.passed}, rev={verdict.requires_review} | Score: {verdict.score:.2f} | Reason: {verdict.reason}")

