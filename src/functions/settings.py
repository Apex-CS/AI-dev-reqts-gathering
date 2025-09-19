import sqlite3

# Global SQL table definitions
LLM_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS llm_settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
"""

PROJECT_DETAILS_TABLE = """
CREATE TABLE IF NOT EXISTS project_details (
    project_name TEXT PRIMARY KEY,
    project_description TEXT,
    project_summary TEXT
)
"""

RQM_TOOL_DETAILS_TABLE = """
CREATE TABLE IF NOT EXISTS rqm_tool_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT,
    tool_type TEXT,
    rqm_type TEXT,
    url TEXT,
    tool_name TEXT,
    pat TEXT,
    user_email TEXT,
    FOREIGN KEY(project) REFERENCES project_details(project_name),
    UNIQUE(project, tool_name)
)
"""

RQM_ITEM_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS rqm_item_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT,
    item_id INTEGER,
    work_item_history TEXT,
    work_item_comments TEXT,
    work_item_commits TEXT,
    UNIQUE(project, item_id)
)
"""
    
    

# Utility context manager for DB connection
from contextlib import contextmanager
import os
import src.classes.work_item as work_item_module
WorkItem = work_item_module.WorkItem

@contextmanager
def db_cursor(db_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()

# LLM Settings
def save_llm_settings(db_path, settings):
    with db_cursor(db_path) as cursor:
        cursor.execute(LLM_SETTINGS_TABLE)
        for key, value in settings.items():
            cursor.execute("""
                INSERT INTO llm_settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, str(value)))

def get_llm_settings(db_path):
    with db_cursor(db_path) as cursor:
        cursor.execute(LLM_SETTINGS_TABLE)
        cursor.execute("SELECT key, value FROM llm_settings")
        return {row[0]: row[1] for row in cursor.fetchall()}

# Project Details
def save_project_details(db_path, project_name, project_description, project_summary):
    with db_cursor(db_path) as cursor:
        cursor.execute(PROJECT_DETAILS_TABLE)
        cursor.execute("""
            INSERT INTO project_details (project_name, project_description, project_summary)
            VALUES (?, ?, ?)
            ON CONFLICT(project_name) DO UPDATE SET project_description=excluded.project_description, project_summary=excluded.project_summary
        """, (project_name, project_description, project_summary))

def get_projects_details(db_path):
    with db_cursor(db_path) as cursor:
        cursor.execute(PROJECT_DETAILS_TABLE)
        cursor.execute("SELECT project_name, project_description, project_summary FROM project_details")
        return [{
            "project_name": row[0],
            "project_description": row[1],
            "project_summary": row[2]
        } for row in cursor.fetchall()]

def edit_project_details(db_path, project_name, new_title, new_description, new_summary):
    with db_cursor(db_path) as cursor:
        cursor.execute(PROJECT_DETAILS_TABLE)
        cursor.execute("""
            UPDATE project_details
            SET project_name = ?, project_description = ?, project_summary = ?
            WHERE project_name = ?
        """, (new_title, new_description, new_summary, project_name))

def delete_project_details(db_path, project_name):
    with db_cursor(db_path) as cursor:
        cursor.execute("DELETE FROM project_details WHERE project_name = ?", (project_name,))

# RQM Tool Details
def save_rqm_tool_details(db_path, project, tool_type, rqm_type, url, tool_name, pat, user_email):
    with db_cursor(db_path) as cursor:
        # Drop existing entry if tool_name already exists for the project
        cursor.execute(RQM_TOOL_DETAILS_TABLE)
        cursor.execute("""
            INSERT INTO rqm_tool_details (project, tool_type, rqm_type, tool_name, url, pat, user_email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project, tool_name) DO UPDATE SET
            tool_type=excluded.tool_type,
            rqm_type=excluded.rqm_type,
            url=excluded.url,
            pat=excluded.pat,
            user_email=excluded.user_email
        """, (project, tool_type, rqm_type, tool_name, url, pat, user_email))

def get_all_rqm_tool_details(db_path, project_name):
    with db_cursor(db_path) as cursor:
        cursor.execute(RQM_TOOL_DETAILS_TABLE)
        cursor.execute("SELECT tool_type, url, project, tool_name, rqm_type, pat, user_email FROM rqm_tool_details WHERE project = ?", (project_name,))
        return [{
            "tool_type": row[0],
            "url": row[1],
            "project": row[2],
            "tool_name": row[3],
            "rqm_type": row[4],
            "pat": row[5],
            "user_email": row[6]
        } for row in cursor.fetchall()]

def delete_rqm_tool_details(db_path, project_name, tool_name):
    with db_cursor(db_path) as cursor:
        cursor.execute("DELETE FROM rqm_tool_details WHERE project = ? AND tool_name = ?", (project_name, tool_name))

def get_project_info(db_path, project_name):
    with db_cursor(db_path) as cursor:
        cursor.execute(PROJECT_DETAILS_TABLE)
        cursor.execute("SELECT project_name, project_description, project_summary FROM project_details WHERE project_name = ?", (project_name,))
        result = cursor.fetchone()
        return {
            "project_name": result[0] if result else None,
            "project_description": result[1] if result else None,
            "project_summary": result[2] if result else None
        }
        
        
def get_work_items_project(db_path, project_name, rqm_name):
    with db_cursor(db_path) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_items (id INTEGER PRIMARY KEY, project_name TEXT, rqm_name TEXT, work_item_id INTEGER)
        """)
        cursor.execute("""
            SELECT id, project_name, rqm_name, work_item_id FROM work_items WHERE project_name = ? AND rqm_name = ?
        """, (project_name, rqm_name))
        return [WorkItem(*row) for row in cursor.fetchall()]
    
def save_remove_work_items_project(db_path, project_name, rqm_name, work_item_id):
    with db_cursor(db_path) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_items (
                id INTEGER PRIMARY KEY, 
                project_name TEXT, 
                rqm_name TEXT, 
                work_item_id INTEGER)
        """)
        cursor.execute("""
            SELECT 1 FROM work_items WHERE project_name = ? AND work_item_id = ? AND rqm_name = ?
        """, (project_name, work_item_id, rqm_name))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("""
            DELETE FROM work_items WHERE project_name = ? AND work_item_id = ? AND rqm_name = ?
            """, (project_name, work_item_id, rqm_name))
        else:
            cursor.execute("""
            INSERT INTO work_items (project_name, work_item_id, rqm_name)
            VALUES (?, ?, ?)
            """, (project_name, work_item_id, rqm_name))
            
            
def get_rqm_data(db_path, project_name, item_id):
    with db_cursor(db_path) as cursor:
        cursor.execute(RQM_ITEM_DATA_TABLE)
        cursor.execute("""
            SELECT work_item_history, work_item_comments, work_item_commits 
            FROM rqm_item_data 
            WHERE project = ? AND item_id = ?
        """, (project_name, item_id))
        result = cursor.fetchone()
        if result:
            return {
                "work_item_history": result[0],
                "work_item_comments": result[1],
                "work_item_commits": result[2]
            }
        else:
            return None
        
def save_rqm_data(db_path, project_name, item_id, work_item_history, work_item_comments, work_item_commits):
    with db_cursor(db_path) as cursor:
        cursor.execute(RQM_ITEM_DATA_TABLE)
        cursor.execute("""
            INSERT INTO rqm_item_data (project, item_id, work_item_history, work_item_comments, work_item_commits)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project, item_id) DO UPDATE SET
            work_item_history=excluded.work_item_history,
            work_item_comments=excluded.work_item_comments,
            work_item_commits=excluded.work_item_commits
        """, (project_name, item_id, work_item_history, work_item_comments, work_item_commits))