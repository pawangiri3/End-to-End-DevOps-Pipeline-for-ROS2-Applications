output "key_vaults" {
  description = "Map of key vaults"
  value = {
    for k, v in azurerm_key_vault.this : k => {
      id   = v.id
      name = v.name
      uri  = v.vault_uri
    }
  }
}
