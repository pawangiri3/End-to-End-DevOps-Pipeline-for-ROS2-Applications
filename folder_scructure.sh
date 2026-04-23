#!/bin/bash

echo "🚀 Creating Production Terraform Infra Structure..."

# Root
mkdir -p infra

# Modules
mkdir -p infra/modules/{resource_group,vnet,aks,acr,key_vault,log_analytics,ingress_nginx,public_ip,dns,identity}

# Create module files
for module in resource_group vnet aks acr key_vault log_analytics ingress_nginx public_ip dns identity
do
  touch infra/modules/$module/main.tf
  touch infra/modules/$module/variables.tf
  touch infra/modules/$module/outputs.tf
done

# Environments
mkdir -p infra/envs/{dev,staging,prod}

for env in dev staging prod
do
  touch infra/envs/$env/main.tf
  touch infra/envs/$env/variables.tf
  touch infra/envs/$env/terraform.tfvars
  touch infra/envs/$env/backend.tf
  touch infra/envs/$env/outputs.tf
done

# Global configs
mkdir -p infra/global/backend
mkdir -p infra/global/naming

touch infra/global/backend/backend.tf
touch infra/global/naming/locals.tf

# Scripts
mkdir -p infra/scripts
touch infra/scripts/{init.sh,plan.sh,apply.sh,destroy.sh}

# Azure DevOps pipelines
mkdir -p infra/pipelines
touch infra/pipelines/{infra-pipeline.yml,app-pipeline.yml}

# Root-level terraform files
touch infra/{versions.tf,provider.tf,variables.tf,outputs.tf}

# README
touch infra/README.md

echo "✅ Infra structure created successfully!"