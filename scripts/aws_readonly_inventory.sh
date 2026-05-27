#!/usr/bin/env bash
set -euo pipefail

AWS_CLI_PATH="aws"
PROFILE=""
REGION=""
EXPECTED_ACCOUNT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --aws-cli-path)
      AWS_CLI_PATH="$2"
      shift 2
      ;;
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --expected-account-id)
      EXPECTED_ACCOUNT_ID="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$PROFILE" || -z "$REGION" || -z "$EXPECTED_ACCOUNT_ID" ]]; then
  echo "Usage: $0 --profile PROFILE --region REGION --expected-account-id ACCOUNT_ID [--aws-cli-path aws]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/aws_preflight.sh" \
  --aws-cli-path "$AWS_CLI_PATH" \
  --profile "$PROFILE" \
  --region "$REGION" \
  --expected-account-id "$EXPECTED_ACCOUNT_ID"

run_inventory() {
  local title="$1"
  shift
  echo
  echo "==> $title"
  if ! "$AWS_CLI_PATH" "$@"; then
    echo "Warning: $title failed. This may be expected if the selected role lacks read-only permission." >&2
  fi
}

echo
echo "Read-only AWS inventory"
echo "No create, update, delete, or secret-value commands are executed."

run_inventory "ECR repositories" \
  ecr describe-repositories --profile "$PROFILE" --region "$REGION" --output table

run_inventory "ECS clusters" \
  ecs list-clusters --profile "$PROFILE" --region "$REGION" --output table

run_inventory "RDS DB instances" \
  rds describe-db-instances --profile "$PROFILE" --region "$REGION" --output table

run_inventory "S3 buckets" \
  s3api list-buckets --profile "$PROFILE" --region "$REGION" --output table

run_inventory "Secrets Manager secret metadata" \
  secretsmanager list-secrets --profile "$PROFILE" --region "$REGION" --output table

run_inventory "CloudWatch log groups" \
  logs describe-log-groups --profile "$PROFILE" --region "$REGION" --output table
