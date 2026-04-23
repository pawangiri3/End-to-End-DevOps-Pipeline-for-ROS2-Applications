output "container_registries" {
  description = "Map of container registries"
  value = {
    for k, v in azurerm_container_registry.this : k => {
      id           = v.id
      name         = v.name
      login_server = v.login_server
    }
  }
}
