"""Tests for Alembic migration upgrade and rollback of V1.02 Niche Foundation.

Verifies:
1. Upgrading a disposable database to V1.01 (b1c2d3e4f5a6) succeeds.
2. Existing V1.01 niche profile and content data can be seeded.
3. Upgrading to V1.02 (c2d3e4f5a6b7 / head) preserves existing profile data,
   adds the 5 new columns with proper defaults, and creates niche_policy_audits.
4. Downgrading back to V1.01 preserves existing niche profile data, cleanly drops
   new columns, and drops niche_policy_audits without schema corruption.
5. Re-upgrading to head succeeds idempotently.
"""
import json
import sqlite3
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config

from app.core.config import settings


@pytest.fixture
def disposable_db(tmp_path, monkeypatch):
    """Provide a temporary SQLite database path and patch settings.DATABASE_URL."""
    db_file = tmp_path / "test_migration_disposable.sqlite"
    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", db_url)
    
    # Configure Alembic
    api_dir = Path(__file__).resolve().parent.parent
    alembic_ini_path = api_dir / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(api_dir / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_file.as_posix()}")

    yield db_file, alembic_cfg


def test_niche_foundation_v1_02_migration_upgrade_and_downgrade(disposable_db):
    """Verify clean upgrade from V1.01 to V1.02 and clean rollback without data loss."""
    db_file, alembic_cfg = disposable_db

    # 1. Migrate to V1.01 baseline (b1c2d3e4f5a6)
    command.upgrade(alembic_cfg, "b1c2d3e4f5a6")

    # Connect synchronously with sqlite3 to inspect and insert V1.01 data
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    # Verify niche_profiles exists in V1.01
    cursor.execute("PRAGMA table_info(niche_profiles)")
    v101_columns = [row[1] for row in cursor.fetchall()]
    assert "id" in v101_columns
    assert "name" in v101_columns
    assert "content_pillars" in v101_columns
    assert "allowed_topics" in v101_columns
    assert "blocked_topics" in v101_columns
    assert "target_skill_levels" not in v101_columns
    assert "policy_fingerprint" not in v101_columns

    # Seed an existing V1.01 niche profile
    pillars = json.dumps(["Autonomous AI Agents", "Local LLMs"])
    allowed = json.dumps(["LangChain", "LlamaIndex", "Ollama"])
    blocked = json.dumps(["Crypto", "Get rich quick"])
    empty_list = json.dumps([])
    cursor.execute(
        """
        INSERT INTO niche_profiles (
            id, name, one_sentence_definition, audience, audience_regions,
            primary_problems, allowed_topics, adjacent_topics, blocked_topics,
            must_have_signals, negative_keywords, preferred_source_types,
            content_pillars, commercial_intent_topics, evergreen_topics,
            created_at, updated_at
        ) VALUES (
            'primary', 'AI Engineering', 'Local AI workflows', 'Software developers', ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            datetime('now'), datetime('now')
        )
        """,
        (empty_list, empty_list, allowed, empty_list, blocked,
         empty_list, empty_list, empty_list,
         pillars, empty_list, empty_list),
    )
    conn.commit()

    # 2. Upgrade to V1.02 head (c2d3e4f5a6b7)
    command.upgrade(alembic_cfg, "c2d3e4f5a6b7")

    # Verify new columns in niche_profiles
    cursor.execute("PRAGMA table_info(niche_profiles)")
    v102_columns = {row[1]: row for row in cursor.fetchall()}
    assert "target_skill_levels" in v102_columns
    assert "audience_goals" in v102_columns
    assert "topic_exceptions" in v102_columns
    assert "policy_version" in v102_columns
    assert "policy_fingerprint" in v102_columns

    # Verify existing profile data is preserved intact with defaults
    cursor.execute("SELECT id, name, content_pillars, allowed_topics, blocked_topics, policy_version, target_skill_levels FROM niche_profiles WHERE id = 'primary'")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "primary"
    assert row[1] == "AI Engineering"
    assert json.loads(row[2]) == ["Autonomous AI Agents", "Local LLMs"]
    assert json.loads(row[3]) == ["LangChain", "LlamaIndex", "Ollama"]
    assert json.loads(row[4]) == ["Crypto", "Get rich quick"]
    assert row[5] == 1  # Default policy_version
    assert json.loads(row[6]) == []  # Default target_skill_levels

    # Verify niche_policy_audits table exists
    cursor.execute("PRAGMA table_info(niche_policy_audits)")
    audit_columns = [r[1] for r in cursor.fetchall()]
    assert "id" in audit_columns
    assert "niche_id" in audit_columns
    assert "version" in audit_columns
    assert "fingerprint" in audit_columns
    assert "snapshot" in audit_columns

    # 3. Roll back (downgrade) back to V1.01 (b1c2d3e4f5a6)
    command.downgrade(alembic_cfg, "b1c2d3e4f5a6")

    # Verify new columns dropped and niche_policy_audits dropped
    cursor.execute("PRAGMA table_info(niche_profiles)")
    downgraded_columns = [r[1] for r in cursor.fetchall()]
    assert "target_skill_levels" not in downgraded_columns
    assert "policy_fingerprint" not in downgraded_columns

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='niche_policy_audits'")
    assert cursor.fetchone() is None

    # Verify existing profile row is STILL intact after downgrade
    cursor.execute("SELECT id, name, content_pillars FROM niche_profiles WHERE id = 'primary'")
    retained_row = cursor.fetchone()
    assert retained_row is not None
    assert retained_row[0] == "primary"
    assert retained_row[1] == "AI Engineering"
    assert json.loads(retained_row[2]) == ["Autonomous AI Agents", "Local LLMs"]

    # 4. Re-upgrade to head to prove idempotent re-application
    command.upgrade(alembic_cfg, "head")
    cursor.execute("PRAGMA table_info(niche_profiles)")
    re_upgraded_cols = [r[1] for r in cursor.fetchall()]
    assert "policy_version" in re_upgraded_cols
    assert "policy_fingerprint" in re_upgraded_cols

    conn.close()
