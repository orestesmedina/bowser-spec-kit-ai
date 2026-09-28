#!/usr/bin/env bash
# Hook PreToolUse: impide que los agentes editen archivos sensibles.
# Salir con código 2 bloquea la acción y le muestra el motivo a Claude.

FILE=$(jq -r '.tool_input.file_path // empty')
[ -z "$FILE" ] && exit 0

# 1. Secretos
case "$FILE" in
  *.env|*/.env.*|*/secrets/*|*.pem|*.key)
    echo "Bloqueado: '$FILE' puede contener secretos. Usa .env.example para documentar variables." >&2
    exit 2
    ;;
esac

# 2. La constitución solo la cambia un humano
case "$FILE" in
  */.specify/memory/constitution.md)
    echo "Bloqueado: la constitución solo se modifica con aprobación de la dirección técnica." >&2
    exit 2
    ;;
esac

# 3. Migraciones ya versionadas en git no se editan (se crea una nueva)
if [[ "$FILE" == */backend/migrations/*.sql ]] && [ -f "$FILE" ]; then
  if git -C "$CLAUDE_PROJECT_DIR" ls-files --error-unmatch "$FILE" >/dev/null 2>&1; then
    echo "Bloqueado: '$FILE' ya está versionada. Crea una migración nueva en lugar de editarla." >&2
    exit 2
  fi
fi

exit 0
