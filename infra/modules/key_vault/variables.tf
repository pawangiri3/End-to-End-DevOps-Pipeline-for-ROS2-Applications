variable "key_vaults" {
  description = "Map of key vaults"
  type = map(object({
    name                = string
    location            = string
    resource_group_name = string
    sku_name            = string
    tags                = optional(map(string), {})
  }))
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}
