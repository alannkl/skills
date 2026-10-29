-- up
ALTER TABLE invoices ADD COLUMN currency char(3) DEFAULT 'USD';

-- down
ALTER TABLE invoices DROP COLUMN currency;
