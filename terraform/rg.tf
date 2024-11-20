resource "azurerm_resource_group" "testing-group" {
  name     = "terraform-testing"
  location = "centralindia"
  tags = {
    environment = "dev"
  }
}

