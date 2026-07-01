# tests/test_api.py

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# ── Helpers ────────────────────────────────────────────────────

def print_header(title):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)

def print_result(test_name, passed, detail=""):
    status = "PASS ✓" if passed else "FAIL ✗"
    color  = "\033[92m" if passed else "\033[91m"  # green / red
    reset  = "\033[0m"
    print(f"  {color}{status}{reset}  {test_name}")
    if detail:
        print(f"         → {detail}")

# ── Tests ──────────────────────────────────────────────────────

def test_root():
    """Test that the root endpoint responds."""
    print_header("Test 1 — Root endpoint GET /")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        passed = response.status_code == 200
        print_result(
            "Root returns 200 OK",
            passed,
            f"Status: {response.status_code}"
        )
        print_result(
            "Response contains message",
            "message" in response.json(),
            f"Body: {response.json()}"
        )
    except requests.exceptions.ConnectionError:
        print_result("Root endpoint reachable", False, "Backend is not running")


def test_health():
    """Test that /health returns status ok with expected fields."""
    print_header("Test 2 — Health check GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()

        print_result(
            "Health returns 200 OK",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        print_result(
            "Status field is 'ok'",
            data.get("status") == "ok",
            f"status: {data.get('status')}"
        )
        print_result(
            "Timestamp field present",
            "timestamp" in data,
            f"timestamp: {data.get('timestamp')}"
        )
        print_result(
            "Model field present",
            "model" in data,
            f"model: {data.get('model')}"
        )
    except requests.exceptions.ConnectionError:
        print_result("Health endpoint reachable", False, "Backend is not running")


def test_ask_valid_question():
    """Test that /ask returns an answer for a valid question."""
    print_header("Test 3 — Valid question POST /ask")
    question = "How do I register for courses?"
    try:
        print(f"  Sending question: '{question}'")
        print("  Waiting for LLM response (this may take a few seconds)...")

        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            timeout=60  # LLM can take a while
        )
        data = response.json()

        print_result(
            "Ask returns 200 OK",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        print_result(
            "Response contains question field",
            "question" in data,
            f"question: {data.get('question')}"
        )
        print_result(
            "Response contains answer field",
            "answer" in data,
            f"answer (first 80 chars): {str(data.get('answer', ''))[:80]}..."
        )
        print_result(
            "Answer is not empty",
            len(data.get("answer", "")) > 0,
            f"Answer length: {len(data.get('answer', ''))} characters"
        )
        print_result(
            "Timestamp field present",
            "timestamp" in data,
            f"timestamp: {data.get('timestamp')}"
        )

    except requests.exceptions.ConnectionError:
        print_result("Ask endpoint reachable", False, "Backend is not running")
    except requests.exceptions.Timeout:
        print_result("LLM responded in time", False, "Request timed out after 60s")


def test_ask_empty_question():
    """Test that /ask rejects an empty question with 400 error."""
    print_header("Test 4 — Empty question handling POST /ask")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": ""},
            timeout=5
        )
        data = response.json()

        print_result(
            "Empty question returns 400",
            response.status_code == 400,
            f"Status: {response.status_code}"
        )
        print_result(
            "Error detail message present",
            "detail" in data,
            f"detail: {data.get('detail')}"
        )

    except requests.exceptions.ConnectionError:
        print_result("Ask endpoint reachable", False, "Backend is not running")


def test_ask_whitespace_question():
    """Test that /ask rejects a whitespace-only question."""
    print_header("Test 5 — Whitespace-only question POST /ask")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": "     "},
            timeout=5
        )
        print_result(
            "Whitespace question returns 400",
            response.status_code == 400,
            f"Status: {response.status_code}"
        )

    except requests.exceptions.ConnectionError:
        print_result("Ask endpoint reachable", False, "Backend is not running")


# ── Summary ────────────────────────────────────────────────────

def run_all_tests():
    print("\n")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     IS365 — Student Support Assistant API Tests       ║")
    print(f"║     Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                     ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print(f"\n  Target: {BASE_URL}")

    test_root()
    test_health()
    test_ask_valid_question()
    test_ask_empty_question()
    test_ask_whitespace_question()

    print("\n" + "=" * 55)
    print("  All tests completed.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    run_all_tests()