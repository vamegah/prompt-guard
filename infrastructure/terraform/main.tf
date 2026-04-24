terraform {
  required_version = ">= 1.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kube_context
}

provider "helm" {
  kubernetes {
    config_path    = var.kubeconfig_path
    config_context = var.kube_context
  }
}

resource "kubernetes_namespace" "promptguard" {
  metadata {
    name = var.namespace
  }
}

resource "helm_release" "promptguard" {
  name       = var.release_name
  namespace  = kubernetes_namespace.promptguard.metadata[0].name
  chart      = var.chart_path
  timeout    = 600
  wait       = true
  atomic     = true
  values     = [file(var.values_file)]
}
