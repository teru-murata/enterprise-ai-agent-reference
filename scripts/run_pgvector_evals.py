import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_PATH = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.db.connection import connect  # noqa: E402
from app.evals.retrieval_eval import (  # noqa: E402
    hit_at_k,
    load_eval_cases,
    reciprocal_rank,
    result_document_name,
)
from app.rag.pgvector_store import (  # noqa: E402
    initialize_schema,
    ingest_documents_to_pgvector,
    search_pgvector,
)


HIT_AT_3_THRESHOLD = 0.75


def main() -> None:
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is required for pgvector retrieval evals")

    with connect() as connection:
        initialize_schema(connection)
        counts = ingest_documents_to_pgvector(connection)

        cases = [case for case in load_eval_cases() if case.expected_documents]
        per_case: list[dict[str, object]] = []
        hit_at_1_count = 0
        hit_at_3_count = 0
        reciprocal_rank_total = 0.0

        for case in cases:
            results = search_pgvector(connection, case.query, limit=3)
            retrieved_documents = [result_document_name(result) for result in results]
            case_hit_at_1 = hit_at_k(case.expected_documents, retrieved_documents, 1)
            case_hit_at_3 = hit_at_k(case.expected_documents, retrieved_documents, 3)
            case_reciprocal_rank = reciprocal_rank(case.expected_documents, retrieved_documents)

            hit_at_1_count += int(case_hit_at_1)
            hit_at_3_count += int(case_hit_at_3)
            reciprocal_rank_total += case_reciprocal_rank
            per_case.append(
                {
                    "id": case.case_id,
                    "category": case.category,
                    "query": case.query,
                    "expected_documents": case.expected_documents,
                    "retrieved_documents": retrieved_documents,
                    "hit_at_1": case_hit_at_1,
                    "hit_at_3": case_hit_at_3,
                    "reciprocal_rank": case_reciprocal_rank,
                }
            )

    total_cases = len(cases)
    hit_at_1 = hit_at_1_count / total_cases if total_cases else 0.0
    hit_at_3 = hit_at_3_count / total_cases if total_cases else 0.0
    mean_reciprocal_rank = reciprocal_rank_total / total_cases if total_cases else 0.0

    print("pgvector retrieval evaluation")
    print(f"- ingested documents: {counts['documents']}")
    print(f"- ingested chunks: {counts['chunks']}")
    print(f"- answerable cases: {total_cases}")
    print(f"- hit@1: {hit_at_1:.3f}")
    print(f"- hit@3: {hit_at_3:.3f}")
    print(f"- MRR: {mean_reciprocal_rank:.3f}")
    print()

    for case in per_case:
        status = "PASS" if case["hit_at_3"] else "FAIL"
        expected = ", ".join(case["expected_documents"])
        retrieved = ", ".join(case["retrieved_documents"]) or "none"
        print(f"- {status} {case['id']} [{case['category']}]")
        print(f"  query: {case['query']}")
        print(f"  expected: {expected}")
        print(f"  retrieved: {retrieved}")
        print(f"  reciprocal_rank: {float(case['reciprocal_rank']):.3f}")

    if hit_at_3 < HIT_AT_3_THRESHOLD:
        raise SystemExit(
            f"pgvector eval failed: hit@3 {hit_at_3:.3f} below {HIT_AT_3_THRESHOLD:.3f}"
        )


if __name__ == "__main__":
    main()
