-- Query to check the latest messages for a specific session
SELECT 
    created_at,
    message->>'type' as message_type,
    message->>'content' as content,
    message->'data'->>'drafts' as drafts
FROM messages 
WHERE session_id = 'sess-123'
ORDER BY created_at DESC;