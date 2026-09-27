output "vm_public_ip" {
  description = "Public IP address of the Metabase VM"
  value       = data.azurerm_public_ip.pip.ip_address
}

output "metabase_url" {
  description = "Metabase URL"
  value       = "http://${data.azurerm_public_ip.pip.ip_address}:3000"
}

output "ssh_command" {
  description = "SSH command for the VM"
  value       = "ssh azureuser@${data.azurerm_public_ip.pip.ip_address}"
}

output "resource_group_name" {
  description = "Resource group name"
  value       = data.azurerm_resource_group.rg.name
}
