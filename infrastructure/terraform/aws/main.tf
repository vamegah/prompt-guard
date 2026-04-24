terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "eks" {
  source = "./modules/eks"
  cluster_name    = var.cluster_name
  vpc_cidr        = var.vpc_cidr
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
  node_groups     = var.node_groups
}

module "rds" {
  source        = "./modules/rds"
  db_name       = var.db_name
  db_username   = var.db_username
  db_password   = var.db_password
  vpc_id        = module.eks.vpc_id
  subnet_ids    = module.eks.private_subnet_ids
}

module "redis" {
  source     = "./modules/redis"
  vpc_id     = module.eks.vpc_id
  subnet_ids = module.eks.private_subnet_ids
}

# Outputs for Kubernetes configuration
output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "eks_cluster_certificate_authority_data" {
  value = module.eks.cluster_certificate_authority_data
}