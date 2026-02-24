import psycopg2
from psycopg2.extras import RealDictCursor
import os

SUPABASE_HOST = "db.cxzhgidmzosdavugggks.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "5kvsZGhH")

# Connect to database
conn = psycopg2.connect(
    host=SUPABASE_HOST,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    port=5432
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Get all waste management related questions
query = '''
SELECT id, question_text, answer_text, category, keywords
FROM l311_approved_questions
WHERE is_approved = true
AND (
    category ILIKE '%waste%' 
    OR category ILIKE '%garbage%'
    OR category ILIKE '%trash%'
    OR category ILIKE '%recycl%'
    OR question_text ILIKE '%waste%'
    OR question_text ILIKE '%garbage%'
    OR question_text ILIKE '%trash%'
    OR question_text ILIKE '%recycl%'
    OR question_text ILIKE '%cart%'
    OR question_text ILIKE '%bin%'
)
ORDER BY category, question_text;
'''

cursor.execute(query)
results = cursor.fetchall()

print(f'Found {len(results)} waste management questions:\n')

for r in results:
    print(f"Category: {r['category']}")
    print(f"Q: {r['question_text']}")
    print(f"Keywords: {', '.join(r['keywords']) if r['keywords'] else 'None'}")
    print(f"A (first 150 chars): {r['answer_text'][:150]}...")
    print('-' * 100)

cursor.close()
conn.close()
