CREATE TABLE customers (id serial PRIMARY KEY, name text NOT NULL, email text NOT NULL, created_at timestamptz DEFAULT now());
CREATE TABLE invoices (
  id serial PRIMARY KEY,
  customer_id integer NOT NULL REFERENCES customers(id),
  number text NOT NULL UNIQUE,
  status text NOT NULL CHECK (status IN ('draft', 'open', 'paid', 'void')),
  total_cents integer NOT NULL,
  issued_at timestamptz,
  due_at timestamptz
);
CREATE TABLE payments (id serial PRIMARY KEY, invoice_id integer NOT NULL REFERENCES invoices(id), amount_cents integer NOT NULL, paid_at timestamptz NOT NULL);
