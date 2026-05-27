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

echo "AWS CLI preflight"
echo "Profile: $PROFILE"
echo "Region: $REGION"
echo "Expected account id: $EXPECTED_ACCOUNT_ID"

echo
echo "AWS CLI version:"
"$AWS_CLI_PATH" --version

echo
echo "AWS CLI configure list:"
if ! "$AWS_CLI_PATH" configure list --profile "$PROFILE"; then
  echo "Warning: aws configure list failed for the selected profile. Continuing to caller identity check." >&2
fi

ACCOUNT="$("$AWS_CLI_PATH" sts get-caller-identity \
  --profile "$PROFILE" \
  --region "$REGION" \
  --query Account \
  --output text)"

CALLER_ARN="$("$AWS_CLI_PATH" sts get-caller-identity \
  --profile "$PROFILE" \
  --region "$REGION" \
  --query Arn \
  --output text)"

if [[ "$ACCOUNT" != "$EXPECTED_ACCOUNT_ID" ]]; then
  echo "AWS account mismatch. Expected $EXPECTED_ACCOUNT_ID but caller identity returned $ACCOUNT." >&2
  exit 1
fi

echo
echo "Preflight passed."
echo "Safe AWS caller metadata:"
echo "- profile: $PROFILE"
echo "- region: $REGION"
echo "- account_id: $ACCOUNT"
echo "- caller_arn: $CALLER_ARN"
