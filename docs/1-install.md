# LCAT - Installation guide

## Introduction

LCAT (the Local Climate Adaptation Tool) is a 3-tier web application, consisting of a Node Express server, a React client, and a Postgres database. To run this project locally, begin by cloning the project:

    git clone https://github.com/Uni-of-Exeter/research.LCAT.public.git
    cd research.LCAT.public

## Express server

A simple NodeJS [Express](https://expressjs.com/) server is provided. To set up, run:

    cd server
    npm install

Run the server with:

    npm run start

or for local development, Nodemon is provided, by running:

    npm run dev

In both cases, the server is started on port 3000.

## React client

The front end is built in [React](https://react.dev/), using [Vite](https://vitejs.dev/). To set up, run:

    cd client
    npm install --legacy-peer-deps

To launch the Vite development server, run:

    npm run dev

This will launch the web app on port 3001. Access the application at `localhost:3001` in your browser.

## Creating a production build

To build for production, and copy the bundle to the server, run the following:

    npm run build
    mkdir -p server/public
    cp -R client/dist/* server/public

This will use Vite to produce a minified application bundle that is suitable to be statically served. This occurs on port 3000: to view this, visit `localhost:3000` without the client running.
