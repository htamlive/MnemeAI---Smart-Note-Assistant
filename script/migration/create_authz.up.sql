CREATE TABLE authz (
	chat_id BIGINT NOT NULL,
	service_type VARCHAR(20) NOT NULL,
	token TEXT NULL,
	refresh_token TEXT NULL,
	client_id TEXT NULl,
	client_secret TEXT NULL,
	current_state TEXT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (chat_id, service_type)
)
