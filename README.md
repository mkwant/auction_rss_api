# Auction RSS Api

This API returns RSS feeds for the search results of (mostly) auction sites.

## Adding auction extractors

Subclass the AuctionExtractor basemodel and add an endpoint to one of routers.

## Docker

`Dockerfile` and `docker-compose.yml` files are included. The latter also includes Traefek and Watchtower containers.

## Configuration

Config is done through a `.env` file, an example of which is included.