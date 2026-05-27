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
    assert "terraform.tfvars.local" in gitignore
    assert "*.tfvars.local" in gitignore
    assert "*.auto.tfvars" in gitignore
    assert "*.auto.tfvars.json" in gitignore


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


def test_apply_readiness_controls_are_documented_and_configurable() -> None:
    ecs_variables = (REPO_ROOT / "infra/terraform/modules/ecs_service/variables.tf").read_text(
        encoding="utf-8"
    )
    ecs_main = (REPO_ROOT / "infra/terraform/modules/ecs_service/main.tf").read_text(
        encoding="utf-8"
    )
    rds_variables = (REPO_ROOT / "infra/terraform/modules/rds_pgvector/variables.tf").read_text(
        encoding="utf-8"
    )
    tfvars_example = (
        REPO_ROOT / "infra/terraform/envs/dev/terraform.tfvars.example"
    ).read_text(encoding="utf-8")
    docs = (REPO_ROOT / "docs/aws-deployment.md").read_text(encoding="utf-8").lower()

    assert "allowed_http_cidrs" in ecs_variables
    assert "cidr_blocks = var.allowed_http_cidrs" in ecs_main
    assert "ecs_assign_public_ip" in tfvars_example
    assert "203.0.113.10/32" in tfvars_example
    assert "deletion_protection" in rds_variables
    assert "skip_final_snapshot" in rds_variables
    assert "backup_retention_period" in rds_variables
    assert "alb exposure cidr" in docs
    assert "ecs public ip" in docs
    assert "0 to destroy" in docs


def test_iam_policy_avoids_broad_admin_and_scopes_runtime_permissions() -> None:
    ecs_main = (REPO_ROOT / "infra/terraform/modules/ecs_service/main.tf").read_text(
        encoding="utf-8"
    )

    assert "AdministratorAccess" not in ecs_main
    assert "var.ecr_repository_arn" in ecs_main
    assert "aws_cloudwatch_log_group.api.arn" in ecs_main
    assert "ecr:GetAuthorizationToken" in ecs_main


def test_no_terraform_state_files_are_tracked_or_present() -> None:
    state_files = [
        path
        for path in (REPO_ROOT / "infra" / "terraform").rglob("*")
        if ".terraform" not in path.parts
        if path.name.endswith(".tfstate") or ".tfstate." in path.name
    ]

    assert state_files == []
