-- SCHEMA: public
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE verification_status AS ENUM ('pending', 'verified');

CREATE TYPE user_role AS ENUM ('superadmin', 'support');

CREATE TYPE stripe_mode AS ENUM ('live', 'test');

CREATE TYPE subscription_status AS ENUM (
    'active',
    'cancelled',
    'past_due',
    'incomplete',
    'incomplete_expired',
    'trialing',
    'unpaid'
);

-- Tables in public schema
CREATE TABLE public.plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    max_users INTEGER,
    max_properties INTEGER,
    price_per_month DECIMAL
);

CREATE TABLE public.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    schema_name VARCHAR NOT NULL,
    custom_domain VARCHAR,
    plan_id UUID REFERENCES public.plans(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.domain_verification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id),
    domain VARCHAR NOT NULL,
    status verification_status NOT NULL,
    verification_token VARCHAR NOT NULL
);

CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.stripe_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id),
    stripe_account_id VARCHAR NOT NULL,
    mode stripe_mode NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id),
    stripe_subscription_id VARCHAR NOT NULL,
    status subscription_status NOT NULL,
    current_period_end TIMESTAMP
);

-- SCHEMA: tenant (replace 'tenant' with your actual tenant schema name)
CREATE TYPE tenant_user_role AS ENUM ('admin', 'employee', 'client');

CREATE TYPE property_status AS ENUM ('available', 'rented', 'sold');

CREATE TYPE appointment_status AS ENUM ('pending', 'confirmed', 'cancelled');

CREATE TYPE contract_status AS ENUM ('draft', 'sent', 'signed');

CREATE TYPE reservation_status AS ENUM ('pending', 'confirmed', 'cancelled', 'completed');

CREATE TABLE tenant.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR,
    role tenant_user_role NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tenant.clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR NOT NULL,
    email VARCHAR,
    phone VARCHAR,
    user_id UUID REFERENCES tenant.users(id)
);

CREATE TABLE tenant.properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR NOT NULL,
    description TEXT,
    price DECIMAL,
    status property_status,
    address JSON,
    listed_at TIMESTAMP,
    agent_id UUID REFERENCES tenant.users(id)
);

CREATE TABLE tenant.property_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES tenant.properties(id),
    image_url VARCHAR NOT NULL,
    is_cover BOOLEAN DEFAULT FALSE
);

CREATE TABLE tenant.appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visitor_name VARCHAR,
    visitor_email VARCHAR,
    property_id UUID REFERENCES tenant.properties(id),
    scheduled_at TIMESTAMP,
    status appointment_status,
    agent_id UUID REFERENCES tenant.users(id)
);

CREATE TABLE tenant.contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES tenant.properties(id),
    buyer_name VARCHAR,
    status contract_status,
    docusign_envelope_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tenant.client_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES tenant.clients(id),
    property_id UUID REFERENCES tenant.properties(id),
    ownership_percentage DECIMAL,
    amount_invested DECIMAL,
    monthly_rent_expected DECIMAL
);

CREATE TABLE tenant.payouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES tenant.clients(id),
    amount DECIMAL,
    paid_at TIMESTAMP,
    property_id UUID REFERENCES tenant.properties(id)
);

CREATE TABLE tenant.settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    logo_url VARCHAR,
    primary_color VARCHAR,
    secondary_color VARCHAR,
    timezone VARCHAR
);

CREATE TABLE tenant.reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES tenant.properties(id),
    client_id UUID REFERENCES tenant.clients(id),
    reserved_from DATE,
    reserved_to DATE,
    status reservation_status,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);