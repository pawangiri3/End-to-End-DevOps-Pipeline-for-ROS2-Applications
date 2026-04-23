

variable "vnets" {
  type = map(object({
    name    = string
    subnets = map(object({
      name           = string
      address_prefix = string
    }))
  }))
}

variable "subnet" {}