#!/usr/bin/env python3
"""
Test and Validate Chat Agent Against Approved Questions
Sends all 53 approved questions to the chat agent and validates responses
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from difflib import SequenceMatcher

# ============================================================================
# CONFIGURATION
# ============================================================================

# Database connection (Supabase)
SUPABASE_HOST = "db.cxzhgidmzosdavugggks.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "5kvsZGhH")  # From environment or default

# Chat endpoint (assumes dashboard is running locally)
CHAT_URL = "http://localhost:5003/chat/ask"

# Output paths
CURRENT_DIR = Path(__file__).parent
RESULTS_PATH = CURRENT_DIR / "validation_results.json"
REPORT_PATH = CURRENT_DIR / "validation_report.md"

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_approved_questions():
    """Fetch all approved questions from Supabase database"""
    print("📊 Connecting to Supabase database...")

    conn_string = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:5432/{SUPABASE_DB}"

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT
            id, question_text, answer_text, category, subcategory,
            question_type, keywords, typical_urgency, typical_response_time,
            service_name
        FROM l311_approved_questions
        WHERE is_approved = true
        ORDER BY category, id
        """

        cursor.execute(query)
        questions = cursor.fetchall()

        cursor.close()
        conn.close()

        print(f"✅ Loaded {len(questions)} approved questions from database\n")
        return questions

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Connection string: postgresql://{SUPABASE_USER}:***@{SUPABASE_HOST}:5432/{SUPABASE_DB}")
        sys.exit(1)

# ============================================================================
# CHAT AGENT TESTING
# ============================================================================

def send_question_to_agent(question_text, timeout=30):
    """
    Send a question to the chat agent and return the response
    Returns: (success: bool, response: str, error: str|None)
    """
    try:
        response = requests.post(
            CHAT_URL,
            data={"message": question_text},
            timeout=timeout
        )

        if response.status_code == 200:
            # Parse HTML response to extract assistant message
            html_text = response.text

            # Extract assistant message using BeautifulSoup-like parsing
            if "assistant-message" in html_text:
                try:
                    # Find the assistant message div
                    start_tag = '<div class="message assistant-message">'
                    start = html_text.find(start_tag)
                    if start == -1:
                        return False, "", "Could not find assistant message start tag"

                    start += len(start_tag)
                    end = html_text.find('</div>', start)

                    if end == -1:
                        return False, "", "Could not find assistant message end tag"

                    assistant_text = html_text[start:end].strip()

                    # Remove any HTML tags that might be in the text
                    import re
                    assistant_text = re.sub(r'<[^>]+>', '', assistant_text)

                    return True, assistant_text, None
                except Exception as e:
                    return False, "", f"Error parsing HTML: {str(e)}"
            else:
                return False, "", "No assistant message found in response"
        else:
            return False, "", f"HTTP {response.status_code}: {response.text[:200]}"

    except requests.exceptions.Timeout:
        return False, "", "Request timed out"
    except requests.exceptions.ConnectionError:
        return False, "", "Connection failed - is the dashboard running at http://localhost:5002?"
    except Exception as e:
        return False, "", f"Error: {str(e)}"

# ============================================================================
# ANSWER VALIDATION
# ============================================================================

def calculate_similarity(text1, text2):
    """Calculate similarity ratio between two texts (0-1)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def validate_answer(question_data, agent_response):
    """
    Validate agent response against approved answer
    Returns: {
        'is_valid': bool,
        'similarity_score': float,
        'contains_keywords': bool,
        'mentions_service': bool,
        'has_contact_info': bool,
        'issues': []
    }
    """
    approved_answer = question_data['answer_text']
    category = question_data['category']
    keywords = question_data.get('keywords', [])
    service_name = question_data.get('service_name')

    validation = {
        'is_valid': True,
        'similarity_score': 0.0,
        'contains_keywords': False,
        'mentions_service': False,
        'has_contact_info': False,
        'has_procedure': False,
        'issues': []
    }

    # 1. Similarity to approved answer (shouldn't be exact, but should cover key points)
    similarity = calculate_similarity(approved_answer, agent_response)
    validation['similarity_score'] = similarity

    # 2. Check if response contains key keywords
    agent_lower = agent_response.lower()
    keyword_matches = sum(1 for kw in keywords if kw.lower() in agent_lower)
    validation['contains_keywords'] = keyword_matches >= max(1, len(keywords) // 2)

    # 3. Check if service name is mentioned (if applicable)
    if service_name:
        validation['mentions_service'] = service_name.lower() in agent_lower
    else:
        validation['mentions_service'] = True  # N/A

    # 4. Check for contact information (311, phone, website)
    contact_indicators = ['311', '574-5000', 'louisvilleky.gov', 'call', 'phone', 'online']
    validation['has_contact_info'] = any(indicator in agent_lower for indicator in contact_indicators)

    # 5. Check for procedure/process description (how-to questions)
    if question_data['question_type'] == 'how_to':
        procedure_indicators = ['report', 'submit', 'call', 'provide', 'describe', 'will', 'typically']
        validation['has_procedure'] = any(indicator in agent_lower for indicator in procedure_indicators)
    else:
        validation['has_procedure'] = True  # N/A

    # Determine validity based on checks
    if not validation['has_contact_info']:
        validation['issues'].append("Missing contact information (311 or louisvilleky.gov)")
        validation['is_valid'] = False

    if not validation['contains_keywords']:
        validation['issues'].append(f"Missing key keywords from: {keywords}")

    if not validation['mentions_service'] and service_name:
        validation['issues'].append(f"Does not mention service: {service_name}")

    if not validation['has_procedure'] and question_data['question_type'] == 'how_to':
        validation['issues'].append("How-to question but response lacks procedural guidance")
        validation['is_valid'] = False

    # If no critical issues but low similarity, mark as warning
    if validation['is_valid'] and similarity < 0.3:
        validation['issues'].append(f"Low similarity to approved answer ({similarity:.2%})")

    return validation

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_validation_tests():
    """Run validation tests on all approved questions"""
    print("=" * 80)
    print("LOUISVILLE 311 - APPROVED QUESTIONS VALIDATION TEST")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n")

    # Load questions from database
    questions = get_approved_questions()
    total_questions = len(questions)

    # Results storage
    results = {
        'metadata': {
            'test_date': datetime.now().isoformat(),
            'total_questions': total_questions,
            'chat_endpoint': CHAT_URL,
            'database_host': SUPABASE_HOST
        },
        'questions': [],
        'summary': {
            'total': total_questions,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'average_similarity': 0.0,
            'response_time_avg': 0.0
        }
    }

    print(f"🧪 Testing {total_questions} approved questions...")
    print(f"📡 Chat endpoint: {CHAT_URL}")
    print(f"⏱️  Estimated time: {total_questions * 3} seconds (~{total_questions * 3 / 60:.1f} minutes)\n")

    # Test each question
    for idx, q in enumerate(questions, 1):
        question_text = q['question_text']
        category = q['category']

        print(f"[{idx}/{total_questions}] Testing: {question_text[:60]}...")

        # Send to agent
        start_time = time.time()
        success, agent_response, error = send_question_to_agent(question_text)
        response_time = time.time() - start_time

        if not success:
            print(f"   ❌ ERROR: {error}")
            results['questions'].append({
                'id': q['id'],
                'question': question_text,
                'category': category,
                'status': 'error',
                'error': error,
                'response_time': response_time
            })
            results['summary']['errors'] += 1
            time.sleep(1)  # Brief pause before next request
            continue

        # Validate response
        validation = validate_answer(q, agent_response)

        # Store result
        result_entry = {
            'id': q['id'],
            'question': question_text,
            'category': category,
            'subcategory': q.get('subcategory'),
            'question_type': q['question_type'],
            'approved_answer': q['answer_text'],
            'agent_response': agent_response,
            'validation': validation,
            'status': 'passed' if validation['is_valid'] else 'failed',
            'response_time': response_time
        }
        results['questions'].append(result_entry)

        # Update summary
        if validation['is_valid']:
            results['summary']['passed'] += 1
            print(f"   ✅ PASSED (similarity: {validation['similarity_score']:.2%})")
        else:
            results['summary']['failed'] += 1
            print(f"   ⚠️  FAILED - Issues: {', '.join(validation['issues'])}")

        # Rate limiting - pause between requests
        time.sleep(1)

    # Calculate summary statistics
    valid_responses = [r for r in results['questions'] if r['status'] != 'error']
    if valid_responses:
        avg_similarity = sum(r['validation']['similarity_score'] for r in valid_responses) / len(valid_responses)
        avg_response_time = sum(r['response_time'] for r in results['questions']) / len(results['questions'])
        results['summary']['average_similarity'] = avg_similarity
        results['summary']['response_time_avg'] = avg_response_time

    # Save results to JSON
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {RESULTS_PATH}")

    # Generate report
    generate_report(results)

    print(f"\n📄 Report saved to: {REPORT_PATH}")

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Questions:     {results['summary']['total']}")
    print(f"Passed:              {results['summary']['passed']} ({results['summary']['passed']/total_questions*100:.1f}%)")
    print(f"Failed:              {results['summary']['failed']} ({results['summary']['failed']/total_questions*100:.1f}%)")
    print(f"Errors:              {results['summary']['errors']} ({results['summary']['errors']/total_questions*100:.1f}%)")
    print(f"Average Similarity:  {results['summary']['average_similarity']:.2%}")
    print(f"Avg Response Time:   {results['summary']['response_time_avg']:.2f}s")
    print("=" * 80)

    return results

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report(results):
    """Generate markdown report from validation results"""

    report = []
    report.append("# Louisville 311 - Approved Questions Validation Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n")
    report.append(f"**Chat Endpoint:** {results['metadata']['chat_endpoint']}\n")
    report.append(f"**Database:** {results['metadata']['database_host']}\n")
    report.append("---\n")

    # Executive Summary
    summary = results['summary']
    report.append("## Executive Summary\n")
    report.append(f"- **Total Questions Tested:** {summary['total']}\n")
    report.append(f"- **Passed:** {summary['passed']} ({summary['passed']/summary['total']*100:.1f}%)\n")
    report.append(f"- **Failed:** {summary['failed']} ({summary['failed']/summary['total']*100:.1f}%)\n")
    report.append(f"- **Errors:** {summary['errors']} ({summary['errors']/summary['total']*100:.1f}%)\n")
    report.append(f"- **Average Similarity:** {summary['average_similarity']:.2%}\n")
    report.append(f"- **Average Response Time:** {summary['response_time_avg']:.2f}s\n")
    report.append("\n---\n")

    # Failed Questions
    failed = [r for r in results['questions'] if r['status'] == 'failed']
    if failed:
        report.append(f"## Failed Questions ({len(failed)})\n")
        for r in failed:
            report.append(f"### {r['question']}\n")
            report.append(f"**Category:** {r['category']}\n")
            report.append(f"**Issues:** {', '.join(r['validation']['issues'])}\n")
            report.append(f"**Similarity Score:** {r['validation']['similarity_score']:.2%}\n")
            report.append(f"\n**Agent Response:**\n```\n{r['agent_response']}\n```\n")
            report.append(f"\n**Approved Answer:**\n```\n{r['approved_answer']}\n```\n")
            report.append("\n---\n")

    # Errors
    errors = [r for r in results['questions'] if r['status'] == 'error']
    if errors:
        report.append(f"## Errors ({len(errors)})\n")
        for r in errors:
            report.append(f"- **{r['question']}** - {r['error']}\n")
        report.append("\n---\n")

    # Category Breakdown
    report.append("## Results by Category\n")
    categories = {}
    for r in results['questions']:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0}
        categories[cat]['total'] += 1
        categories[cat][r['status']] += 1

    report.append("| Category | Total | Passed | Failed | Errors | Pass Rate |\n")
    report.append("|----------|-------|--------|--------|--------|----------|\n")
    for cat, stats in sorted(categories.items()):
        pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        errors = stats.get('error', 0)  # Note: 'error' not 'errors'
        report.append(f"| {cat} | {stats['total']} | {passed} | {failed} | {errors} | {pass_rate:.1f}% |\n")

    report.append("\n---\n")

    # Recommendations
    report.append("## Recommendations\n")

    if summary['errors'] > 0:
        report.append("1. **Fix Connection Errors** - Some questions failed to reach the chat agent\n")

    if summary['average_similarity'] < 0.5:
        report.append("2. **Integrate Database Querying** - Agent responses have low similarity to approved answers\n")
        report.append("   - Current agent uses generic Claude responses\n")
        report.append("   - Need to query l311_approved_questions table and return validated answers\n")

    if summary['failed'] > 0:
        report.append("3. **Review Failed Questions** - See detailed failures above\n")
        report.append("   - Ensure responses contain contact info (311, louisvilleky.gov)\n")
        report.append("   - Ensure how-to questions include procedural steps\n")
        report.append("   - Ensure key service names and keywords are mentioned\n")

    report.append("\n---\n")
    report.append(f"\n*Report generated by test_approved_questions.py on {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}*\n")

    # Write report
    with open(REPORT_PATH, 'w') as f:
        f.writelines(report)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    try:
        results = run_validation_tests()

        # Exit with appropriate code
        if results['summary']['errors'] > 0 or results['summary']['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
