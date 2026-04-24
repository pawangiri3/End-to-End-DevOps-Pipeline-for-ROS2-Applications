# Resource Groups
module "resource_groups" {
  source = "../../modules/resource_group"
  resource_groups = var.resource_groups
  tags = var.common_tags
}




# Networking
# module "networking" {
#   source = "../../modules/networking"
#   location            = var.location
#   resource_group_name = module.resource_groups.resource_groups["network"].name

#   virtual_networks = {
#     for vnet_key, vnet_config in var.virtual_networks : vnet_key => {
#       name                = "${var.environment}-${vnet_key}"
#       location            = var.location
#       resource_group_name = module.resource_groups.resource_groups["network"].name
#       address_space       = vnet_config.address_space
#       subnets             = vnet_config.subnets
#       tags                = var.common_tags
#     }
#   }

#   subnets = {
#     for pair in flatten([
#       for vnet_key, vnet in var.virtual_networks : [
#         for subnet_key, subnet in vnet.subnets : {
#           key = "${vnet_key}-${subnet_key}"
#           value = {
#             name                 = "${var.environment}-${vnet_key}-${subnet_key}"
#             resource_group_name  = module.resource_groups.resource_groups["network"].name
#             virtual_network_name = "${var.environment}-${vnet_key}"
#             address_prefixes     = subnet.address_prefixes
#           }
#         }
#       ]
#     ]) : pair.key => pair.value
#   }

#   network_security_groups = var.network_security_groups
#   tags                     = var.common_tags

#   depends_on = [module.resource_groups]
# }

# # Key Vault
# module "key_vault" {
#   source = "../../modules/key_vault"
#   key_vaults = var.key_vaults
#   tags = var.common_tags
# }



# # Log Analytics
# module "log_analytics" {
#   source = "../../modules/log_analytics"

#   log_analytics_workspaces = {
#     for la_key, la_config in var.log_analytics_workspaces : la_key => {
#       name                = la_config.name
#       location            = var.location
#       resource_group_name = module.resource_groups.resource_groups["monitoring"].name
#       sku                 = la_config.sku
#       retention_in_days   = la_config.retention_in_days
#       tags                = var.common_tags
#     }
#   }

#   tags = var.common_tags
# }

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

