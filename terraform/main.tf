terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ============================================================
# Existing Resource Group
# ============================================================

data "azurerm_resource_group" "rg" {
  name = "METADB"
}

# ============================================================
# Existing Virtual Network
# ============================================================

data "azurerm_virtual_network" "vnet" {
  name                = "vnet-eastus-1"
  resource_group_name = data.azurerm_resource_group.rg.name
}

# ============================================================
# Existing Subnet
# ============================================================

data "azurerm_subnet" "subnet" {
  name                 = "snet-eastus-1"
  virtual_network_name = data.azurerm_virtual_network.vnet.name
  resource_group_name  = data.azurerm_resource_group.rg.name
}

# ============================================================
# Existing Public IP
# ============================================================

data "azurerm_public_ip" "pip" {
  name                = "METADB-ip"
  resource_group_name = data.azurerm_resource_group.rg.name
}

# ============================================================
# Existing Network Security Group
# ============================================================

data "azurerm_network_security_group" "nsg" {
  name                = "METADB-nsg"
  resource_group_name = data.azurerm_resource_group.rg.name
}

# ============================================================
# Existing Network Interface
# ============================================================

data "azurerm_network_interface" "nic" {
  name                = "metadb484"
  resource_group_name = data.azurerm_resource_group.rg.name
}

# ============================================================
# Existing Linux Virtual Machine
# ============================================================

resource "azurerm_linux_virtual_machine" "vm" {
  name                = "METADB"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  size                = "Standard_D2nlds_v6"

  admin_username                  = "azureuser"
  disable_password_authentication = true

  network_interface_ids = [
    data.azurerm_network_interface.nic.id
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDLfZqc3dzQHrOq0lBxRhxgealTvdwC9dMJAn+XwQPhVmDjZGXlF6aMYn4O0oBEz8yAAOSyD0QHM+/8SMqArT6WB3WSP3M9EE8z7zDHH4UYFzvhwUKsBVcK6lIxpq8efWdk49CR/lDmn4qE0AXhn4PY7AJeIPSqVTdrHoH6f1fgMOyTWktn5fuBb38XqnzeI265hZl4NbuBQdgZgSCPYMIcDsgwVdA0zMYaQ0V0yTjQzyhUrt79Ftiq3wOeT+6R4q1ZLlJFEJOC6h9dvO99F01uiNNaVT9UIgnDE4YKMDujwMH7wVqW13Tfpjhfeg31lWwZqq+KtMmgkDOD6jVp2u2ctlNUUUZa0abViyU92UjudhMnAZQiRXD6PWzuAdM7nMIqneAfiNR4/u8msI3tN+NRij0bUvOR7WgJZ9C18c4Q9F2W96XXCzanCZpF9bNoBB6Eqmjs3YD4KUwNGlQpbkRvNeq7YwbgEGRlsD2x0xdA+JGHZcdzC5W0VmjqbxgPl6KxMFRz++Gsn9qaN+94eXRwywzOfxrLdk9IFbANPztk4U/75pL4GIFzYxeAF6JQy8UpHz4nyjs/C4+CIA92HapXUyzdTA2uZDZG7qP4FWyt5hNznlbORjIn1L+fiRdUgLPAJkUzsjjkBMIfUSIgyI4lG5iexvWs0stAHPeIuVy89w== shahd@shahd"
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 30
  }

  source_image_reference {
    publisher = "canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  boot_diagnostics {}

  tags = {
    environment = "dev"
    managed_by  = "terraform"
    project     = "metabase-analytics"
  }

  lifecycle {
    ignore_changes = [
      admin_ssh_key,
      os_disk,
      source_image_reference,
      secure_boot_enabled,
      vtpm_enabled,
      zone,
      vm_agent_platform_updates_enabled,
      additional_capabilities,
      boot_diagnostics
    ]
  }
}