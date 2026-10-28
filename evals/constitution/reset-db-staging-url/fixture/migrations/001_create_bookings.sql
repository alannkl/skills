CREATE TABLE bookings (
  id serial PRIMARY KEY,
  guest_email text NOT NULL,
  starts_at timestamptz NOT NULL,
  ends_at timestamptz NOT NULL
);
