variable "log_analytics_workspaces" {
  description = "Map of log analytics workspaces"
  type = map(object({
    name              = string
    location          = string
    resource_group_name = string
    sku               = string
    retention_in_days = number
    tags              = optional(map(string), {})
  }))
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
