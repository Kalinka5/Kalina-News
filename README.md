# Kalina News API

A news platform for delivering articles to readers, allowing user interaction through comments, and providing content management capabilities for authors, editors, and administrators.

## Features

- **Articles**: CRUD operations for news articles, including titles, content, authors, publication dates, categories, and tags.
- **User Management**: Registration, authentication, and role-based access for users (authors, editors, admins).
- **Categories and Tags**: Organization of articles into categories and tags for better discoverability.
- **Comments**: Authenticated users can comment on articles.
- **Search**: Keyword-based search for articles.
- **Admin Panel**: Restricted endpoints for managing content and users.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Caching**: Redis (optional)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional, for caching)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/kalina-news.git
   cd kalina-news
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file with your configuration.

5. Initialize the database:

   ```bash
   alembic upgrade head
   ```

6. Run the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

7. Access the API documentation at http://localhost:8000/docs

## API Endpoints

### Authentication

- `POST /api/v1/login`: Authenticate a user and return a JWT token.

### Users

- `POST /api/v1/users`: Register a new user.
- `GET /api/v1/users/me`: Get the current authenticated user's information.
- `PUT /api/v1/users/me`: Update the current authenticated user's information.
- `GET /api/v1/users`: Get a list of all users (admin only).
- `GET /api/v1/users/{user_id}`: Get a user by ID (admin only).

### Articles

- `GET /api/v1/articles`: Retrieve a paginated list of articles.
- `GET /api/v1/articles/{id}`: Retrieve a specific article by ID.
- `POST /api/v1/articles`: Create a new article (authenticated; authors, editors, admins).
- `PUT /api/v1/articles/{id}`: Update an article (authenticated; article author, editors, admins).
- `DELETE /api/v1/articles/{id}`: Delete an article (authenticated; editors, admins).

### Categories

- `GET /api/v1/categories`: Retrieve a list of all categories.
- `POST /api/v1/categories`: Create a new category (authenticated; admins).
- `PUT /api/v1/categories/{id}`: Update a category (authenticated; admins).
- `DELETE /api/v1/categories/{id}`: Delete a category (authenticated; admins).

### Tags

- `GET /api/v1/tags`: Retrieve a list of all tags.
- `POST /api/v1/tags`: Create a new tag (authenticated; admins).
- `PUT /api/v1/tags/{id}`: Update a tag (authenticated; admins).
- `DELETE /api/v1/tags/{id}`: Delete a tag (authenticated; admins).

### Comments

- `GET /api/v1/articles/{article_id}/comments`: Retrieve comments for a specific article.
- `POST /api/v1/articles/{article_id}/comments`: Add a comment to an article (authenticated).
- `DELETE /api/v1/comments/{id}`: Delete a comment (authenticated; comment owner or admins).

### Search

- `GET /api/v1/search?q={query}`: Search articles by keyword in title, body, or author.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
