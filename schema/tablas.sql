create table messages (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null,
  channel text not null, -- Ej: "WhatsApp", "Email", "Web"
  message text not null,
  intent text, -- Detectado por el Agente Clasificador
  created_at timestamp with time zone default now(),
  order_error_reason text, -- Razón del error si no se pudo procesar el pedido
);

create table orders (
  order_id text primary key, -- Ej: "#1234"
  customer_id uuid not null,
  status text not null, -- Ej: "Enviado", "Pendiente", "Entregado"
  shipped_date date,
  delivery_estimate date,
  updated_at timestamp with time zone default now()
  order_checked boolean default false -- Indica si el pedido ha sido revisado por el agente
);

create table responses (
  id uuid primary key default gen_random_uuid(),
  message_id uuid references messages(id) on delete cascade,
  agent_response text not null,
  sent_at timestamp with time zone default now()
);

create table analytics (
  id serial primary key,
  summary_date date default current_date,
  top_intents jsonb, -- Ej: {"compra": 20, "devolución": 12}
  created_at timestamp with time zone default now()
);

create table customers (
  id uuid primary key default gen_random_uuid(),
  name text,
  email text,
  phone text,
  created_at timestamp with time zone default now()
);

create table order_processing_log (
  id uuid default gen_random_uuid() primary key,
  message_id uuid references messages(id),
  status text, -- success, not_found, no_order_id
  timestamp timestamp default now(),
  detail text
);