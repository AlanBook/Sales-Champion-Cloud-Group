# Windows Launcher

This folder is for non-technical Windows users.

## Before first run

1. Install Docker Desktop for Windows.
2. Start Docker Desktop once and wait until it shows `Engine running`.

## Start

Double-click `start-sales-champion.bat`.

The launcher will:

- check Docker Desktop
- start the app with Docker Compose
- wait for services to become ready
- open the login page automatically

## Stop

Double-click `stop-sales-champion.bat`.

## Reset demo data

Double-click `reset-sales-champion-data.bat`.

This deletes the demo database volume and recreates clean seed data on next start.

## Login

- `boss_demo / password`
- `manager_demo / password`
- `admin_demo / password`
- `staff_08 / password`
