variable "project_name" {
  description = "Short name used as a prefix for all Azure resources"
  type        = string
  default     = "metabase-analytics"
}

variable "location" {
  description = "Azure region to deploy into"
  type        = string
  default     = "westeurope"
}

variable "environment" {
  description = "Deployment environment tag (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vm_size" {
  description = "Azure VM size hosting Docker + Metabase"
  type        = string
  default     = "Standard_B2s" # 2 vCPU / 4GB RAM - enough for Metabase + Postgres
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "azureadmin"
}

variable "ssh_public_key_path" {
  description = "Path to your local SSH public key (e.g. ~/.ssh/id_rsa.pub)"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the VM. Restrict this to your own IP, e.g. 203.0.113.5/32"
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_metabase_cidr" {
  description = "CIDR block allowed to reach Metabase on port 3000. Restrict to your office/VPN IP."
  type        = string
  default     = "0.0.0.0/0"
}

variable "os_disk_size_gb" {
  description = "Size of the OS disk in GB"
  type        = number
  default     = 64
}
