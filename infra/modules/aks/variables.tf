variable "kubernetes_clusters" {
  description = "Map of AKS clusters"
  type = map(object({
    name                = string
    location            = string
    resource_group_name = string
    dns_prefix          = string
    kubernetes_version  = string
    default_node_pool = object({
      name            = string
      node_count      = number
      vm_size        = string
      os_disk_size_gb = number
    })
    tags = optional(map(string), {})
  }))
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
