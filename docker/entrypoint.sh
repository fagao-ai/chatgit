# !/bin/bash
if [ "$CHATGIT_DB_ENABLE" = "true" ] || [ "$CHATGIT_DB_ENABLE" = "1" ]; then
    exec uv run inv db.migrate
else
    echo "CHATGIT_DB_ENABLE is not set to true or 1"
fi

exec uv run supervisord -n -c /etc/supervisor/supervisord.conf