output "namespace" {
  value = kubernetes_namespace.promptguard.metadata[0].name
}

output "release_name" {
  value = helm_release.promptguard.name
}
