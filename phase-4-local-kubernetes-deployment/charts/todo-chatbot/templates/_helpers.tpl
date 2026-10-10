{{/*
Name and label helpers. Kept in one place so selectors stay consistent between
the Deployments and the Services (T046 selects pods by
app.kubernetes.io/component=backend and depends on this).
*/}}

{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified app name. With release name `todo-chatbot` and chart name
`todo-chatbot`, this resolves to `todo-chatbot`, so the Services become
`todo-chatbot-frontend` and `todo-chatbot-backend` — the exact DNS names the
backend's JWKS URL depends on (D6).
*/}}
{{- define "todo-chatbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "todo-chatbot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Labels applied to every object. */}}
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ include "todo-chatbot.chart" . }}
{{ include "todo-chatbot.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels — the IMMUTABLE subset used in matchLabels and pod labels.
Adding a key here after release means the selector changes, which the API
server rejects, so only add labels that are known at install time.
*/}}
{{- define "todo-chatbot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-chatbot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Usage: {{ include "todo-chatbot.componentLabels" (dict "ctx" $ "component" "backend") }} */}}
{{- define "todo-chatbot.componentLabels" -}}
{{ include "todo-chatbot.selectorLabels" .ctx }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "todo-chatbot.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todo-chatbot.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "todo-chatbot.configMapName" -}}
{{- printf "%s-config" (include "todo-chatbot.fullname" .) }}
{{- end }}
