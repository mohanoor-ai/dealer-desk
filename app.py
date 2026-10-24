"""Vercel's supported FastAPI entrypoint. Migrate separately before promotion."""
from backend.app import app

__all__ = ['app']
