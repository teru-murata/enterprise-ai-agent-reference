import json
from pathlib import Path


def main() -> None:
    eval_path = Path(__file__).resolve().parents[1] / "datasets" / "golden_eval_set.jsonl"

    print("Planned evaluation cases:")
    with eval_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            case = json.loads(line)
            sources = ", ".join(case["expected_sources"])
            print(f"- {case['id']} [{case['category']}] expects sources: {sources}")


if __name__ == "__main__":
    main()
