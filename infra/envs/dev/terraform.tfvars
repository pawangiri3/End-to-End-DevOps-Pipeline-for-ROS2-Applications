environment = "dev"
location    = "East US 2"
project     = "rudra"

common_tags = {
  Environment = "dev"
  Project     = "rudra-lz"
  ManagedBy   = "Terraform"
  CreatedDate = "2026-04-24"
}

# Resource Groups - one for compute
resource_groups = {
  compute = {
    name     = "rg-dev-compute-rudra"
    location = "East US 2"
  }
}

# Container Registry
container_registries = {
  acr = {
    name          = "rudradevacr"
    location      = "East US 2"
    resource_group_name = "rg-dev-compute-rudra"
    sku           = "Premium"
    admin_enabled = false
  }
}

# AKS Clusters
kubernetes_clusters = {
  primary = {
    name                = "aks-dev-rudra"
    location            = "East US 2"
    resource_group_name = "rg-dev-compute-rudra"
    dns_prefix          = "aks-dev-rudra"
    kubernetes_version  = "1.34.4"
    default_node_pool = {
      name            = "default"
      node_count      = 1
      vm_size         = "Standard_D2ads_v6"
      os_disk_size_gb = 128
    }
  }
}



