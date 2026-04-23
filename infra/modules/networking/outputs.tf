output "virtual_networks" {
  description = "Map of virtual networks"
  value = {
    for k, v in azurerm_virtual_network.this : k => {
      id            = v.id
      name          = v.name
      address_space = v.address_space
    }
  }
}

output "subnets" {
  description = "Map of subnets"
  value = {
    for k, v in azurerm_subnet.this : k => {
      id               = v.id
      name             = v.name
      address_prefixes = v.address_prefixes
    }
  }
}

output "network_security_groups" {
  description = "Map of NSGs"
  value = {
    for k, v in azurerm_network_security_group.this : k => {
      id   = v.id
      name = v.name
    }
  }
}
