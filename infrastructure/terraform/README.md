# Terraform deployment

This directory contains two deployment paths:

1. `./` (root): installs the Helm chart into an existing Kubernetes cluster using your kubeconfig.
2. `./aws`: placeholder AWS/EKS layout for managed infrastructure.

## Local/Existing cluster

```bash
cd infrastructure/terraform
terraform init
terraform apply -auto-approve
```

Inputs can be overridden via `-var`:

```bash
terraform apply -var="namespace=promptguard" -var="values_file=../helm/promptguard/values.yaml"
```

## AWS/EKS

`infrastructure/terraform/aws` contains the earlier EKS/RDS/Redis skeleton. Add modules under `aws/modules` as needed.
