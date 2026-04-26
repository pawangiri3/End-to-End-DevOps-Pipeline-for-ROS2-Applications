# Azure Landing Zone with Terraform

This repository contains a streamlined, scalable Azure landing zone implementation using modern Terraform patterns. Designed specifically for ROS2 applications, this landing zone provides essential cloud infrastructure components that are reusable across multiple environments (dev, staging, prod) while maintaining simplicity and ease of management.

## Architecture

The landing zone implements a minimal yet complete infrastructure setup with the following core components:

- **Resource Groups**: Centralized resource organization and management
- **Azure Container Registry (ACR)**: Secure container image storage and management
- **Azure Kubernetes Service (AKS)**: Managed Kubernetes clusters for containerized applications

This simplified architecture focuses on the essential components needed for deploying and managing ROS2 applications, making it easy to scale while keeping operational overhead low.

## Structure

```
infra/
├── modules/              # Reusable Terraform modules
│   ├── resource_group/   # Resource group creation
│   ├── acr/             # Azure Container Registry
│   └── aks/             # Azure Kubernetes Service
├── envs/                 # Environment-specific configurations
│   ├── dev/             # Development environment
│   │   ├── main.tf      # Environment-specific resources
│   │   ├── variables.tf # Environment variables
│   │   ├── terraform.tfvars # Environment values
│   │   └── provider.tf  # Azure provider config
│   ├── staging/         # Staging environment
│   └── prod/            # Production environment
└── pipelines/           # CI/CD pipeline definitions
    ├── infra-pipeline.yml # Infrastructure deployment
    └── app-pipeline.yml   # Application deployment
```

## Key Features

### Environment-Based Configuration
- **Dev Environment**: Single-node AKS for development and testing
- **Staging Environment**: Multi-node AKS with monitoring for pre-production
- **Prod Environment**: Highly available, scalable AKS with advanced features

### Scalable and Reusable
- Modular Terraform modules that can be reused across environments
- Environment-specific variable files for easy customization
- Consistent naming conventions and tagging
- Easy to extend with additional components when needed

### Easy Management
- Simplified configuration with minimal variables
- Clear separation of concerns between environments
- Automated deployment via Azure DevOps pipelines
- Cost-effective resource allocation per environment

### Modern Terraform Patterns
- Terraform 1.5+ compatibility
- AzureRM provider 4.70+
- Proper resource dependencies and lifecycle management
- Sensitive data handling with secure variable management

## Usage

### Prerequisites

1. Azure CLI installed and authenticated
2. Terraform 1.5+ installed
3. Azure subscription with appropriate permissions
4. Azure DevOps project (for CI/CD pipelines)

### Deployment

1. **Navigate to environment directory**:
   ```bash
   cd envs/dev  # or staging/prod
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Review deployment plan**:
   ```bash
   terraform plan
   ```

4. **Apply configuration**:
   ```bash
   terraform apply
   ```

### Configuration Structure

Each environment uses a simple, focused configuration:

```hcl
# Resource Groups
resource_groups = {
  compute = {
    name     = "rg-dev-compute-rudra"
    location = "East US 2"
  }
}

# Container Registry
container_registries = {
  acr = {
    name                = "rudradevacr"
    location            = "East US 2"
    resource_group_name = "rg-dev-compute-rudra"
    sku                 = "Premium"
    admin_enabled       = false
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
```

## Modules

### Resource Group Module
- Creates resource groups with consistent naming
- Applies standard tags across all resources
- Supports multiple resource groups per environment

### ACR Module
- Provisions Azure Container Registry
- Configurable SKU (Basic, Standard, Premium)
- Admin access control
- Network access restrictions support

### AKS Module
- Deploys managed Kubernetes clusters
- Configurable node pools and VM sizes
- Kubernetes version management
- System-assigned managed identity
- Basic networking configuration

## Scaling Across Environments

### Adding New Environments
1. Copy an existing environment directory (e.g., `dev` to `new-env`)
2. Update `terraform.tfvars` with environment-specific values
3. Modify resource names, sizes, and configurations as needed
4. Run `terraform init`, `plan`, and `apply`

### Scaling Resources
- **Dev**: Minimal resources for development
- **Staging**: Increased node counts, monitoring enabled
- **Prod**: High availability, multiple node pools, advanced networking

### Extending Components
To add more components (networking, monitoring, etc.):
1. Create new modules following existing patterns
2. Add variables to `variables.tf`
3. Update `terraform.tfvars` with new configurations
4. Include modules in `main.tf`

## CI/CD Integration

The landing zone includes Azure DevOps pipeline templates:

- **infra-pipeline.yml**: Automated infrastructure deployment
- **app-pipeline.yml**: Application deployment to AKS

Pipelines support:
- Multi-stage deployments (dev → staging → prod)
- Automated testing and validation
- Rollback capabilities
- Environment-specific configurations

## Best Practices

### Infrastructure Management
- Use remote state with Azure Storage backend
- Implement proper RBAC and access controls
- Regular security updates and patching
- Monitor costs and resource utilization
- Use Terraform workspaces for complex multi-environment setups

### Application Deployment
- Store container images in ACR
- Use Kubernetes manifests in `k8s/` directory
- Implement proper resource limits and requests
- Use ConfigMaps and Secrets for configuration
- Enable monitoring with Prometheus/Grafana stack

### Cost Optimization
- Right-size VM instances per environment
- Use Azure reservations for production workloads
- Implement auto-scaling for AKS node pools
- Clean up unused resources regularly
- Monitor spending with Azure Cost Management

## Troubleshooting

### Common Issues
- **Authentication**: Ensure Azure CLI is logged in with correct subscription
- **Permissions**: Verify service principal has required Azure roles
- **Resource Quotas**: Check Azure subscription limits for AKS, ACR
- **Network**: Ensure proper network connectivity for AKS nodes

### Getting Help
- Check Terraform logs with `TF_LOG=DEBUG`
- Use `terraform validate` to check configuration
- Review Azure portal for resource status
- Check pipeline logs for deployment issues

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