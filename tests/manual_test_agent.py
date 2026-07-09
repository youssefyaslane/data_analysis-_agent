import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent.analysis_agent import run_analysis

result = run_analysis("uploads/sales.csv")
print("=== REPORT ===")
print(result["report"])
print()
print("=== PLOT URL ===")
print(result["plot_url"])
