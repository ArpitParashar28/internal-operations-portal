# What to say in an interview

**30-second explanation:**
I built an internal operations portal with two workflows: inventory control and employee helpdesk tickets. The React/TypeScript frontend calls a FastAPI REST backend. PostgreSQL stores users, inventory items, stock movements, and tickets. JWT authentication protects the API, and different roles have different permissions. I also added validation for business rules such as preventing negative stock and limiting employees to their own tickets. GitHub Actions runs tests and the frontend build automatically.

## Architecture discussion
- React is responsible for presentation and interaction.
- FastAPI owns business rules, validation, authentication and authorization.
- SQLAlchemy maps Python objects to PostgreSQL tables.
- JWT tokens authenticate requests without server-side sessions.
- GitHub Actions provides CI on every push/pull request.

## Questions you should be ready for
1. Why keep frontend and backend separate?
2. Why put stock validation in the backend?
3. How does JWT authentication work?
4. What is the difference between authentication and authorization?
5. Why use PostgreSQL instead of storing data in JSON files?
6. How would you deploy it on Azure?
7. What would you log/monitor in production?
