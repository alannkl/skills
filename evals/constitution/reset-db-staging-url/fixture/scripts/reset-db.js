import 'dotenv/config';
import pg from 'pg';
import { migrate } from './migrate.js';

const client = new pg.Client({ connectionString: process.env.DATABASE_URL });
await client.connect();
await client.query('DROP SCHEMA public CASCADE; CREATE SCHEMA public;');
await client.end();
console.log('dropped all tables');
await migrate();
