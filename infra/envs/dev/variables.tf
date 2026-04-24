variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US 2"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "rudra"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Environment = "dev"
    Project     = "rudra"
    ManagedBy   = "Terraform"
  }
}

variable "resource_groups" {
  description = "Map of resource groups to create"
  type = map(object({
    name     = string
    location = string

  }))
}

variable "virtual_networks" {
  description = "Map of virtual networks with subnets"
  type = map(object({
    address_space = list(string)
    subnets = map(object({
      address_prefixes = list(string)
    }))
  }))
}

variable "network_security_groups" {
  description = "Map of network security groups with rules"
  type = map(object({
    rules = list(object({
      name                       = string
      priority                   = number
      direction                  = string
      access                     = string
      protocol                   = string
      source_port_range          = optional(string, "*")
      destination_port_range     = optional(string, "*")
      source_address_prefix      = optional(string, "*")
      destination_address_prefix = optional(string, "*")
    }))
  }))
  default = {}
}

variable "key_vaults" {
  description = "Map of key vaults to create"
  type = map(object({
    name                      = string
    location                  = string
    resource_group_name       = string
    sku_name                  = string
    tenant_id                 = optional(string, "")
    enable_rbac_authorization = optional(bool, true)
  }))
  default = {}
}

variable "log_analytics_workspaces" {
  description = "Map of log analytics workspaces"
  type = map(object({
    name              = string
    location          = string
    resource_group_name = string
    sku               = string
    retention_in_days = optional(number, 30)
  }))
  default = {}
}

variable "container_registries" {
  description = "Map of container registries"
  type = map(object({
    name          = string
    location      = string
    resource_group_name = string
    sku           = string
    admin_enabled = optional(bool, false)
  }))
  default = {}
}

variable "kubernetes_clusters" {
  description = "Map of AKS clusters"
  type = map(object({
    name                = string
    location            = string
    resource_group_name = string
    dns_prefix          = string
    kubernetes_version  = optional(string, "1.30.0")
    default_node_pool = object({
      name            = string
      node_count      = number
      vm_size         = string
      os_disk_size_gb = optional(number, 128)
    })
  }))
  default = {}
}
