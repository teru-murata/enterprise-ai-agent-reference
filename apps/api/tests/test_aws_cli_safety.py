from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def read_repo_file(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_aws_cli_safety_scripts_exist() -> None:
    required = [
        "scripts/aws_preflight.ps1",
        "scripts/aws_preflight.sh",
        "scripts/aws_preflight_from_config.ps1",
        "scripts/aws_readonly_inventory.ps1",
        "scripts/aws_readonly_inventory.sh",
        "scripts/aws_readonly_inventory_from_config.ps1",
        "docs/aws-cli-operations.md",
    ]

    for path in required:
        assert (REPO_ROOT / path).exists(), path


def test_preflight_requires_profile_region_and_expected_account() -> None:
    powershell = read_repo_file("scripts/aws_preflight.ps1")
    bash = read_repo_file("scripts/aws_preflight.sh")

    assert "Profile" in powershell
    assert "Region" in powershell
    assert "ExpectedAccountId" in powershell
    assert "--profile" in bash
    assert "--region" in bash
    assert "--expected-account-id" in bash
    assert "get-caller-identity" in powershell
    assert "get-caller-identity" in bash


def test_inventory_scripts_do_not_call_secret_values_or_mutating_commands() -> None:
    script_text = "\n".join(
        [
            read_repo_file("scripts/aws_preflight.ps1"),
            read_repo_file("scripts/aws_preflight.sh"),
            read_repo_file("scripts/aws_readonly_inventory.ps1"),
            read_repo_file("scripts/aws_readonly_inventory.sh"),
        ]
    ).lower()

    forbidden_fragments = [
        "get-secret-value",
        "terraform apply",
        "terraform destroy",
        "aws delete-",
        "aws s3 rm",
        "aws s3 rb",
        "aws rds delete-",
        "aws ecs delete-",
        "iam attach-",
        "iam put-",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in script_text


def test_docs_warn_apply_destroy_are_forbidden_by_default() -> None:
    docs = read_repo_file("docs/aws-cli-operations.md").lower()

    assert "terraform apply" in docs
    assert "terraform destroy" in docs
    assert "forbidden unless explicitly approved" in docs
    assert "get-secret-value" in docs
    assert "github actions should use oidc" in docs


def test_readme_uses_placeholder_account_id() -> None:
    readme = read_repo_file("README.md")

    assert "ExpectedAccountId 123456789012" in readme
    assert "enterprise-ai-agent-dev" in readme
