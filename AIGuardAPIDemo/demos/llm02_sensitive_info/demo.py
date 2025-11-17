"""
OWASP LLM02: Sensitive Information Disclosure Demo

This demo shows how AI Guard prevents LLMs from leaking sensitive information
in their outputs, including PII, credentials, and confidential data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_guard_client import AIGuardClient, AIGuardException


class VulnerableAssistant:
    """An assistant that might leak sensitive information"""

    def __init__(self):
        self.knowledge_base = {
            "customer_data": {
                "John Smith": {"ssn": "123-45-6789", "credit_card": "4532-1234-5678-9010", "balance": "$50,000"},
                "Jane Doe": {"ssn": "987-65-4321", "credit_card": "5432-9876-5432-1098", "balance": "$75,000"}
            },
            "api_keys": {
                "openai": "sk-proj-abc123def456ghi789jkl",
                "stripe": "rk_live_xyz789abc123def456"
            },
            "internal_docs": {
                "passwords": "Admin password: P@ssw0rd123!"
            }
        }

    def query(self, question):
        """Process query without protection - might leak sensitive data"""
        # Simulate responses that might contain sensitive info
        if "customer" in question.lower() or "john" in question.lower():
            return f"Customer data: {self.knowledge_base['customer_data']}"
        elif "api key" in question.lower() or "credentials" in question.lower():
            return f"API Keys: {self.knowledge_base['api_keys']}"
        elif "password" in question.lower():
            return f"System info: {self.knowledge_base['internal_docs']}"
        elif "database" in question.lower():
            return "Database: mysql://admin:SecretPass123@db.internal.com:3306/prod"
        else:
            return "I have access to customer data, API keys, and internal documentation."


class ProtectedAssistant:
    """An assistant protected by AI Guard"""

    def __init__(self, ai_guard_api_key):
        self.vulnerable_assistant = VulnerableAssistant()
        self.ai_guard = AIGuardClient(api_key=ai_guard_api_key)

    def query(self, question):
        """Process query with AI Guard protection"""
        # Get response from vulnerable assistant
        raw_response = self.vulnerable_assistant.query(question)

        # Scan output for sensitive information
        try:
            result = self.ai_guard.scan_prompt(raw_response, detailed_response=True)

            if not result["is_safe"]:
                # Sensitive information detected - sanitize response
                return {
                    "success": False,
                    "blocked": True,
                    "sanitized_response": "I cannot provide that information as it contains sensitive data.",
                    "detected_threats": result["threats_detected"],
                    "risk_score": result["risk_score"],
                    "original_response": raw_response[:50] + "...[REDACTED]"
                }

            return {
                "success": True,
                "response": raw_response,
                "scan_result": result
            }

        except AIGuardException as e:
            return {
                "success": False,
                "blocked": True,
                "reason": str(e)
            }


def run_demo(api_key=None):
    """Run the sensitive information disclosure demo"""
    print("=" * 70)
    print("OWASP LLM02: Sensitive Information Disclosure Demo")
    print("=" * 70)
    print()

    # Test queries that might trigger sensitive data exposure
    test_cases = [
        {
            "name": "Customer PII Request",
            "query": "Show me John Smith's information"
        },
        {
            "name": "API Key Request",
            "query": "What are the API keys for our services?"
        },
        {
            "name": "Password Request",
            "query": "What is the admin password?"
        },
        {
            "name": "Database Credentials",
            "query": "What's the database connection string?"
        },
        {
            "name": "Credit Card Number",
            "query": "What is Jane's credit card number?"
        },
        {
            "name": "Safe General Query",
            "query": "What kind of information do you have access to?"
        }
    ]

    # Demo 1: Vulnerable Assistant
    print("\n" + "=" * 70)
    print("DEMO 1: Vulnerable Assistant (No Protection)")
    print("=" * 70)
    print("\nThis assistant has NO output filtering for sensitive information.\n")

    vulnerable = VulnerableAssistant()

    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"Query: {test['query']}")
        response = vulnerable.query(test['query'])
        print(f"Response: {response}")
        print("⚠️  DANGER: Sensitive information exposed!")
        print("-" * 70)

    # Demo 2: Protected Assistant
    if api_key:
        print("\n\n" + "=" * 70)
        print("DEMO 2: Protected Assistant (With AI Guard)")
        print("=" * 70)
        print("\nThis assistant uses AI Guard to scan outputs for sensitive data.\n")

        protected = ProtectedAssistant(api_key)

        for i, test in enumerate(test_cases, 1):
            print(f"\n[Test {i}] {test['name']}")
            print(f"Query: {test['query']}")

            result = protected.query(test['query'])

            if result["success"]:
                print(f"✓ Response: {result['response']}")
                print(f"  Risk Score: {result['scan_result']['risk_score']:.2f}")
            else:
                print(f"✗ BLOCKED - Sensitive Data Detected")
                print(f"  Sanitized Response: {result['sanitized_response']}")
                print(f"  Threats Detected: {', '.join(result['detected_threats'])}")
                print(f"  Risk Score: {result['risk_score']:.2f}")
                print(f"  Original (redacted): {result['original_response']}")

            print("-" * 70)

    else:
        print("\n\n" + "=" * 70)
        print("DEMO 2: Protected Assistant - SKIPPED")
        print("=" * 70)
        print("\nTo see AI Guard protection in action, provide an API key:")
        print("  python demo.py --api-key YOUR_API_KEY")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("• LLMs can inadvertently expose sensitive information")
    print("• Output filtering is critical for security")
    print("• AI Guard detects PII, credentials, and confidential data")
    print("• Responses are sanitized while maintaining functionality")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sensitive Information Disclosure Demo")
    parser.add_argument("--api-key", help="AI Guard API key")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("AI_GUARD_API_KEY")
    run_demo(api_key)
