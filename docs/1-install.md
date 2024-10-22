# LCAT - Installation guide

## Introduction

LCAT (the Local Climate Adaptation Tool) is a 3-tier web application, consisting of a Node Express server, a React client, and a Postgres database. To run this project locally, begin by cloning the project:

```bash
git clone https://github.com/Uni-of-Exeter/research.LCAT.public.git
cd research.LCAT.public
```

## 1. Express server

A simple NodeJS [Express](https://expressjs.com/) server is provided. To set up, run:

```bash
cd server
npm install
```

Run the server with:

```bash
npm run start
```

Or for local development, Nodemon is provided, by running:

```bash
npm run dev
```

In both cases, the server is started on port 3000.

## 2. React client

The front end is built in [React](https://react.dev/), using [Vite](https://vitejs.dev/). To set up, run:

```bash
cd client
npm install --legacy-peer-deps
```

To launch the Vite development server, run:

```bash
npm run dev
```

This will launch the web app on port 3001. Access the application at `localhost:3001` in your browser.

### Client production build

To build the client for production, and copy the bundle to the server, run the following:

```bash
npm run build
mkdir -p server/public
cp -R client/dist/* server/public
```

This will use Vite to produce a minified application bundle that is suitable to be statically served. This occurs on port 3000: to view this, visit `localhost:3000` with the server running.

## 3. PostgreSQL database

LCAT uses a Postgres database to store climate data, which is served to the user in the application via the API (located in the server module). You will need to build this database from scratch, or rebuild the database from a backup.

**Note**: You can find detailed instructions for rebuilding the database in `docs/2-database-build.md`.

### Create .env file

Once you have a working database, you will need to create a .env file in the server root directory. This should contain the database credentials used to build the database.

```text
DB_USER=db_username
DB_PASS=db_password
DB_HOST=localhost:5432
DB_DATABASE=db_name
```

## Running everything

The application should now be fully functional. Launch the server and client (or serve the minified build), select a geographic region, and check that climate data can be viewed.
