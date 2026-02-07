"""Create an admin user in the database.

Usage (from project root):
    docker exec photo-platform-auth python scripts/create_admin.py

Or with custom credentials:
    docker exec -e ADMIN_EMAIL=admin@example.com \
                -e ADMIN_USERNAME=myadmin \
                -e ADMIN_PASSWORD='Admin123!@#' \
                photo-platform-auth python scripts/create_admin.py
"""

import asyncio
import os
import sys

# Ensure the service root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from shared.enums import UserRole


# Defaults (override via environment variables)
DEFAULT_EMAIL = "admin@admin.com"
DEFAULT_USERNAME = "admin_user"
DEFAULT_PASSWORD = "Admin123!@#"


async def create_admin() -> None:
    """Create an admin user if one does not already exist."""
    email = os.getenv("ADMIN_EMAIL", DEFAULT_EMAIL)
    username = os.getenv("ADMIN_USERNAME", DEFAULT_USERNAME)
    password = os.getenv("ADMIN_PASSWORD", DEFAULT_PASSWORD)

    async with AsyncSessionLocal() as db:
        # Check if an admin already exists
        result = await db.execute(
            select(User).where(User.role == UserRole.ADMIN)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Admin user already exists: {existing.username} ({existing.email})")
            return

        # Check if email/username is taken
        result = await db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        conflict = result.scalar_one_or_none()
        if conflict:
            print(f"User with email '{email}' or username '{username}' already exists.")
            print("Promoting existing user to ADMIN role...")
            conflict.role = UserRole.ADMIN
            await db.commit()
            print(f"Done — {conflict.username} is now an admin.")
            return

        # Create new admin user
        admin = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            full_name="Platform Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        await db.commit()

        print(f"Admin user created successfully!")
        print(f"  Email:    {email}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print()
        print("IMPORTANT: Change the default password after first login.")


if __name__ == "__main__":
    asyncio.run(create_admin())
