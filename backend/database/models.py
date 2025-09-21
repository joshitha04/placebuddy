import json
from datetime import datetime
from database.connection import get_db_connection

class UserModel:
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return user
    
    @staticmethod
    def find_by_username_or_email(username, email):
        """Check if user exists by username or email"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return result is not None
    
    @staticmethod
    def create_user(username, email, password_hash):
        """Create new user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        return user_id

class CompanyModel:
    @staticmethod
    def find_by_name(name):
        """Find company by name (case insensitive)"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM companies WHERE LOWER(name) = LOWER(%s) LIMIT 1", (name,))
        company = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return company
    
    @staticmethod
    def create_company(company_data, user_id):
        """Create new company"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO companies (name, description, website, industry, tier, location, 
                              funding_stage, employee_count, revenue, extracted_data, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
       # edit later 
        cursor.execute(query, (
            company_data.get('name'),
            company_data.get('description'),
            company_data.get('website'),
            company_data.get('industry'),
            company_data.get('tier', 'tier3'),
            company_data.get('location'),
            company_data.get('funding_stage'),
            company_data.get('employee_count'),
            company_data.get('revenue'),
            json.dumps(company_data),
            user_id
        ))
        
        company_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return company_id
    
    @staticmethod
    def get_companies_by_user(user_id):
        """Get all companies created by user"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, description, tier, industry, location, website, 
                   funding_stage, employee_count, revenue, created_at 
            FROM companies 
            WHERE created_by = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        
        companies = cursor.fetchall()
        
        # Convert datetime to string
        for company in companies:
            if company['created_at']:
                company['created_at'] = company['created_at'].isoformat()
        
        cursor.close()
        conn.close()
        return companies