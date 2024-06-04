# LCAT - Installation guide

## Introduction

LCAT (the Local Climate Adaptation Tool) is a 3-tier web application, consisting of a Node Express server, a React client, and a Postgres database. To run this project locally, begin by cloning the project:

    git clone https://github.com/Uni-of-Exeter/research.LCAT.public.git
    cd research.LCAT.public

## 1. Express server

A simple NodeJS [Express](https://expressjs.com/) server is provided. To set up, run:

    cd server
    npm install

Run the server with:

    npm run start

or for local development, Nodemon is provided, by running:

    npm run dev

In both cases, the server is started on port 3000.

## 2. React client

The front end is built in [React](https://react.dev/), using [Vite](https://vitejs.dev/). To set up, run:

    cd client
    npm install --legacy-peer-deps

To launch the Vite development server, run:

    npm run dev

This will launch the web app on port 3001. Access the application at `localhost:3001` in your browser.

### Client production build

To build the client for production, and copy the bundle to the server, run the following:

    npm run build
    mkdir -p server/public
    cp -R client/dist/* server/public

This will use Vite to produce a minified application bundle that is suitable to be statically served. This occurs on port 3000: to view this, visit `localhost:3000` with the server running.

## 3. Postgres database

LCAT uses a Postgres database to store climate data, which is provided to the user in the application via the API (located in the server module). To set this up locally from a database backup, follow the instructions below.

**Note**: You can find detailed instructions for rebuilding the database from the raw data files in `docs/2-database-build.md`. To shortcut this rebuild process, and restore from an existing database, you can download a database backup [here](http://data-lcat-uk.s3-website.eu-west-2.amazonaws.com/dumps/climate_geo_data2_prod_backup_20230829.sql.gz).
