#!/usr/bin/env bash
# =============================================================================
# 01_entrypoints.sh — Inventory every entrypoint = every candidate flow
# Usage:   ./01_entrypoints.sh [SRC_DIR]        (default: src/main)
# Output:  docs/scan/ENTRYPOINTS.md
# Deterministic, idempotent — re-run monthly in CI, diff to detect new flows.
# =============================================================================
set -euo pipefail

SRC="${1:-src/main}"
OUT_DIR="${OUT_DIR:-docs/scan}"
mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/ENTRYPOINTS.md"

section() { # $1=title $2=grep pattern
  echo "## $1"
  echo
  echo '```'
  grep -rn --include='*.java' -E "$2" "$SRC" 2>/dev/null | sed 's/^[[:space:]]*//' || echo "(none found)"
  echo '```'
  echo
}

{
  echo "# ENTRYPOINTS — candidate flows (generated $(date +%F))"
  echo
  echo "> Each entrypoint = one candidate flow for FLOW_BACKLOG.md."
  echo "> Re-running this script and diffing the output is how new flows reveal themselves."
  echo

  section "REST (JAX-RS)"                    '@(Path|GET|POST|PUT|DELETE|PATCH|HEAD)\('
  section "REST (JAX-RS parameterless markers)" '^\s*@(GET|POST|PUT|DELETE|PATCH)\s*$'
  section "REST (Spring MVC)"                '@(RestController|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\b'
  section "Messaging (JMS/MDB + Spring/Kafka)" '@(MessageDriven|JMSDestinationDefinition|OnMessage|JmsListener|KafkaListener|RabbitListener|SqsListener)\b'
  section "Scheduler / Batch"                '@(Schedule|Schedules|Scheduled|Timeout)\b|implements\s+Job\b'
  section "Servlet"                          '@WebServlet'
  section "SOAP / JAX-WS"                    '@(WebService|WebMethod)\b'

  echo "## Servlet mappings in web.xml"
  echo
  echo '```'
  find "$SRC" -name 'web.xml' -exec grep -Hn -E '<(servlet-class|url-pattern)>' {} \; 2>/dev/null || echo "(none)"
  echo '```'
} > "$OUT"

echo "OK: $OUT"
