output "acr_login_server" {
  description = "Login server for the Azure Container Registry (use this to tag/push images)"
  value       = azurerm_container_registry.main.login_server
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.name
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}
