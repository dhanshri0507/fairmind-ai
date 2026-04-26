-- FairMind AI · Supabase Schema
-- Run this in the Supabase SQL editor to initialize the database.

create table if not exists audits (
  id            text primary key,
  filename      text,
  overall_bias_detected boolean default false,
  fairness_score        integer default 0,
  dataset_size          integer default 0,
  results       jsonb,
  created_at    timestamptz default now()
);

-- Enable RLS (Row Level Security)
alter table audits enable row level security;

-- Allow public anonymous reads and inserts (adjust for auth in production)
create policy "Allow public insert" on audits for insert with check (true);
create policy "Allow public select" on audits for select using (true);
create policy "Allow public update" on audits for update using (true) with check (true);

-- Index for fast recent-first lookups
create index if not exists idx_audits_created_at on audits (created_at desc);
