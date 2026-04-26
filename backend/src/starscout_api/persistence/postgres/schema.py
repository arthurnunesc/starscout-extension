SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS import_runs (
    source_name TEXT NOT NULL,
    source_version TEXT NOT NULL,
    analyzed_through TEXT NOT NULL,
    low_activity_count INTEGER NOT NULL,
    lockstep_count INTEGER NOT NULL,
    deduped_fact_count INTEGER NOT NULL,
    aggregate_count INTEGER NOT NULL,
    status TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (source_name, source_version)
);

CREATE TABLE IF NOT EXISTS suspicious_star_facts (
    repo TEXT NOT NULL,
    actor TEXT NOT NULL,
    starred_at TEXT NOT NULL,
    low_activity BOOLEAN NOT NULL,
    lockstep BOOLEAN NOT NULL,
    PRIMARY KEY (repo, actor, starred_at)
);

CREATE TABLE IF NOT EXISTS repo_aggregates (
    repo TEXT PRIMARY KEY,
    suspected_non_legit_stars INTEGER NOT NULL,
    low_activity_count INTEGER NOT NULL,
    lockstep_count INTEGER NOT NULL,
    overlap_count INTEGER NOT NULL,
    analyzed_through TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS github_repo_cache (
    repo TEXT PRIMARY KEY,
    canonical_full_name TEXT NOT NULL,
    github_repo_id BIGINT NOT NULL,
    github_node_id TEXT NOT NULL,
    stargazers_count INTEGER NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
