from deepseek_harness import DeepSeekHarness
import os

cwd = os.getcwd()
print(f"Starting DeepSeek Harness in: {cwd}")

with DeepSeekHarness(
    dsh_home=os.path.join(cwd, "dsh_home"),
    cwd=cwd,
    provider="deepseek-official",
    model="deepseek-v4-flash"
) as harness:
    result = harness.run("Say 'Installation successful!' and nothing else.")
    print("\n--- RESULT ---")
    print(f"Finish reason: {result.finish_reason}")
    print(f"Response: {result.final_response!r}")
