from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_aws_deploy_workflow_is_manual_only() -> None:
    workflow = REPO_ROOT / ".github" / "workflows" / "aws-deploy.yml"
    text = workflow.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "pull_request:" not in text
    assert "\npush:" not in text
    assert "configure-aws-credentials" in text
    assert "id-token: write" in text
    assert "AWS_ACCESS_KEY_ID" not in text
    assert "AWS_SECRET_ACCESS_KEY" not in text
    assert "default: false" in text
    assert "terraform apply" in text
    assert "if: ${{ inputs.apply == true }}" in text


def test_terraform_skeleton_files_exist() -> None:
    required_paths = [
        "infra/terraform/README.md",
        "infra/terraform/modules/network/main.tf",
        "infra/terraform/modules/ecr/main.tf",
        "infra/terraform/modules/ecs_service/main.tf",
        "infra/terraform/modules/rds_pgvector/main.tf",
        "infra/terraform/modules/s3_documents/main.tf",
        "infra/terraform/modules/secrets/main.tf",
        "infra/terraform/modules/observability/main.tf",
        "infra/terraform/envs/dev/backend.tf.example",
        "infra/terraform/envs/dev/terraform.tfvars.example",
    ]

    for path in required_paths:
        assert (REPO_ROOT / path).exists(), path


def test_local_aws_config_example_exists_and_real_config_is_ignored() -> None:
    example = REPO_ROOT / ".local" / "aws-dev.example.json"
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert example.exists()
    assert '"expectedAccountId": "123456789012"' in example.read_text(encoding="utf-8")
    assert ".local/*.json" in gitignore
    assert "!.local/*.example.json" in gitignore


def test_terraform_examples_do_not_contain_obvious_secrets_or_real_arns() -> None:
    infra_files = list((REPO_ROOT / "infra" / "terraform").rglob("*"))
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in infra_files
        if path.is_file() and path.suffix in {".tf", ".example", ".md"}
    )

    forbidden = [
        "AKIA",
        "BEGIN PRIVATE KEY",
        "BEGIN RSA PRIVATE KEY",
        "OPENAI_API_KEY=",
        "aws_secret_access_key",
        "AdministratorAccess",
        "arn:aws:",
    ]

    for value in forbidden:
        assert value not in text


def test_no_terraform_state_files_are_tracked_or_present() -> None:
    state_files = [
        path
        for path in (REPO_ROOT / "infra" / "terraform").rglob("*")
        if ".terraform" not in path.parts
        if path.name.endswith(".tfstate") or ".tfstate." in path.name
    ]

    assert state_files == []
