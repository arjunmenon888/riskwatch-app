# database.py

import os
import base64
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"FATAL: Could not connect to PostgreSQL database: {e}")
        # In a real app, you might want to exit or handle this more gracefully
        raise

def init_db():
    """Initializes the database and creates the observations table if it doesn't exist."""
    conn = get_db_connection()
    # Use a RealDictCursor to get dictionary-like rows
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Note the changes for PostgreSQL:
        # - SERIAL PRIMARY KEY for auto-incrementing integer
        # - BYTEA for binary data (replaces BLOB)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id SERIAL PRIMARY KEY,
                date_str TEXT NOT NULL,
                floor TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT,
                impact TEXT,
                likelihood INTEGER,
                severity INTEGER,
                risk_rating INTEGER,
                corrective_action TEXT,
                responsible_person TEXT,
                deadline TEXT,
                photo_bytes BYTEA
            )
        ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully (PostgreSQL).")

def add_observation_to_db(entry_data):
    """Adds a new observation record to the database and returns the new ID."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        standardized_floor = entry_data['ai_analysis'].get('StandardizedFloor', entry_data.get('floor_from_user'))
        likelihood = entry_data['ai_analysis'].get('Likelihood', 0)
        severity = entry_data['ai_analysis'].get('Severity', 0)
        
        # Note the use of %s as placeholders for psycopg2
        # Use RETURNING id to get the ID of the new row, as lastrowid is not standard
        sql = '''
            INSERT INTO observations (
                date_str, floor, location, description, impact, 
                likelihood, severity, risk_rating, corrective_action, 
                responsible_person, deadline, photo_bytes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        '''
        cur.execute(sql, (
            entry_data.get('date_str'),
            standardized_floor,
            entry_data.get('location_from_user'),
            entry_data['ai_analysis'].get('CorrectedDescription'),
            entry_data['ai_analysis'].get('ImpactOnOperations'),
            likelihood,
            severity,
            likelihood * severity,
            entry_data['ai_analysis'].get('CorrectiveAction'),
            entry_data['ai_analysis'].get('ResponsiblePerson'),
            entry_data['ai_analysis'].get('DeadlineSuggestion'),
            entry_data.get('photo_bytes')
        ))
        
        # Fetch the returned ID
        last_id = cur.fetchone()[0]
        
    conn.commit()
    conn.close()
    return last_id

def get_observations_from_db(search_term=None, sort_by='date_newest'):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = "SELECT * FROM observations"
        params = []

        if search_term:
            query += " WHERE description ILIKE %s OR location ILIKE %s OR floor ILIKE %s"
            # Note: Using ILIKE for case-insensitive search in PostgreSQL
            params.extend([f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'])
        
        if sort_by == 'date_newest':
            query += " ORDER BY id DESC"
        elif sort_by == 'date_oldest':
            query += " ORDER BY id ASC"
        elif sort_by == 'risk_high':
            query += " ORDER BY risk_rating DESC"
        
        cur.execute(query, params)
        # fetchall() with RealDictCursor returns a list of dictionary-like objects
        observations = cur.fetchall()
        
    conn.close()
    
    # Process photos. psycopg2 returns 'bytea' as bytes, which is what we need.
    for obs in observations:
        if obs['photo_bytes']:
            # The object is already bytes-like, just needs base64 encoding
            obs['photo_b64'] = base64.b64encode(obs['photo_bytes']).decode('utf-8')
        else:
            obs['photo_b64'] = None
            
    return observations

def delete_observation_from_db(observation_id):
    """Deletes an observation record from the database by its ID."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        sql = "DELETE FROM observations WHERE id = %s;"
        cur.execute(sql, (observation_id,))
    conn.commit()
    conn.close()
    print(f"Observation with ID {observation_id} deleted from database.")
