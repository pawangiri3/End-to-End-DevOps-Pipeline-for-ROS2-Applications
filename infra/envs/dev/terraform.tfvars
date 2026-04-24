environment = "dev"
location    = "East US 2"
project     = "rudra"

common_tags = {
  Environment = "dev"
  Project     = "rudra-lz"
  ManagedBy   = "Terraform"
  CreatedDate = "2026-04-24"
}

# Resource Groups - one for each resource type
resource_groups = {
  core = {
    name     = "rg-dev-core-rudra"
    location = "East US 2"
  }
  network = {
    name     = "rg-dev-network-rudra"
    location = "East US 2"
  }
  security = {
    name     = "rg-dev-security-rudra"
    location = "East US 2"
  }
  compute = {
    name     = "rg-dev-compute-rudra"
    location = "East US 2"
  }
  monitoring = {
    name     = "rg-dev-monitoring-rudra"
    location = "East US 2"
  }
}

# Virtual Networks
virtual_networks = {
  hub = {
    address_space = ["10.0.0.0/16"]
    subnets = {
      gateway = {
        address_prefixes = ["10.0.0.0/24"]
      }
      management = {
        address_prefixes = ["10.0.1.0/24"]
      }
    }
  }
  spoke_app = {
    address_space = ["10.1.0.0/16"]
    subnets = {
      aks = {
        address_prefixes = ["10.1.0.0/22"]
      }
      appgw = {
        address_prefixes = ["10.1.4.0/24"]
      }
    }
  }
}

# Network Security Groups
network_security_groups = {
  nsg_app = {
    rules = [
      {
        name                       = "Allow-K8s-API"
        priority                   = 100
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "443"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
      }
    ]
  }
}

# Key Vaults
# key_vaults = {
#   kv = {
#     name                      = "rudradevkv001"
#     location                  = "East US 2"
#     resource_group_name       = "rg-dev-security-rudra"
#     sku_name                  = "standard"
    
#     enable_rbac_authorization = true
#   }
# }


# Log Analytics
# log_analytics_workspaces = {
#   monitoring = {
#     name              = "rudradevlaw001"
#     location          = "East US 2"
#     resource_group_name = "rg-dev-monitoring-rudra"
#     sku               = "PerGB2018"
#     retention_in_days = 30
#   }
# }

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



