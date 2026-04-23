output "kubernetes_clusters" {
  description = "Map of AKS clusters"
  value = {
    for k, v in azurerm_kubernetes_cluster.this : k => {
      id   = v.id
      name = v.name
      fqdn = v.fqdn
    }
  }
}
