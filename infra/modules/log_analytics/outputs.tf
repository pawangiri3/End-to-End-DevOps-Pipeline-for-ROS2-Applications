output "log_analytics_workspaces" {
  description = "Map of log analytics workspaces"
  value = {
    for k, v in azurerm_log_analytics_workspace.this : k => {
      id           = v.id
      name         = v.name
      workspace_id = v.workspace_id
    }
  }
}
