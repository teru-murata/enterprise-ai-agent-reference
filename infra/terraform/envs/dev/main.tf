terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = "${var.app_name}-${var.environment}"
}

module "network" {
  source = "../../modules/network"

  app_name             = var.app_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

module "secrets" {
  source = "../../modules/secrets"

  app_name                   = var.app_name
  environment                = var.environment
  openai_api_key_secret_name = "${local.name_prefix}/openai-api-key"
  database_url_secret_name   = "${local.name_prefix}/database-url"
}

module "documents" {
  source = "../../modules/s3_documents"

  app_name          = var.app_name
  environment       = var.environment
  bucket_name       = var.documents_bucket_name
  enable_versioning = true
}

module "ecr" {
  source = "../../modules/ecr"

  app_name        = var.app_name
  environment     = var.environment
  repository_name = var.ecr_repository_name
  scan_on_push    = true
}

module "api_service" {
  source = "../../modules/ecs_service"

  app_name                  = var.app_name
  environment               = var.environment
  aws_region                = var.aws_region
  vpc_id                    = module.network.vpc_id
  subnet_ids                = module.network.public_subnet_ids
  image_uri                 = var.api_image_uri
  desired_count             = var.api_desired_count
  embedding_provider        = var.embedding_provider
  answer_provider           = var.answer_provider
  database_url_secret_arn   = module.secrets.database_url_secret_arn
  openai_api_key_secret_arn = module.secrets.openai_api_key_secret_arn
  documents_bucket_arn      = module.documents.bucket_arn
  assign_public_ip          = true
}

module "database" {
  source = "../../modules/rds_pgvector"

  app_name              = var.app_name
  environment           = var.environment
  vpc_id                = module.network.vpc_id
  private_subnet_ids    = module.network.private_subnet_ids
  app_security_group_id = module.api_service.service_security_group_id
  db_name               = var.db_name
  db_username           = var.db_username
  db_instance_class     = var.db_instance_class
  allocated_storage_gb  = var.db_allocated_storage_gb
  engine_version        = var.postgres_engine_version
}

module "observability" {
  source = "../../modules/observability"

  app_name             = var.app_name
  environment          = var.environment
  log_retention_days   = var.log_retention_days
  create_dashboard     = false
}
