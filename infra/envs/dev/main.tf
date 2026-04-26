# Resource Groups
module "resource_groups" {
  source = "../../modules/resource_group"
  resource_groups = var.resource_groups
  tags = var.common_tags
}

# Container Registry
module "acr" {
  source = "../../modules/acr"
  container_registries = var.container_registries
  tags = var.common_tags
  depends_on = [ module.resource_groups ]
}

# AKS Clusters
module "aks" {
  source = "../../modules/aks"
  kubernetes_clusters = var.kubernetes_clusters
  tags = var.common_tags
  depends_on = [ module.resource_groups ]
}

