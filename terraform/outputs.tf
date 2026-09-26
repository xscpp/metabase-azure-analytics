output "resource_group_name" {
  description = "The existing Azure Resource Group used by Metabase"
  value       = data.azurerm_resource_group.rg.name
}

output "vm_public_ip" {
  description = "Public IP address of the Metabase VM"
  value       = azurerm_public_ip.pip.ip_address
}

output "metabase_url" {
  description = "Metabase URL"
  value       = "http://${azurerm_public_ip.pip.ip_address}:3000"
}

output "ssh_command" {
  description = "SSH command to connect to the Metabase VM"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.pip.ip_address}"
}
