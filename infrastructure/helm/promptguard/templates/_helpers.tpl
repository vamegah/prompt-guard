{{- define "promptguard.name" -}}
promptguard
{{- end -}}

{{- define "promptguard.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "promptguard.name" .) -}}
{{- end -}}

{{- define "promptguard.labels" -}}
app.kubernetes.io/name: {{ include "promptguard.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | default .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "promptguard.componentLabels" -}}
{{ include "promptguard.labels" . }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}
