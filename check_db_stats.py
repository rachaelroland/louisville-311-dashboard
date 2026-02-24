#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host='db.cxzhgidmzosdavugggks.supabase.co',
    database='postgres',
    user='postgres',
    password='5kvsZGhH',
    port=5432
)

cursor = conn.cursor()

# Check if times_shown has been incremented
cursor.execute('''
SELECT id, question_text, times_shown, times_helpful, times_not_helpful
FROM l311_approved_questions
WHERE times_shown > 0
ORDER BY times_shown DESC
LIMIT 10
''')

results = cursor.fetchall()

print('Questions with usage stats:')
print('=' * 80)
if results:
    for row in results:
        print(f'ID {row[0]}: {row[1][:60]}')
        print(f'   Shown: {row[2]}, Helpful: {row[3]}, Not helpful: {row[4]}')
        print()
else:
    print('❌ No questions have been shown yet - database integration may not be working')
    print()
    print('Testing database connection...')

    # Test that we can at least query questions
    cursor.execute('SELECT COUNT(*) FROM l311_approved_questions WHERE is_approved = true')
    count = cursor.fetchone()[0]
    print(f'✅ Database accessible - {count} approved questions found')

cursor.close()
conn.close()
