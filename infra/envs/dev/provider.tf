terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.70.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "Do_not_delete_rg"
    storage_account_name = "donotdelete2026"
    container_name       = "tfstate"
    key                  = "dev.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = "5789023e-647a-4c34-8b8d-de9fb25a09eb"
}