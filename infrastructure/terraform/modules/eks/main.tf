# EKS Cluster + Node Group module.
# Cluster was pre-created by the training environment with Auto Mode enabled.
# We are importing and managing it — not recreating it.
# bootstrap_self_managed_addons must be false to match existing cluster state (immutable field).
# Node group subnets are hardcoded to match existing state and avoid forced replacement.

data "aws_iam_role" "node_role" {
  name = var.node_role_name
}

data "aws_iam_role" "cluster_role" {
  name = "AmazonEKSAutoClusterRole"
}

# EKS Control Plane
resource "aws_eks_cluster" "this" {
  name                          = var.cluster_name
  role_arn                      = data.aws_iam_role.cluster_role.arn
  bootstrap_self_managed_addons = false

  # Preserve existing control plane logging config
  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler",
  ]

  vpc_config {
    subnet_ids = [
      "subnet-0562536a500d0b1a9",
      "subnet-07f0e589d30aa953c",
      "subnet-0db3302bd33eda479",
      "subnet-002827af9379deb64",
      "subnet-0256a890a183bdf5a",
    ]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  compute_config {
    enabled       = true
    node_pools    = ["general-purpose", "system"]
    node_role_arn = "arn:aws:iam::388691194728:role/AmazonEKSAutoNodeRole"
  }

  kubernetes_network_config {
    elastic_load_balancing {
      enabled = true
    }
  }

  storage_config {
    block_storage {
      enabled = true
    }
  }

  zonal_shift_config {
    enabled = true
  }

  tags = {
    Name        = "cams-${var.cluster_name}"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

# EKS Managed Node Group
# Subnets hardcoded to match existing node group — avoids forced replacement.
resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "student-nodes"
  node_role_arn   = data.aws_iam_role.node_role.arn
  instance_types  = [var.node_instance_type]

  subnet_ids = [
    "subnet-0562536a500d0b1a9",
    "subnet-07f0e589d30aa953c",
    "subnet-0db3302bd33eda479",
    "subnet-002827af9379deb64",
    "subnet-0256a890a183bdf5a",
  ]

  scaling_config {
    desired_size = var.desired_node_count
    min_size     = 2
    max_size     = 4
  }

  update_config {
    max_unavailable = 1
  }

  tags = {
    Name        = "cams-${var.cluster_name}-nodes"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
