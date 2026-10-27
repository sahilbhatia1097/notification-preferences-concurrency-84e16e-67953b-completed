CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) UNIQUE,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email_enabled BOOLEAN NOT NULL DEFAULT true,
    sms_enabled BOOLEAN NOT NULL DEFAULT false,
    push_enabled BOOLEAN NOT NULL DEFAULT true,
    frequency VARCHAR(50) NOT NULL DEFAULT 'realtime',
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO tenants (id, name) VALUES
    ('a1000000-0000-0000-0000-000000000001', 'Acme Corp'),
    ('b2000000-0000-0000-0000-000000000002', 'Globex Inc');

INSERT INTO users (id, tenant_id, email, role) VALUES
    ('c3000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'alice@acme.com', 'user'),
    ('c3000000-0000-0000-0000-000000000002', 'a1000000-0000-0000-0000-000000000001', 'bob@acme.com', 'user'),
    ('c3000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000001', 'carol@acme.com', 'admin'),
    ('d4000000-0000-0000-0000-000000000001', 'b2000000-0000-0000-0000-000000000002', 'dave@globex.com', 'user');

INSERT INTO notification_preferences (user_id, tenant_id, email_enabled, sms_enabled, push_enabled, frequency, version) VALUES
    ('c3000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', true, false, true, 'realtime', 1),
    ('c3000000-0000-0000-0000-000000000002', 'a1000000-0000-0000-0000-000000000001', true, true, false, 'daily', 1),
    ('c3000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000001', false, false, true, 'weekly', 1),
    ('d4000000-0000-0000-0000-000000000001', 'b2000000-0000-0000-0000-000000000002', true, false, false, 'realtime', 1);
