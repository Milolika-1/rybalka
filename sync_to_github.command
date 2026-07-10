#!/bin/zsh
set -e

cd "$(dirname "$0")"

export GIT_SSH_COMMAND="ssh -i $HOME/.ssh/rybalka_bot_github -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

echo "Проверяю изменения..."
git status --short

git add -A

if git diff --cached --quiet; then
  echo "Новых изменений нет. GitHub уже синхронизирован."
  exit 0
fi

commit_message="Update fishing bot $(date '+%Y-%m-%d %H:%M')"

echo "Сохраняю версию: $commit_message"
git commit -m "$commit_message"

echo "Отправляю в GitHub..."
git push origin main

echo "Готово! GitHub обновлен."
