# notes-api

A small API for shared team notes.

## Running

    npm install
    DATABASE_URL=postgres://localhost/notes JWT_SECRET=dev npm start

## Auth

Get a token with `POST /auth/token` and the user's email and password, then send it on every request:

    Authorization: Bearer <token>

Tokens expire after 24 hours; request a new one with the same call.

## Endpoints

| Method | Path | Notes |
| --- | --- | --- |
| GET | /notes | the caller's notes |
| POST | /notes | create a note |
| DELETE | /notes/:id | owner only |
