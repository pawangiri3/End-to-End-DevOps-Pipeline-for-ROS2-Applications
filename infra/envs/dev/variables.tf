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
