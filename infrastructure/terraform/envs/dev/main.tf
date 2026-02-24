terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "cams-tf-state-assessment-4"
    key            = "assessment-4/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "cams-tf-lock-assessment-4"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

module "eks" {
  source             = "../../modules/eks"
  cluster_name       = var.cluster_name
  aws_region         = var.aws_region
  node_instance_type = var.node_instance_type
  desired_node_count = var.desired_node_count
  node_role_name     = var.node_role_name
}
