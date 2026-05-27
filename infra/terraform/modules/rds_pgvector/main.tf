locals {
  name_prefix = "${var.app_name}-${var.environment}"
}

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Allow PostgreSQL access from the ECS service only."
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from ECS service"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  egress {
    description = "Allow outbound responses"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name_prefix}-db-sg"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${local.name_prefix}-db-subnets"
    Environment = var.environment
  }
}

resource "aws_db_parameter_group" "this" {
  name   = "${local.name_prefix}-postgres-params"
  family = "postgres16"

  tags = {
    Name        = "${local.name_prefix}-postgres-params"
    Environment = var.environment
  }
}

resource "aws_db_instance" "this" {
  identifier                  = "${local.name_prefix}-postgres"
  engine                      = "postgres"
  engine_version              = var.engine_version
  instance_class              = var.db_instance_class
  allocated_storage           = var.allocated_storage_gb
  db_name                     = var.db_name
  username                    = var.db_username
  manage_master_user_password = true
  db_subnet_group_name        = aws_db_subnet_group.this.name
  vpc_security_group_ids      = [aws_security_group.db.id]
  parameter_group_name        = aws_db_parameter_group.this.name
  publicly_accessible         = false
  storage_encrypted           = true
  skip_final_snapshot         = true
  deletion_protection         = false

  tags = {
    Name        = "${local.name_prefix}-postgres"
    Environment = var.environment
    DataClass    = "synthetic"
  }
}

# Enable pgvector after database creation using a controlled migration path:
# CREATE EXTENSION IF NOT EXISTS vector;
# Do not store database passwords in Terraform variables or tfvars files.
