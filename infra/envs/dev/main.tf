# Resource Groups
module "resource_groups" {
  source = "../../modules/resource_group"

  resource_groups = var.resource_groups
  tags             = var.common_tags
}

# Networking
module "networking" {
  source = "../../modules/networking"

  location            = var.location
  resource_group_name = module.resource_groups.resource_groups["core"].name

  virtual_networks = {
    for vnet_key, vnet_config in var.virtual_networks : vnet_key => {
      name                = "${var.environment}-${vnet_key}"
      location            = var.location
      resource_group_name = module.resource_groups.resource_groups["core"].name
      address_space       = vnet_config.address_space
      subnets             = vnet_config.subnets
      tags                = var.common_tags
    }
  }

  network_security_groups = var.network_security_groups
  tags                     = var.common_tags

  depends_on = [module.resource_groups]
}

# Key Vault
module "key_vault" {
  source = "../../modules/key_vault"

  key_vaults = {
    for kv_key, kv_config in var.key_vaults : kv_key => {
      name                = kv_config.name
      location            = var.location
      resource_group_name = module.resource_groups.resource_groups["security"].name
      sku_name            = kv_config.sku_name
      tags                = var.common_tags
    }
  }

  tags = var.common_tags
}

# Log Analytics
module "log_analytics" {
  source = "../../modules/log_analytics"

  log_analytics_workspaces = {
    for la_key, la_config in var.log_analytics_workspaces : la_key => {
      name                = la_config.name
      location            = var.location
      resource_group_name = module.resource_groups.resource_groups["monitoring"].name
      sku                 = la_config.sku
      retention_in_days   = la_config.retention_in_days
      tags                = var.common_tags
    }
  }

  tags = var.common_tags
}

# Container Registry
module "acr" {
  source = "../../modules/acr"

  container_registries = {
    for acr_key, acr_config in var.container_registries : acr_key => {
      name                = acr_config.name
      location            = var.location
      resource_group_name = module.resource_groups.resource_groups["compute"].name
      sku                 = acr_config.sku
      admin_enabled       = acr_config.admin_enabled
      tags                = var.common_tags
    }
  }

  tags = var.common_tags
}

# AKS Clusters
module "aks" {
  source = "../../modules/aks"

  kubernetes_clusters = {
    for aks_key, aks_config in var.kubernetes_clusters : aks_key => {
      name                = aks_config.name
      location            = var.location
      resource_group_name = module.resource_groups.resource_groups["compute"].name
      dns_prefix          = "${var.environment}-${aks_key}"
      kubernetes_version  = aks_config.kubernetes_version
      default_node_pool = {
        name                = "default"
        node_count          = aks_config.node_count
        vm_size            = aks_config.vm_size
        os_disk_size_gb    = 128
        os_disk_type       = "Managed"
        enable_auto_scaling = false
        max_pods           = 110
        node_labels        = {}
        node_taints        = []
      }
      tags = var.common_tags
    }
  }

  tags = var.common_tags
}
