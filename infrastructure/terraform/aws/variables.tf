variable "aws_region" {
  type        = string
  description = "AWS region."
  default     = "us-east-1"
}

variable "cluster_name" {
  type        = string
  description = "EKS cluster name."
  default     = "promptguard"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR."
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  type        = list(string)
  description = "Private subnet CIDRs."
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnets" {
  type        = list(string)
  description = "Public subnet CIDRs."
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "node_groups" {
  type        = map(any)
  description = "EKS node groups."
  default     = {}
}

variable "db_name" {
  type        = string
  description = "RDS database name."
  default     = "promptguard"
}

variable "db_username" {
  type        = string
  description = "RDS username."
  default     = "promptguard"
}

variable "db_password" {
  type        = string
  description = "RDS password."
  default     = "promptguard"
}
