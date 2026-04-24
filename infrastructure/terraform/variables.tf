variable "kubeconfig_path" {
  type        = string
  description = "Path to kubeconfig file."
  default     = "~/.kube/config"
}

variable "kube_context" {
  type        = string
  description = "Kubeconfig context to use."
  default     = null
}

variable "namespace" {
  type        = string
  description = "Namespace for PromptGuard."
  default     = "promptguard"
}

variable "release_name" {
  type        = string
  description = "Helm release name."
  default     = "promptguard"
}

variable "chart_path" {
  type        = string
  description = "Path to the Helm chart."
  default     = "../helm/promptguard"
}

variable "values_file" {
  type        = string
  description = "Values file for the Helm chart."
  default     = "../helm/promptguard/values.yaml"
}
