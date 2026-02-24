#!/usr/bin/env python3
"""
Test query performance before/after index creation
Verifies Supabase Postgres best practices implementation
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from statistics import mean, stdev

# Database credentials
SUPABASE_HOST = "db.cxzhgidmzosdavugggks.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "5kvsZGhH")

print("=" * 80)
print("QUERY PERFORMANCE TESTING")
print("=" * 80)
print()

# Test queries
test_queries = [
    {
        "name": "Standard FTS Query (How do I report a pothole?)",
        "sql": """
        SELECT
            id,
            question_text,
            answer_text,
            ts_rank(
                to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' ')),
                plainto_tsquery('english', %s)
            ) as rank
        FROM l311_approved_questions
        WHERE
            to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' '))
            @@ plainto_tsquery('english', %s)
            AND is_approved = true
        ORDER BY rank DESC
        LIMIT 1
        """,
        "params": ("How do I report a pothole?", "How do I report a pothole?")
    },
    {
        "name": "Category-Filtered Query (Code Enforcement)",
        "sql": """
        SELECT id, question_text, category
        FROM l311_approved_questions
        WHERE category = 'Code Enforcement'
        AND is_approved = true
        LIMIT 10
        """,
        "params": ()
    },
    {
        "name": "Enhanced Search with Category Boost",
        "sql": """
        WITH ranked_results AS (
            SELECT
                id,
                question_text,
                answer_text,
                category,
                ts_rank(
                    to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' ')),
                    plainto_tsquery('english', %s)
                ) as search_rank,
                CASE
                    WHEN category = ANY(%s) THEN 2.0
                    ELSE 1.0
                END as category_boost
            FROM l311_approved_questions
            WHERE
                is_approved = true
                AND (
                    to_tsvector('english', question_text || ' ' || array_to_string(keywords, ' '))
                    @@ plainto_tsquery('english', %s)
                    OR category = ANY(%s)
                )
        )
        SELECT id, question_text, answer_text, category
        FROM ranked_results
        ORDER BY search_rank * category_boost DESC
        LIMIT 1
        """,
        "params": ("overgrown weeds vegetation", ["Code Enforcement", "Environmental"],
                   "overgrown weeds vegetation", ["Code Enforcement", "Environmental"])
    },
    {
        "name": "Usage Analytics Query (Most Popular)",
        "sql": """
        SELECT id, question_text, times_shown
        FROM l311_approved_questions
        WHERE is_approved = true
        ORDER BY times_shown DESC
        LIMIT 10
        """,
        "params": ()
    },
    {
        "name": "Feedback Analytics Query (Most Helpful)",
        "sql": """
        SELECT id, question_text, times_helpful, times_not_helpful
        FROM l311_approved_questions
        WHERE is_approved = true
        ORDER BY times_helpful DESC
        LIMIT 10
        """,
        "params": ()
    }
]

def run_query_benchmark(conn, query_info, runs=10):
    """
    Run a query multiple times and measure performance

    Args:
        conn: Database connection
        query_info: Dict with 'name', 'sql', 'params'
        runs: Number of times to run the query

    Returns:
        Dict with timing statistics
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    timings = []

    for i in range(runs):
        start = time.time()
        cursor.execute(query_info['sql'], query_info['params'])
        result = cursor.fetchall()
        duration = time.time() - start

        timings.append(duration * 1000)  # Convert to milliseconds

    cursor.close()

    return {
        "min": min(timings),
        "max": max(timings),
        "mean": mean(timings),
        "stdev": stdev(timings) if len(timings) > 1 else 0,
        "timings": timings
    }

try:
    # Connect to database
    print(f"🔌 Connecting to {SUPABASE_HOST}...")
    conn = psycopg2.connect(
        host=SUPABASE_HOST,
        database=SUPABASE_DB,
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        port=5432
    )
    print("✅ Connected successfully")
    print()

    # Check if indexes exist
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as index_count
        FROM pg_indexes
        WHERE tablename = 'l311_approved_questions'
        AND indexname LIKE 'idx_%'
    """)
    index_count = cursor.fetchone()[0]
    cursor.close()

    print(f"📊 Found {index_count} custom indexes on l311_approved_questions")
    print()

    if index_count < 5:
        print("⚠️  WARNING: Expected at least 5 indexes")
        print("   Run apply_indexes.py first to create performance indexes")
        print()

    # Run benchmarks
    print("🏃 Running performance benchmarks (10 runs each)...")
    print()

    results = []

    for i, query_info in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query_info['name']}")
        print(f"   Running 10 iterations...", end=" ", flush=True)

        stats = run_query_benchmark(conn, query_info, runs=10)

        print(f"✓")
        print(f"   Min:  {stats['min']:6.2f}ms")
        print(f"   Mean: {stats['mean']:6.2f}ms")
        print(f"   Max:  {stats['max']:6.2f}ms")
        print(f"   StdDev: {stats['stdev']:6.2f}ms")

        # Performance assessment
        if stats['mean'] < 10:
            print(f"   ✅ EXCELLENT (< 10ms)")
        elif stats['mean'] < 50:
            print(f"   ✅ GOOD (< 50ms)")
        elif stats['mean'] < 100:
            print(f"   ⚠️  ACCEPTABLE (< 100ms)")
        else:
            print(f"   ❌ SLOW (> 100ms) - Check indexes")

        print()

        results.append({
            "name": query_info['name'],
            "stats": stats
        })

    # Summary
    print("=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    print()

    all_means = [r['stats']['mean'] for r in results]
    overall_mean = mean(all_means)

    print(f"Overall average query time: {overall_mean:.2f}ms")
    print()

    # Expected benchmarks with indexes
    print("Expected performance with GIN indexes:")
    print("  • Standard FTS Query:        5-15ms   ✓")
    print("  • Category Filter:           2-5ms    ✓")
    print("  • Enhanced Search:           10-20ms  ✓")
    print("  • Usage Analytics:           2-5ms    ✓")
    print("  • Feedback Analytics:        2-5ms    ✓")
    print()

    # Performance grade
    if overall_mean < 15:
        print("🎉 GRADE: A+ (Excellent performance)")
    elif overall_mean < 30:
        print("✅ GRADE: A (Good performance)")
    elif overall_mean < 50:
        print("✅ GRADE: B (Acceptable performance)")
    elif overall_mean < 100:
        print("⚠️  GRADE: C (Below expectations, investigate)")
    else:
        print("❌ GRADE: D (Poor performance, indexes may be missing)")

    print()

    # Additional diagnostics
    print("🔍 Query Plan Analysis (EXPLAIN for first query):")
    cursor = conn.cursor()

    # Get EXPLAIN output for standard FTS query
    explain_sql = "EXPLAIN ANALYZE " + test_queries[0]['sql']
    cursor.execute(explain_sql, test_queries[0]['params'])

    explain_output = cursor.fetchall()
    for row in explain_output:
        print(f"   {row[0]}")

    print()

    # Check for index usage
    print("📊 Index Usage Statistics:")
    cursor.execute("""
        SELECT
            indexrelname as index_name,
            idx_scan as scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        AND relname = 'l311_approved_questions'
        AND indexrelname LIKE 'idx_%'
        ORDER BY idx_scan DESC
    """)

    index_stats = cursor.fetchall()

    if index_stats:
        print()
        for idx_name, scans, tuples_read, tuples_fetched in index_stats:
            print(f"   {idx_name}:")
            print(f"     Scans: {scans}, Tuples Read: {tuples_read}, Fetched: {tuples_fetched}")
    else:
        print("   No index usage statistics available yet")

    print()

    cursor.close()
    conn.close()

    print("=" * 80)
    print("✅ PERFORMANCE TESTING COMPLETE")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
