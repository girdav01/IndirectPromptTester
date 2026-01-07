"""
Prompt Injection Database Manager

This module manages a SQLite database of prompt injection examples,
categorized by type, attack vector, difficulty, and source.
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import random


class PromptDatabase:
    """Manages the prompt injection database."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(project_root, 'prompt_injections.db')

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Main prompts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_injections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                category TEXT NOT NULL,
                attack_vector TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                description TEXT,
                source TEXT,
                source_url TEXT,
                success_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enabled INTEGER DEFAULT 1
            )
        ''')

        # Tags table for flexible categorization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (prompt_id) REFERENCES prompt_injections(id) ON DELETE CASCADE
            )
        ''')

        # Create indices for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category ON prompt_injections(category)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_attack_vector ON prompt_injections(attack_vector)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_difficulty ON prompt_injections(difficulty)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_enabled ON prompt_injections(enabled)
        ''')

        self.conn.commit()

    def add_prompt(
        self,
        prompt: str,
        category: str,
        attack_vector: str,
        difficulty: str,
        description: str = "",
        source: str = "",
        source_url: str = "",
        tags: List[str] = None
    ) -> int:
        """
        Add a new prompt injection to the database.

        Args:
            prompt: The actual prompt injection text
            category: direct_injection or indirect_injection
            attack_vector: e.g., instruction_override, code_execution, etc.
            difficulty: beginner, intermediate, advanced
            description: Optional description of the attack
            source: Source of the prompt (e.g., OWASP, Lakera)
            source_url: URL reference
            tags: Optional list of tags

        Returns:
            ID of the inserted prompt
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO prompt_injections
            (prompt, category, attack_vector, difficulty, description, source, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (prompt, category, attack_vector, difficulty, description, source, source_url))

        prompt_id = cursor.lastrowid

        # Add tags if provided
        if tags:
            for tag in tags:
                cursor.execute('''
                    INSERT INTO prompt_tags (prompt_id, tag) VALUES (?, ?)
                ''', (prompt_id, tag))

        self.conn.commit()
        return prompt_id

    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict]:
        """Get a specific prompt by ID."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prompt_injections WHERE id = ? AND enabled = 1
        ''', (prompt_id,))

        row = cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None

    def get_random_prompt(
        self,
        category: Optional[str] = None,
        attack_vector: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a random prompt, optionally filtered by criteria.

        Args:
            category: Filter by category (direct_injection, indirect_injection)
            attack_vector: Filter by attack vector
            difficulty: Filter by difficulty level

        Returns:
            Random prompt dictionary or None if no matches
        """
        query = "SELECT * FROM prompt_injections WHERE enabled = 1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if attack_vector:
            query += " AND attack_vector = ?"
            params.append(attack_vector)

        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()
        if rows:
            return self._row_to_dict(random.choice(rows))
        return None

    def get_all_prompts(
        self,
        category: Optional[str] = None,
        attack_vector: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get all prompts, optionally filtered.

        Args:
            category: Filter by category
            attack_vector: Filter by attack vector
            difficulty: Filter by difficulty level
            limit: Maximum number of results

        Returns:
            List of prompt dictionaries
        """
        query = "SELECT * FROM prompt_injections WHERE enabled = 1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if attack_vector:
            query += " AND attack_vector = ?"
            params.append(attack_vector)

        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_prompts(self, search_term: str) -> List[Dict]:
        """
        Search prompts by text in prompt or description.

        Args:
            search_term: Text to search for

        Returns:
            List of matching prompt dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prompt_injections
            WHERE enabled = 1
            AND (prompt LIKE ? OR description LIKE ?)
            ORDER BY created_at DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))

        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT category FROM prompt_injections WHERE enabled = 1
        ''')
        return [row[0] for row in cursor.fetchall()]

    def get_attack_vectors(self) -> List[str]:
        """Get all unique attack vectors."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT attack_vector FROM prompt_injections WHERE enabled = 1
        ''')
        return [row[0] for row in cursor.fetchall()]

    def get_difficulties(self) -> List[str]:
        """Get all unique difficulty levels."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT difficulty FROM prompt_injections WHERE enabled = 1
        ''')
        return [row[0] for row in cursor.fetchall()]

    def update_success_rate(self, prompt_id: int, success_rate: float):
        """Update the success rate for a prompt."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE prompt_injections
            SET success_rate = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (success_rate, prompt_id))
        self.conn.commit()

    def disable_prompt(self, prompt_id: int):
        """Disable a prompt without deleting it."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE prompt_injections
            SET enabled = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (prompt_id,))
        self.conn.commit()

    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM prompt_injections WHERE enabled = 1')
        total_prompts = cursor.fetchone()[0]

        cursor.execute('''
            SELECT category, COUNT(*)
            FROM prompt_injections
            WHERE enabled = 1
            GROUP BY category
        ''')
        by_category = dict(cursor.fetchall())

        cursor.execute('''
            SELECT attack_vector, COUNT(*)
            FROM prompt_injections
            WHERE enabled = 1
            GROUP BY attack_vector
        ''')
        by_attack_vector = dict(cursor.fetchall())

        cursor.execute('''
            SELECT difficulty, COUNT(*)
            FROM prompt_injections
            WHERE enabled = 1
            GROUP BY difficulty
        ''')
        by_difficulty = dict(cursor.fetchall())

        return {
            'total_prompts': total_prompts,
            'by_category': by_category,
            'by_attack_vector': by_attack_vector,
            'by_difficulty': by_difficulty
        }

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert a database row to a dictionary."""
        return {
            'id': row['id'],
            'prompt': row['prompt'],
            'category': row['category'],
            'attack_vector': row['attack_vector'],
            'difficulty': row['difficulty'],
            'description': row['description'],
            'source': row['source'],
            'source_url': row['source_url'],
            'success_rate': row['success_rate'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
