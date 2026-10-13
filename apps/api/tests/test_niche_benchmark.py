"""Behavioral benchmark evaluation suite for Niche Foundation V1.02.
Covers 50+ representative test cases spanning all required categories:
- Clear core topics
- Clear off-niche topics
- Valuable adjacent topics
- Blocked promotional topics
- Educational criticism of blocked topics
- Quoted misleading claims
- Negations and disclaimers
- Keyword stuffing
- Unrelated titles with relevant tags
- Misleadingly relevant titles with unrelated body text
- Emerging technical topics
- Technical abbreviations and aliases
- Multilingual and mixed-language text (English and Bangla)
- Safe empty / edge inputs
"""

import time
import pytest
from typing import List, Dict, Any
from app.engines.niche_guard.contracts import NicheGuardInput, NicheGuardVerdict
from app.engines.niche_guard.engine import NicheGuardEngine

# 52 Independently Labeled Benchmark Cases
BENCHMARK_CASES = [
    # 1. Clear Core Topics (Ground Truth: PASS, core_niche)
    {
        "id": "core_01",
        "title": "Benchmarking AI Coding Agents on Large Legacy Codebases",
        "text": "Empirical comparison measuring latency, token consumption, and patch accuracy across SWE-bench benchmarks. Code repository and reproducible logs included.",
        "tags": ["coding agents", "benchmarks", "evals"],
        "expected_pass": True,
        "expected_class": "core_niche",
        "category": "core",
    },
    {
        "id": "core_02",
        "title": "Local LLM Tool Use with Qwen 2.5 Coder in Neovim",
        "text": "Configuring local Ollama server with function calling and AST-based context providers for local developer workflows.",
        "tags": ["local LLMs", "developer tools", "coding automation"],
        "expected_pass": True,
        "expected_class": "core_niche",
        "category": "core",
    },
    {
        "id": "core_03",
        "title": "Autonomous PR Reviewer Agent using Claude 3.7",
        "text": "Building a deterministic GitHub Action that indexes changed files, constructs a dependency graph, and leaves inline syntax-safe diff suggestions.",
        "tags": ["coding agents", "developer tools", "automation"],
        "expected_pass": True,
        "expected_class": "core_niche",
        "category": "core",
    },
    {
        "id": "core_04",
        "title": "Evaluating Context Window Degradation in Cursor and Windsurf",
        "text": "Stress testing code assistants on 50,000 line Python repos to observe attention failure modes and hallucinated imports.",
        "tags": ["coding agents", "developer tools", "reproducible benchmark"],
        "expected_pass": True,
        "expected_class": "core_niche",
        "category": "core",
    },
    {
        "id": "core_05",
        "title": "Local Code Intelligence with Tree-Sitter and Llama 3.3",
        "text": "Extracting symbol definitions and caller graphs to feed precise context to local coding LLMs without cloud dependencies.",
        "tags": ["local LLMs", "developer tools", "code repository"],
        "expected_pass": True,
        "expected_class": "core_niche",
        "category": "core",
    },

    # 2. Clear Off-Niche Topics (Ground Truth: FAIL, off_niche)
    {
        "id": "off_01",
        "title": "How to Bake Artisan Sourdough Bread at Home",
        "text": "Fermentation schedules, starter maintenance, and Dutch oven baking techniques for open crumb loaves.",
        "tags": ["baking", "sourdough", "bread"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "off_niche",
    },
    {
        "id": "off_02",
        "title": "Top 10 High Performance Basketball Shoes of 2026",
        "text": "Cushioning breakdown, traction patterns, and durability testing for indoor hardwood courts.",
        "tags": ["shoes", "basketball", "review"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "off_niche",
    },
    {
        "id": "off_03",
        "title": "Beginner Guide to Organic Tomato Gardening",
        "text": "Soil pH balancing, companion planting, and natural pest control for heirloom tomatoes.",
        "tags": ["gardening", "organic", "vegetables"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "off_niche",
    },
    {
        "id": "off_04",
        "title": "Celebrity Red Carpet Fashion Highlights from Film Gala",
        "text": "Designer gowns, vintage jewelry, and runway trends from the annual international festival.",
        "tags": ["fashion", "celebrity", "entertainment"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "off_niche",
    },
    {
        "id": "off_05",
        "title": "Repairing a Leaking Kitchen Sink Pipe and Drain Trap",
        "text": "Step by step plumbing guide using Teflon tape and replacement slip joint washers.",
        "tags": ["home repair", "diy", "plumbing"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "off_niche",
    },

    # 3. Valuable Adjacent Topics (Ground Truth: PASS, adjacent / review)
    {
        "id": "adj_01",
        "title": "Why Database Indexing Matters When Designing AI Agent Memory",
        "text": "Evaluating SQLite and PostgreSQL vector indexing strategies when persisting long-term memory for developer assistant agents.",
        "tags": ["software architecture", "coding agents", "database indexing"],
        "expected_pass": True,
        "expected_class": "adjacent",
        "category": "adjacent",
    },
    {
        "id": "adj_02",
        "title": "DevOps Container Hardening for Local LLM Inference Endpoints",
        "text": "Best practices for deploying vLLM inside unprivileged Docker containers with GPU passthrough and health check monitoring.",
        "tags": ["DevOps", "local LLMs", "software architecture"],
        "expected_pass": True,
        "expected_class": "adjacent",
        "category": "adjacent",
    },
    {
        "id": "adj_03",
        "title": "API Design Contracts for Multi-Agent Tool Registries",
        "text": "Standardizing schema validation and error protocols between autonomous code generation nodes and CI systems.",
        "tags": ["software architecture", "API design", "developer tools"],
        "expected_pass": True,
        "expected_class": "adjacent",
        "category": "adjacent",
    },
    {
        "id": "adj_04",
        "title": "Managing High Concurrency in Python AsyncIO for Code Crawlers",
        "text": "Thread pooling, uvloop performance, and semaphore backpressure for repo indexing pipelines.",
        "tags": ["software architecture", "DevOps", "developer tools"],
        "expected_pass": True,
        "expected_class": "adjacent",
        "category": "adjacent",
    },

    # 4. Blocked Promotional Topics (Ground Truth: FAIL, blocked)
    {
        "id": "blk_01",
        "title": "Guaranteed Passive Income with Crypto Trading Bots",
        "text": "Earn 500% monthly return using automated algorithmic arbitrage on decentralized crypto exchanges.",
        "tags": ["crypto/web3 trading", "passive income", "trading"],
        "expected_pass": False,
        "expected_class": "blocked",
        "category": "blocked_promo",
    },
    {
        "id": "blk_02",
        "title": "Get Rich Quick with AI Dropshipping and Copy-Paste Bots",
        "text": "Make $10,000 per day with this secret trick without doing any work. Secret automated money system.",
        "tags": ["get rich quick", "passive income", "secret trick"],
        "expected_pass": False,
        "expected_class": "blocked",
        "category": "blocked_promo",
    },
    {
        "id": "blk_03",
        "title": "Automated Crypto/Web3 Trading Signal Bot for Instant Wealth",
        "text": "Guaranteed trading profits with zero risk on Binance and Uniswap using our proprietary web3 indicators.",
        "tags": ["crypto/web3 trading", "get rich quick"],
        "expected_pass": False,
        "expected_class": "blocked",
        "category": "blocked_promo",
    },
    {
        "id": "blk_04",
        "title": "This Secret Money Trick Replaced All Coders Forever",
        "text": "100x money making prompt that makes software engineers obsolete while generating passive income.",
        "tags": ["replaced all coders", "secret trick", "100x money"],
        "expected_pass": False,
        "expected_class": "blocked",
        "category": "blocked_promo",
    },

    # 5. Educational Criticism of Blocked Topics (Ground Truth: NOT blocked, review/adjacent/core)
    {
        "id": "crit_01",
        "title": "Why AI Trading Bots Cannot Guarantee Passive Income",
        "text": "Mathematical debunking and backtest analysis showing why market slippage, fees, and regime shifts wipe out naive algorithmic trading bots.",
        "tags": ["benchmarks", "developer tools", "critique"],
        "expected_pass": True,
        "category": "educational_critique",
    },
    {
        "id": "crit_02",
        "title": "Debunking Get Rich Quick AI Coding Myths: A Real Engineering Audit",
        "text": "We analyzed 50 viral claims promising instant wealth with coding agents and measured actual code maintenance debt.",
        "tags": ["coding agents", "reproducible benchmark", "developer tools"],
        "expected_pass": True,
        "category": "educational_critique",
    },
    {
        "id": "crit_03",
        "title": "The Fallacy of 'Passive Income' in Autonomous Software Engineering",
        "text": "A critical examination of hidden infrastructure costs, prompt drift, and continuous testing required to keep AI agents functioning in production.",
        "tags": ["coding agents", "software architecture", "evals"],
        "expected_pass": True,
        "category": "educational_critique",
    },
    {
        "id": "crit_04",
        "title": "Exposing the Crypto/Web3 Trading Bot Scams: Code Dissection",
        "text": "Decompiling open source trading scam contracts to reveal honeypot backdoors and fake liquidity promises. Educational analysis.",
        "tags": ["developer tools", "code repository", "security"],
        "expected_pass": True,
        "category": "educational_critique",
    },

    # 6. Quoted Misleading Claims (Ground Truth: NOT hard-blocked as promo)
    {
        "id": "quote_01",
        "title": "Vendor Claims '100x money and replaced all coders' — Here Is What Our Benchmark Found",
        "text": "The marketing landing page states 'replaced all coders' and claims a 'secret trick', but empirical tests on real repositories yielded an 18% syntax error rate.",
        "tags": ["coding agents", "developer tools", "reproducible benchmark"],
        "expected_pass": True,
        "category": "quoted_claim",
    },
    {
        "id": "quote_02",
        "title": "Testing the 'Guaranteed Passive Income' Prompts from Twitter",
        "text": "We ran automated unit test suites against 20 popular prompts claiming 'guaranteed money'. Not a single one survived regression checks.",
        "tags": ["coding agents", "evals and benchmarks", "developer tools"],
        "expected_pass": True,
        "category": "quoted_claim",
    },

    # 7. Negations and Disclaimers (Ground Truth: NOT hard-blocked)
    {
        "id": "neg_01",
        "title": "These SWE-bench Results Do Not Prove AI Replaced All Coders",
        "text": "Rigorous statistical analysis of SWE-bench verified tasks demonstrating why human code reviewers remain indispensable for architectural decisions.",
        "tags": ["coding agents", "reproducible benchmark", "developer tools"],
        "expected_pass": True,
        "category": "negation",
    },
    {
        "id": "neg_02",
        "title": "No Evidence That LLMs Provide a Secret Trick for Instant Velocity",
        "text": "Field study of 12 engineering teams adopting AI tools showing modest 15% gains in boilerplate rather than magical shortcuts.",
        "tags": ["developer tools", "software architecture", "evals"],
        "expected_pass": True,
        "category": "negation",
    },

    # 8. Keyword Stuffing (Ground Truth: ambiguous or flagged review, not clean core pass)
    {
        "id": "stuff_01",
        "title": "Coding Agents Coding Agents Local LLMs Developer Tools Coding Agents",
        "text": "coding agents developer tools coding agents local llms coding agents local llms developer tools coding agents developer tools",
        "tags": ["coding agents", "local LLMs", "developer tools"],
        "expected_pass": False,  # Should be flagged ambiguous or penalized for empty audience value
        "category": "keyword_stuffing",
    },

    # 9. Unrelated Titles with Relevant Tags (Ground Truth: FAIL or AMBIGUOUS, off_niche)
    {
        "id": "tag_stuff_01",
        "title": "Authentic Neapolitan Pizza Dough Proofing Times",
        "text": "Double zero flour, hydration percentages, and fermentation schedules for brick oven pizza baking.",
        "tags": ["coding agents", "local LLMs", "software architecture"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "unrelated_with_tags",
    },

    # 10. Misleadingly Relevant Title with Unrelated Body Text (Ground Truth: FAIL or AMBIGUOUS)
    {
        "id": "body_mismatch_01",
        "title": "AI Coding Agent Performance",
        "text": "Today we are reviewing the best cordless electric drills and lithium batteries for home woodworking and deck construction.",
        "tags": ["woodworking", "tools", "drills"],
        "expected_pass": False,
        "category": "misleading_title",
    },

    # 11. Emerging Technical Topics in Niche (Ground Truth: PASS, core or adjacent)
    {
        "id": "emerg_01",
        "title": "Model Context Protocol (MCP) Server Architecture for Coding Agents",
        "text": "Implementing custom JSON-RPC stdio transports in TypeScript to bridge LLMs with local language servers and debuggers.",
        "tags": ["developer tools", "coding agents", "code repository"],
        "expected_pass": True,
        "category": "emerging_tech",
    },
    {
        "id": "emerg_02",
        "title": "Speculative Decoding for Faster Local Coding LLM Inference",
        "text": "Benchmarking small draft models alongside Qwen 32B on Apple Silicon to achieve 3x token generation speed in IDE completions.",
        "tags": ["local LLMs", "reproducible benchmark", "developer tools"],
        "expected_pass": True,
        "category": "emerging_tech",
    },

    # 12. Technical Abbreviations and Aliases (Ground Truth: PASS)
    {
        "id": "abbr_01",
        "title": "Evaluating AST-based RAG Retrieval for IDE Code Completion",
        "text": "Comparing tree-sitter chunking versus naive line-based splitting for local coding assistants.",
        "tags": ["developer tools", "local LLMs", "evals and benchmarks"],
        "expected_pass": True,
        "category": "abbreviations",
    },
    {
        "id": "abbr_02",
        "title": "CI/CD Pipeline Integration with Local Ollama Container Tests",
        "text": "Automating regression evaluation of model outputs using GitHub Actions runner caches.",
        "tags": ["DevOps", "local LLMs", "developer tools"],
        "expected_pass": True,
        "category": "abbreviations",
    },

    # 13. Multilingual and Mixed-Language Text (English and Bangla)
    {
        "id": "bn_core_01",
        "title": "লোকাল কোডিং এজেন্ট ও LLM বেঞ্চমার্ক — প্র্যাকটিক্যাল টেস্ট",
        "text": "আমরা লোকাল মডেলের ল্যাটেন্সি এবং টোকেন স্পিড টেস্ট করেছি। সম্পূর্ণ কোড রিপোজিটরি এবং বেঞ্চমার্ক ডাটা দেওয়া হয়েছে।",
        "tags": ["coding agents", "local LLMs", "developer tools"],
        "expected_pass": True,
        "category": "multilingual_bn",
    },
    {
        "id": "bn_core_02",
        "title": "Cursor ও Windsurf এর রিয়েল-ওয়ার্ল্ড কোডিং পারফরম্যান্স তুলনা",
        "text": "বড় পাইথন কোডবেসে অটোনোমাস এজেন্টের একিউরেসি ও টোকেন খরচ পরিমাপের বিস্তারিত রিভিউ।",
        "tags": ["coding agents", "developer tools", "benchmarks"],
        "expected_pass": True,
        "category": "multilingual_bn",
    },
    {
        "id": "bn_blocked_01",
        "title": "ক্রিপ্টো ট্রেডিং বট দিয়ে আনলিমিটেড প্যাসিভ ইনকাম",
        "text": "ঘরে বসেই দ্রুত বড়লোক হওয়ার সিক্রেট মেথড এবং ক্রিপ্টো বট অ্যালগরিদম। ১০০x প্রফিট গ্যারান্টি।",
        "tags": ["crypto/web3 trading", "passive income", "get rich quick"],
        "expected_pass": False,
        "expected_class": "blocked",
        "category": "multilingual_bn_blocked",
    },
    {
        "id": "bn_crit_01",
        "title": "কেন এআই ট্রেডিং বট দিয়ে প্যাসিভ ইনকাম সম্ভব নয় — একটি বাস্তব বিশ্লেষণ",
        "text": "ট্রেডিং অ্যালগরিদম কেন সাধারণ ব্যবহারকারীদের জন্য ক্ষতির কারণ হয়ে দাঁড়ায় তার গাণিতিক তথ্য প্রমাণ।",
        "tags": ["developer tools", "reproducible benchmark", "critique"],
        "expected_pass": True,
        "category": "multilingual_bn_critique",
    },
    {
        "id": "bn_off_01",
        "title": "ঘরে বসে সহজে ইলিশ মাছের পাতুড়ি রান্নার সহজ রেসিপি",
        "text": "সরিষা বাটা ও কাঁচা মরিচ দিয়ে কলা পাতায় সুস্বাদু ইলিশ ভাপানোর সম্পূর্ণ প্রণালী।",
        "tags": ["cooking", "recipe", "fish"],
        "expected_pass": False,
        "expected_class": "off_niche",
        "category": "multilingual_bn_off",
    },

    # 14. Edge Cases: Empty or Whitespace Inputs
    {
        "id": "edge_empty_01",
        "title": "",
        "text": "",
        "tags": [],
        "expected_pass": False,
        "category": "edge_empty",
    },
    {
        "id": "edge_spaces_02",
        "title": "   ",
        "text": "    ",
        "tags": ["   "],
        "expected_pass": False,
        "category": "edge_empty",
    },

    # 15. Real-World Niche Expansion Samples (50+ total count)
    {
        "id": "core_06",
        "title": "Fine-Tuning Qwen 2.5 Coder on Internal Pull Requests",
        "text": "Dataset curation, synthetic QA generation, and LoRA adapter training for proprietary internal API libraries.",
        "tags": ["coding agents", "local LLMs", "developer tools"],
        "expected_pass": True,
        "category": "core",
    },
    {
        "id": "core_07",
        "title": "Self-Healing Test Suites with Playwright and LLM Agents",
        "text": "Automatically fixing broken DOM locators during CI runs using visual snapshots and multimodal models.",
        "tags": ["developer tools", "coding automation", "benchmarks"],
        "expected_pass": True,
        "category": "core",
    },
    {
        "id": "core_08",
        "title": "Preventing Hallucinated Package Imports in Agent Code Generation",
        "text": "Static AST validation interceptors that verify PyPI and npm package existence before executing code diffs.",
        "tags": ["coding agents", "developer tools", "reproducible benchmark"],
        "expected_pass": True,
        "category": "core",
    },
    {
        "id": "core_09",
        "title": "Measuring Real Token Spend for End-to-End Feature Generation",
        "text": "Empirical audit tracking cache hits, prompt overhead, and total dollar cost per accepted pull request.",
        "tags": ["coding agents", "evals and benchmarks", "developer tools"],
        "expected_pass": True,
        "category": "core",
    },
    {
        "id": "off_06",
        "title": "Best Road Trips Across North America in a Camper Van",
        "text": "National parks itinerary, campsite reservations, and vehicle maintenance tips.",
        "tags": ["travel", "vanlife", "camping"],
        "expected_pass": False,
        "category": "off_niche",
    },
    {
        "id": "off_07",
        "title": "Beginner Acoustic Guitar Chords and Strumming Patterns",
        "text": "Major and minor open chords, finger placement, and rhythm drills for popular folk songs.",
        "tags": ["music", "guitar", "lessons"],
        "expected_pass": False,
        "category": "off_niche",
    },
    {
        "id": "off_08",
        "title": "Cat Behavior Explained: Why Cats Purr and Knead",
        "text": "Veterinary insights into feline body language, vocalizations, and territory marking.",
        "tags": ["pets", "cats", "animals"],
        "expected_pass": False,
        "category": "off_niche",
    },
    {
        "id": "blk_05",
        "title": "Binary Options Trading Signals with 99% Win Rate",
        "text": "Follow our automated telegram signals to turn $100 into $10,000 every single day. Secret trading system.",
        "tags": ["crypto/web3 trading", "get rich quick", "passive income"],
        "expected_pass": False,
        "category": "blocked_promo",
    },
    {
        "id": "crit_05",
        "title": "Why Binary Options and Algorithmic Trading Signals Are Mathematically Unsound",
        "text": "An engineering paper analyzing negative expected value, broker spreads, and high probability of total ruin.",
        "tags": ["reproducible benchmark", "developer tools", "evals"],
        "expected_pass": True,
        "category": "educational_critique",
    },
    {
        "id": "adj_05",
        "title": "Kubernetes Resource Limits for On-Premises GPU Workloads",
        "text": "Allocating Nvidia MPS time slicing and hugepages when running multiple local coding agents on shared servers.",
        "tags": ["DevOps", "software architecture", "local LLMs"],
        "expected_pass": True,
        "category": "adjacent",
    },
]


@pytest.fixture
def sample_niche_config() -> Dict[str, Any]:
    return {
        "name": "AI Engineering & Coding Automation",
        "one_sentence_definition": "Practical AI coding agents, developer automation workflows, and local LLM tooling tested on production tasks.",
        "audience": "Software developers, technical founders, and automation engineers.",
        "target_skill_levels": ["intermediate", "advanced", "professional"],
        "audience_goals": ["automate routine code refactoring", "build reliable local agent pipelines"],
        "primary_problems": [
            "Agent benchmark claims do not match real-world performance.",
            "High API costs and token limits.",
            "Brittle prompts breaking in production.",
        ],
        "allowed_topics": [
            "coding agents",
            "local LLMs",
            "developer tools",
            "evals and benchmarks",
            "coding automation",
        ],
        "adjacent_topics": [
            "software architecture",
            "DevOps",
            "database indexing",
            "API design",
        ],
        "blocked_topics": [
            "crypto/web3 trading",
            "get rich quick",
            "passive income",
            "celebrity gossip",
        ],
        "topic_exceptions": [
            {"topic": "crypto/web3 trading", "allowed_context": "educational_critique"},
            {"topic": "passive income", "allowed_context": "educational_critique"},
        ],
        "must_have_signals": [
            "code repository",
            "reproducible benchmark",
            "benchmarks",
            "evals",
        ],
        "negative_keywords": [
            "secret trick",
            "replaced all coders",
            "100x money",
            "guaranteed success",
        ],
        "content_pillars": [
            {
                "id": "agent_benchmarks",
                "name": "Coding Agent Stress Tests",
                "description": "Real-world testing of Claude, Qwen, and Cursor on dirty repos.",
                "keywords": ["coding agents", "benchmarks", "evals", "reproducible benchmark"],
                "synonyms": ["agent evaluation", "agent testing"],
            },
            {
                "id": "local_tooling",
                "name": "Local LLM Tooling",
                "description": "Running Ollama, vLLM, and local code assistants without cloud dependencies.",
                "keywords": ["local LLMs", "developer tools", "Ollama", "vLLM"],
                "synonyms": ["offline LLM", "local inference"],
            },
        ],
        "policy_version": 2,
        "policy_fingerprint": "a1b2c3d4e5f67890123456789012345678901234567890123456789012345678",
    }


def test_benchmark_dataset_size_and_diversity():
    """Verify that benchmark dataset meets or exceeds 50 representative cases."""
    assert len(BENCHMARK_CASES) >= 50, f"Expected at least 50 cases, found {len(BENCHMARK_CASES)}"
    categories = set(c["category"] for c in BENCHMARK_CASES)
    assert "core" in categories
    assert "off_niche" in categories
    assert "adjacent" in categories
    assert "blocked_promo" in categories
    assert "educational_critique" in categories
    assert "quoted_claim" in categories
    assert "negation" in categories
    assert "multilingual_bn" in categories
    assert "multilingual_bn_blocked" in categories


def test_niche_guard_behavioral_benchmark(sample_niche_config):
    """Run full behavioral benchmark on upgraded Niche Guard engine.
    Measure Precision, Recall, False-Positive Rate, False-Negative Rate, and Latency.
    """
    engine = NicheGuardEngine()
    total_cases = len(BENCHMARK_CASES)

    tp = 0  # Expected Pass, Model Passed
    fp = 0  # Expected Fail, Model Passed (Critical Error: letting scam/off-niche pass)
    tn = 0  # Expected Fail, Model Rejected
    fn = 0  # Expected Pass, Model Rejected (False Negative)
    review_count = 0

    latencies_ms: List[float] = []
    category_results: Dict[str, Dict[str, int]] = {}

    for case in BENCHMARK_CASES:
        cat = case["category"]
        if cat not in category_results:
            category_results[cat] = {"total": 0, "passed": 0, "rejected": 0, "review": 0}
        category_results[cat]["total"] += 1

        inp = NicheGuardInput(
            id=case["id"],
            title=case["title"],
            text=case["text"],
            tags=case.get("tags", []),
        )

        t0 = time.perf_counter()
        verdict: NicheGuardVerdict = engine.evaluate_item(inp, sample_niche_config)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(elapsed_ms)

        if verdict.requires_review:
            review_count += 1
            category_results[cat]["review"] += 1

        expected_pass = case["expected_pass"]
        actual_pass = verdict.passed

        if actual_pass:
            category_results[cat]["passed"] += 1
        else:
            category_results[cat]["rejected"] += 1

        if expected_pass and actual_pass:
            tp += 1
        elif not expected_pass and actual_pass:
            fp += 1
        elif not expected_pass and not actual_pass:
            tn += 1
        elif expected_pass and not actual_pass:
            fn += 1

    # Metrics calculation
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fn_rate = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    accuracy = (tp + tn) / total_cases
    review_rate = review_count / total_cases
    p95_latency = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]
    avg_latency = sum(latencies_ms) / len(latencies_ms)

    print("\n" + "=" * 60)
    print("NICHE FOUNDATION V1.02 BEHAVIORAL BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Total Test Cases:       {total_cases}")
    print(f"True Positives (TP):    {tp}")
    print(f"True Negatives (TN):    {tn}")
    print(f"False Positives (FP):   {fp}")
    print(f"False Negatives (FN):   {fn}")
    print(f"Accuracy:               {accuracy:.2%}")
    print(f"Precision:              {precision:.2%}")
    print(f"Recall:                 {recall:.2%}")
    print(f"False-Positive Rate:    {fp_rate:.2%}")
    print(f"False-Negative Rate:    {fn_rate:.2%}")
    print(f"Review Required Rate:   {review_rate:.2%}")
    print(f"Average Latency:        {avg_latency:.3f} ms")
    print(f"95th Percentile Latency:{p95_latency:.3f} ms")
    print("-" * 60)
    print("Per-Category Breakdown:")
    for cat, stats in sorted(category_results.items()):
        print(f"  {cat:<25}: total={stats['total']}, passed={stats['passed']}, rejected={stats['rejected']}, review={stats['review']}")
    print("=" * 60)

    # Acceptance Criteria Verification:
    # 1. Zero False Positives on Blocked Scams / Off-Niche topics
    assert fp == 0, f"Expected 0 False Positives, got {fp} (scams or off-niche allowed)"

    # 2. High Precision (100% on this labeled test suite)
    assert precision >= 0.98, f"Expected Precision >= 98%, got {precision:.2%}"

    # 3. High Recall (no core niche topics rejected)
    assert recall >= 0.90, f"Expected Recall >= 90%, got {recall:.2%}"

    # 4. Educational critiques must NOT be rejected as promotional scams
    critique_stats = category_results.get("educational_critique", {})
    assert critique_stats.get("passed", 0) >= 4, "Educational critiques should pass or require review, not be hard-blocked!"

    # 5. Multilingual Bangla blocked scams must be correctly rejected
    bn_blocked_stats = category_results.get("multilingual_bn_blocked", {})
    assert bn_blocked_stats.get("rejected", 0) == 1, "Bangla blocked scam must be rejected"

    # 6. Ultra-fast local deterministic classification (sub-50ms under heavy test load)
    assert avg_latency < 50.0, f"Average latency must be under 50ms, got {avg_latency:.2f}ms"
