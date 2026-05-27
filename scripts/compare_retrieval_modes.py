import argparse
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
    run_retrieval_eval,
)
from app.rag.pgvector_store import (  # noqa: E402
    initialize_schema,
    ingest_documents_to_pgvector,
    search_pgvector,
)


def summarize_pgvector(provider: str) -> dict[str, object]:
    with connect() as connection:
        initialize_schema(connection)
        ingest_documents_to_pgvector(connection, embedding_provider=provider)
        cases = [case for case in load_eval_cases() if case.expected_documents]
        hit_at_1_count = 0
        hit_at_3_count = 0
        reciprocal_rank_total = 0.0

        for case in cases:
            results = search_pgvector(connection, case.query, limit=3, embedding_provider=provider)
            retrieved_documents = [result_document_name(result) for result in results]
            hit_at_1_count += int(hit_at_k(case.expected_documents, retrieved_documents, 1))
            hit_at_3_count += int(hit_at_k(case.expected_documents, retrieved_documents, 3))
            reciprocal_rank_total += reciprocal_rank(case.expected_documents, retrieved_documents)

    total_cases = len(cases)
    return {
        "hit_at_1": hit_at_1_count / total_cases if total_cases else 0.0,
        "hit_at_3": hit_at_3_count / total_cases if total_cases else 0.0,
        "mean_reciprocal_rank": reciprocal_rank_total / total_cases if total_cases else 0.0,
    }


def print_row(mode: str, metrics: dict[str, object] | None, status: str = "available") -> None:
    if metrics is None:
        print(f"{mode:28} {status:12} {'-':>7} {'-':>7} {'-':>7}")
        return

    print(
        f"{mode:28} {status:12} "
        f"{float(metrics['hit_at_1']):7.3f} "
        f"{float(metrics['hit_at_3']):7.3f} "
        f"{float(metrics['mean_reciprocal_rank']):7.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare retrieval modes without acting as a gate.")
    parser.add_argument(
        "--include-openai",
        action="store_true",
        help="Include OpenAI pgvector retrieval when DATABASE_URL and OPENAI_API_KEY are set.",
    )
    args = parser.parse_args()

    print(f"{'mode':28} {'status':12} {'hit@1':>7} {'hit@3':>7} {'MRR':>7}")
    print("-" * 66)
    print_row("keyword", run_retrieval_eval(), status="baseline")

    if os.getenv("DATABASE_URL"):
        try:
            print_row("pgvector deterministic", summarize_pgvector("deterministic"))
        except Exception as error:
            print_row("pgvector deterministic", None, status=f"skipped: {type(error).__name__}")
    else:
        print_row("pgvector deterministic", None, status="skipped: no DB")

    if args.include_openai:
        if os.getenv("DATABASE_URL") and os.getenv("OPENAI_API_KEY"):
            try:
                os.environ["EMBEDDING_PROVIDER"] = "openai"
                os.environ.setdefault("OPENAI_EMBEDDING_DIMENSIONS", "16")
                print_row("pgvector openai", summarize_pgvector("openai"))
            except Exception as error:
                print_row("pgvector openai", None, status=f"skipped: {type(error).__name__}")
        else:
            print_row("pgvector openai", None, status="skipped: no key/db")


if __name__ == "__main__":
    main()
