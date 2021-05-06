# site

sex

---

## Stack

### Backend:
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)

### Frontend:
- [Jinja](https://jinja.palletsprojects.com/en/2.11.x/)

---

## Installation

1. Install dependencies using `pip -r requirements.txt`
2. Make sure you have a PostgreSQL server running. [Instructions for losers](https://www.postgresql.org/docs/current/server-start.html)
3. Create a database using `createdb postgres`
4. Create schema using `psql -f schema.sql postgres`
5. Set an environment variable named `DB_URL` to your database's URL (usually this is `postgresql://localhost:5432/postgres`)
6. Run `__main__.py`
