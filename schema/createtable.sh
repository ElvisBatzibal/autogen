#!/bin/bash

# Configura tus variables de conexión
SUPABASE_DB_HOST="https://dtofcomppmoytkwmqvro.supabase.co"
SUPABASE_DB_PORT="5432"
SUPABASE_DB_NAME="postgres"
SUPABASE_DB_USER="postgres"
SUPABASE_DB_PASSWORD="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR0b2Zjb21wcG1veXRrd21xdnJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIyNzMyNTMsImV4cCI6MjA2Nzg0OTI1M30.yfrX1g3_0lTxJtKf6pJyTkqCIWiiSnv1qK4xsqZ5d6I"

# Exporta la variable para que psql la use automáticamente
export PGPASSWORD=$SUPABASE_DB_PASSWORD

echo "Creando tablas en Supabase..."

psql -h $SUPABASE_DB_HOST -p $SUPABASE_DB_PORT -d $SUPABASE_DB_NAME -U $SUPABASE_DB_USER <<EOF

-- Tabla de clientes
create table if not exists customers (
  id uuid primary key default gen_random_uuid(),
  name text,
  email text,
  phone text,
  created_at timestamp with time zone default now()
);

-- Tabla de mensajes
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references customers(id) on delete cascade,
  channel text not null,
  message text not null,
  intent text,
  created_at timestamp with time zone default now()
);

-- Tabla de pedidos
create table if not exists orders (
  order_id text primary key,
  customer_id uuid references customers(id) on delete cascade,
  status text not null,
  shipped_date date,
  delivery_estimate date,
  updated_at timestamp with time zone default now()
);

-- Tabla de respuestas generadas
create table if not exists responses (
  id uuid primary key default gen_random_uuid(),
  message_id uuid references messages(id) on delete cascade,
  agent_response text not null,
  sent_at timestamp with time zone default now()
);

-- Tabla de analítica resumida
create table if not exists analytics (
  id serial primary key,
  summary_date date default current_date,
  top_intents jsonb,
  created_at timestamp with time zone default now()
);

EOF

echo "✅ Tablas creadas exitosamente."

# Limpia variable sensible
unset PGPASSWORD