resource "azurerm_virtual_network" "this" {
  for_each = var.virtual_networks

  name                = each.value.name
  location            = each.value.location
  resource_group_name = each.value.resource_group_name
  address_space       = each.value.address_space
  tags                = merge(each.value.tags, var.tags)
}

resource "azurerm_subnet" "this" {
  for_each = local.subnets

  name                 = "${each.value.vnet_key}-${each.key}"
  resource_group_name  = each.value.resource_group_name
  virtual_network_name = each.value.virtual_network_name
  address_prefixes     = each.value.address_prefixes
}

resource "azurerm_network_security_group" "this" {
  for_each = var.network_security_groups

  name                = each.key
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = merge(each.value.tags, var.tags)

  dynamic "security_rule" {
    for_each = each.value.rules
    content {
      name                       = security_rule.value.name
      priority                   = security_rule.value.priority
      direction                  = security_rule.value.direction
      access                     = security_rule.value.access
      protocol                   = security_rule.value.protocol
      source_port_range          = security_rule.value.source_port_range
      destination_port_range     = security_rule.value.destination_port_range
      source_address_prefix      = security_rule.value.source_address_prefix
      destination_address_prefix = security_rule.value.destination_address_prefix
    }
  }
}

locals {
  subnets = merge([
    for vnet_key, vnet in var.virtual_networks : {
      for subnet_key, subnet in vnet.subnets : "${vnet_key}-${subnet_key}" => {
        vnet_key             = vnet_key
        name                 = "${vnet_key}-${subnet_key}"
        resource_group_name  = vnet.resource_group_name
        virtual_network_name = vnet.name
        address_prefixes     = subnet.address_prefixes
      }
    }
  ]...)
}
