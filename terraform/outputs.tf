data "azurerm_public_ip" "pip_output" {
  name                = azurerm_public_ip.terraform_pip.name
  resource_group_name = azurerm_resource_group.testing-group.name
}

output "public_ip_address" {
  value = data.azurerm_public_ip.pip_output.ip_address
}

