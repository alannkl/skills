-- up
ALTER TABLE orders ADD COLUMN currency char(3) NOT NULL DEFAULT 'USD';

-- down
ALTER TABLE orders DROP COLUMN currency;
