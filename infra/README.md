# Azure Landing Zone with Terraform

This repository contains a scalable Azure landing zone implementation using modern Terraform patterns with `for_each` and nested maps.

## Architecture

The landing zone implements a hub-and-spoke network topology with the following components:

- **Resource Groups**: Organized resource management
- **Networking**: Hub-and-spoke VNet architecture with NSGs
- **Security**: Key Vault for secrets management
- **Compute**: AKS clusters with multiple node pools
- **Container Registry**: ACR for container images
- **Monitoring**: Log Analytics workspaces
- **Identity**: Managed identities for secure access

## Structure

```
infra/
├── global/
│   ├── backend/          # Terraform backend configuration
│   └── naming/           # Global naming conventions
├── modules/              # Reusable Terraform modules
│   ├── resource_group/
│   ├── networking/
│   ├── key_vault/
│   ├── aks/
│   ├── acr/
│   └── log_analytics/
├── envs/                 # Environment-specific configurations
│   ├── dev/
│   ├── staging/
│   └── prod/
├── versions.tf           # Terraform and provider versions
├── provider.tf           # Azure provider configuration
├── variables.tf          # Root variables
└── outputs.tf            # Root outputs
```

## Key Features

### Scalable Configuration
- Uses nested maps for easy scaling
- `for_each` loops for resource creation
- Environment-specific configurations
- Modular architecture

### Modern Terraform Patterns
- Terraform 1.5+ compatibility
- AzureRM provider 3.74+
- Proper resource dependencies
- Sensitive data handling

### Security Best Practices
- Network security groups
- Key Vault integration
- Managed identities
- RBAC support

## Usage

### Prerequisites

1. Azure CLI installed and authenticated
2. Terraform 1.5+ installed
3. Azure subscription with appropriate permissions

### Deployment

1. **Initialize Terraform** (run from environment directory):
   ```bash
   cd envs/dev
   terraform init
   ```

2. **Plan deployment**:
   ```bash
   terraform plan -var-file=terraform.tfvars
   ```

3. **Apply configuration**:
   ```bash
   terraform apply -var-file=terraform.tfvars
   ```

### Configuration Structure

The landing zone uses a comprehensive nested map structure:

```hcl
landing_zone_config = {
  location = "East US 2"

  networking = {
    hub = {
      address_space = ["10.0.0.0/16"]
      subnets = {
        gateway = {
          address_prefixes = ["10.0.0.0/24"]
          nsg_rules = [...]
        }
      }
    }
    spokes = {
      app = {
        address_space = ["10.1.0.0/16"]
        subnets = {...}
      }
    }
  }

  security = {
    key_vaults = {
      main = {
        name = "kv-dev-lz"
        sku_name = "standard"
      }
    }
  }

  compute = {
    aks_clusters = {
      main = {
        name = "aks-dev"
        node_pools = {
          default = {
            node_count = 1
            vm_size = "Standard_DS2_v2"
          }
        }
      }
    }
    container_registries = {
      main = {
        name = "acrdev"
        sku = "Premium"
      }
    }
  }

  monitoring = {
    log_analytics_workspaces = {
      main = {
        name = "log-dev"
        sku = "PerGB2018"
      }
    }
  }
}
```

## Modules

### Resource Group Module
Creates resource groups with consistent naming and tagging.

### Networking Module
- Virtual networks with hub-and-spoke topology
- Subnets with delegation support
- Network security groups with custom rules
- Automatic NSG-subnet associations

### Key Vault Module
- Key vaults with access policies
- Network ACLs support
- RBAC authorization option

### AKS Module
- Kubernetes clusters with multiple node pools
- Network profiles for CNI
- Add-on profiles (monitoring, ingress)
- Auto-scaling support

### ACR Module
- Container registries with geo-replication
- Admin access control
- Network restrictions

### Log Analytics Module
- Workspaces for monitoring
- Retention policies
- Quota management

## Scaling

To add new environments or resources:

1. **New Environment**: Copy an existing environment directory and modify `terraform.tfvars`
2. **New Resources**: Add entries to the nested maps in `landing_zone_config`
3. **New Modules**: Create new modules following the established patterns

## Best Practices

- Use remote state with Azure Storage
- Implement proper access controls
- Regular security updates
- Monitor costs and usage
- Use Terraform workspaces for multi-environment management

## Contributing

1. Follow Terraform best practices
2. Use consistent naming conventions
3. Update documentation for changes
4. Test changes in dev environment first

## Support

For issues and questions, please check:
- Azure documentation
- Terraform documentation
- Module-specific READMEs