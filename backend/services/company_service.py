import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database.models import CompanyModel, UserModel

# Configure logging
logger = logging.getLogger(__name__)

class CompanyService:
    """Service for company-related database operations"""
    
    def process_company(self, company_data: Dict, user_id: int) -> Dict:
        """
        Process company data - check for duplicates and save if new
        
        Args:
            company_data (dict): Extracted company information
            user_id (int): ID of the user adding the company
            
        Returns:
            dict: Result containing company_id and duplicate status
        """
        try:
            company_name = company_data.get('name')
            if not company_name:
                raise ValueError("Company name is required")
            
            # Check if company already exists
            existing_company = CompanyModel.find_by_name(company_name)
            
            if existing_company:
                logger.info(f"Company '{company_name}' already exists with ID: {existing_company['id']}")
                return {
                    'company_id': existing_company['id'],
                    'is_duplicate': True,
                    'message': f"Company '{company_name}' already exists in database"
                }
            
            # Create new company
            company_id = CompanyModel.create_company(company_data, user_id)
            
            logger.info(f"Created new company '{company_name}' with ID: {company_id}")
            return {
                'company_id': company_id,
                'is_duplicate': False,
                'message': f"Successfully added new company '{company_name}'"
            }
            
        except Exception as e:
            logger.error(f"Error processing company: {str(e)}")
            raise e
    
    def get_user_companies(self, user_id: int, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get companies for a specific user with optional filters
        
        Args:
            user_id (int): User ID
            filters (dict): Optional filters (tier, read_status, etc.)
            
        Returns:
            list: List of companies
        """
        try:
            # Get base companies for user
            companies = CompanyModel.get_companies_by_user(user_id)
            
            if not filters:
                return companies
            
            # Apply filters
            filtered_companies = []
            for company in companies:
                # Filter by tier
                if filters.get('tier') and company['tier'] != filters['tier']:
                    continue
                
                # Add read status if needed
                if filters.get('read_status'):
                    is_read = self.is_company_read(user_id, company['id'])
                    company['is_read'] = is_read
                    
                    if filters['read_status'] == 'read' and not is_read:
                        continue
                    if filters['read_status'] == 'unread' and is_read:
                        continue
                
                filtered_companies.append(company)
            
            return filtered_companies
            
        except Exception as e:
            logger.error(f"Error getting user companies: {str(e)}")
            return []
    
    def get_all_companies(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all companies with optional filters
        
        Args:
            filters (dict): Optional filters
            
        Returns:
            list: List of companies
        """
        try:
            # This would need to be implemented in CompanyModel
            # For now, return empty list
            logger.warning("get_all_companies not implemented in CompanyModel")
            return []
            
        except Exception as e:
            logger.error(f"Error getting all companies: {str(e)}")
            return []
    
    def mark_company_as_read(self, user_id: int, company_id: int) -> bool:
        """
        Mark a company as read for a user
        
        Args:
            user_id (int): User ID
            company_id (int): Company ID
            
        Returns:
            bool: Success status
        """
        try:
            # This would need a ReadStatus model and table
            # For now, just log the action
            logger.info(f"Marking company {company_id} as read for user {user_id}")
            
            # TODO: Implement ReadStatus model and database operations
            # ReadStatusModel.mark_as_read(user_id, company_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking company as read: {str(e)}")
            return False
    
    def is_company_read(self, user_id: int, company_id: int) -> bool:
        """
        Check if a company is marked as read by a user
        
        Args:
            user_id (int): User ID
            company_id (int): Company ID
            
        Returns:
            bool: Read status
        """
        try:
            # TODO: Implement ReadStatus model and check
            # return ReadStatusModel.is_read(user_id, company_id)
            return False  # Default to unread for now
            
        except Exception as e:
            logger.error(f"Error checking read status: {str(e)}")
            return False
    
    def get_company_stats(self, user_id: int) -> Dict:
        """
        Get statistics about companies for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Company statistics
        """
        try:
            companies = CompanyModel.get_companies_by_user(user_id)
            
            total_companies = len(companies)
            tier_stats = {'tier1': 0, 'tier2': 0, 'tier3': 0}
            industry_stats = {}
            
            for company in companies:
                # Count by tier
                tier = company.get('tier', 'tier3')
                if tier in tier_stats:
                    tier_stats[tier] += 1
                
                # Count by industry
                industry = company.get('industry', 'Unknown')
                industry_stats[industry] = industry_stats.get(industry, 0) + 1
            
            return {
                'total_companies': total_companies,
                'tier_breakdown': tier_stats,
                'industry_breakdown': industry_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting company stats: {str(e)}")
            return {
                'total_companies': 0,
                'tier_breakdown': {'tier1': 0, 'tier2': 0, 'tier3': 0},
                'industry_breakdown': {},
                'last_updated': datetime.now().isoformat()
            }
    
    def cleanup_old_companies(self, days: int = 30) -> Dict:
        """
        Clean up old company entries
        
        Args:
            days (int): Number of days to keep companies
            
        Returns:
            dict: Cleanup results
        """
        try:
            # This would need to be implemented in CompanyModel
            # For now, just return mock results
            logger.info(f"Would clean up companies older than {days} days")
            
            # TODO: Implement in CompanyModel
            # result = CompanyModel.cleanup_old_entries(days)
            
            return {
                'deleted_companies': 0,
                'cleanup_date': datetime.now().isoformat(),
                'days_threshold': days
            }
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return {
                'deleted_companies': 0,
                'cleanup_date': datetime.now().isoformat(),
                'days_threshold': days,
                'error': str(e)
            }
    
    def search_companies(self, user_id: int, search_term: str) -> List[Dict]:
        """
        Search companies by name, industry, or description
        
        Args:
            user_id (int): User ID
            search_term (str): Search term
            
        Returns:
            list: Matching companies
        """
        try:
            companies = CompanyModel.get_companies_by_user(user_id)
            search_term_lower = search_term.lower()
            
            matching_companies = []
            for company in companies:
                # Search in name
                if search_term_lower in company.get('name', '').lower():
                    matching_companies.append(company)
                    continue
                
                # Search in industry
                if search_term_lower in company.get('industry', '').lower():
                    matching_companies.append(company)
                    continue
                
                # Search in description
                if search_term_lower in company.get('description', '').lower():
                    matching_companies.append(company)
                    continue
                
                # Search in location
                if search_term_lower in company.get('location', '').lower():
                    matching_companies.append(company)
                    continue
            
            return matching_companies
            
        except Exception as e:
            logger.error(f"Error searching companies: {str(e)}")
            return []
    
    def update_company(self, company_id: int, updates: Dict, user_id: int) -> bool:
        """
        Update company information
        
        Args:
            company_id (int): Company ID
            updates (dict): Fields to update
            user_id (int): User ID (for permission check)
            
        Returns:
            bool: Success status
        """
        try:
            # TODO: Implement update method in CompanyModel
            # Also check if user has permission to update
            logger.info(f"Would update company {company_id} with data: {updates}")
            
            # CompanyModel.update_company(company_id, updates, user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating company: {str(e)}")
            return False
    
    def delete_company(self, company_id: int, user_id: int) -> bool:
        """
        Delete a company (soft delete recommended)
        
        Args:
            company_id (int): Company ID
            user_id (int): User ID (for permission check)
            
        Returns:
            bool: Success status
        """
        try:
            # TODO: Implement delete method in CompanyModel
            # Check if user has permission to delete
            logger.info(f"Would delete company {company_id} by user {user_id}")
            
            # CompanyModel.delete_company(company_id, user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting company: {str(e)}")
            return False
    
    def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """
        Get a specific company by ID
        
        Args:
            company_id (int): Company ID
            
        Returns:
            dict: Company data or None
        """
        try:
            # TODO: Implement get_by_id method in CompanyModel
            # return CompanyModel.get_by_id(company_id)
            
            logger.warning("get_company_by_id not implemented in CompanyModel")
            return None
            
        except Exception as e:
            logger.error(f"Error getting company by ID: {str(e)}")
            return None


class ReadStatusService:
    """Service for managing read/unread status of companies"""
    
    @staticmethod
    def mark_as_read(user_id: int, company_id: int) -> bool:
        """Mark a company as read for a user"""
        try:
            # TODO: Implement ReadStatus model and database table
            logger.info(f"Marking company {company_id} as read for user {user_id}")
            
            # This would require a read_status table with columns:
            # - id (primary key)
            # - user_id (foreign key to users)
            # - company_id (foreign key to companies) 
            # - read_at (timestamp)
            # - created_at (timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking as read: {str(e)}")
            return False
    
    @staticmethod
    def mark_as_unread(user_id: int, company_id: int) -> bool:
        """Mark a company as unread for a user"""
        try:
            logger.info(f"Marking company {company_id} as unread for user {user_id}")
            
            # Remove from read_status table
            # ReadStatusModel.remove_read_status(user_id, company_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking as unread: {str(e)}")
            return False
    
    @staticmethod
    def get_read_status(user_id: int, company_id: int) -> Dict:
        """Get read status information for a company"""
        try:
            # TODO: Query read_status table
            # return ReadStatusModel.get_status(user_id, company_id)
            
            return {
                'is_read': False,
                'read_at': None
            }
            
        except Exception as e:
            logger.error(f"Error getting read status: {str(e)}")
            return {
                'is_read': False,
                'read_at': None
            }
    
    @staticmethod
    def get_user_read_companies(user_id: int) -> List[int]:
        """Get list of company IDs that user has read"""
        try:
            # TODO: Query read_status table
            # return ReadStatusModel.get_read_company_ids(user_id)
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting read companies: {str(e)}")
            return []