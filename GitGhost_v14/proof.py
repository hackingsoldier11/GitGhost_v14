from gitghost_core_v14 import analyze_content

test_secret = 'AKIAIOSFODNN7EXAMPLE'
print(f"Testing Secret: {test_secret}")

severity, reason, entropy, score, vector, is_fp = analyze_content(test_secret, "test.txt")

print(f"Severity: {severity}")
print(f"Reason: {reason}")
print(f"Score: {score}")
print(f"Is False Positive: {is_fp}")

if severity == "CRITICAL":
    print("\n✅ PROOF: The engine successfully detected the AWS Critical Secret!")
else:
    print("\n❌ PROOF FAILED: The engine did not detect the secret.")
