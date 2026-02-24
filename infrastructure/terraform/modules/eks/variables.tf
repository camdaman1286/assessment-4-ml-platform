variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "node_instance_type" {
  description = "EC2 instance type for worker nodes"
  type        = string
}

variable "desired_node_count" {
  description = "Desired number of worker nodes"
  type        = number
}

variable "node_role_name" {
  description = "Name of the pre-existing IAM role for EKS nodes"
  type        = string
}
