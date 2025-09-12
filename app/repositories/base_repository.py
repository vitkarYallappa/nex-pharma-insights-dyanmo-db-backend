"""
Simplified Base Repository - Only 4 Essential Methods
Clean and minimal repository with just the required methods
"""

from abc import ABC
from typing import Dict, List, Optional, Any
from decimal import Decimal
from app.core.database import dynamodb_client
from app.core.logging import get_logger
from boto3.dynamodb.conditions import Attr

class BaseRepository(ABC):
    """Simplified base repository with only 4 essential methods"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._table = None
        self.logger = get_logger(f"repository.{table_name}")
    
    @property
    def table(self):
        """Lazy load table to avoid initialization errors"""
        if self._table is None:
            try:
                self._table = dynamodb_client.get_table(self.table_name)
            except Exception as e:
                self.logger.error(f"Failed to get table {self.table_name}: {str(e)}")
                raise Exception(f"Table {self.table_name} not found. Please run migrations first.")
        return self._table
    
    def _build_filter_expression(self, query: Dict[str, Any]):
        """Build DynamoDB filter expression from query dict"""
        if not query:
            return None
            
        filter_expression = None
        for field, value in query.items():
            condition = Attr(field).eq(value)
            if filter_expression is None:
                filter_expression = condition
            else:
                filter_expression = filter_expression & condition
        return filter_expression
    
    async def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item"""
        try:
            self.table.put_item(Item=item)
            self.logger.info(f"Created item in {self.table_name}")
            return item
        except Exception as e:
            self.logger.error(f"Create failed in {self.table_name}: {str(e)}")
            raise Exception(f"Error creating item: {str(e)}")
    
    async def find_one_by_query(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find single item by query filters"""
        try:
            self.logger.debug(f"Find one query in {self.table_name} - Query: {query}")
            
            # If querying by primary key 'pk', use get_item for better performance
            if len(query) == 1 and 'pk' in query:
                self.logger.debug(f"Using get_item for primary key lookup: {query['pk']}")
                response = self.table.get_item(Key={'pk': query['pk']})
                result = response.get('Item')
                self.logger.info(f"Find one by pk in {self.table_name} - Found: {result is not None}")
                if result:
                    self.logger.debug(f"Found item: {result}")
                return result
            
            # For other queries, use scan with filter
            filter_expression = self._build_filter_expression(query)
            self.logger.debug(f"Filter expression: {filter_expression}")
            
            if filter_expression:
                # Don't use Limit=1 with filters as scan might not find the item
                # Instead, scan all and take first match
                response = self.table.scan(FilterExpression=filter_expression)
                items = response.get('Items', [])
                result = items[0] if items else None
                
                # Handle pagination if needed
                while 'LastEvaluatedKey' in response and not result:
                    response = self.table.scan(
                        FilterExpression=filter_expression,
                        ExclusiveStartKey=response['LastEvaluatedKey']
                    )
                    items = response.get('Items', [])
                    result = items[0] if items else None
            else:
                response = self.table.scan(Limit=1)
                items = response.get('Items', [])
                result = items[0] if items else None
            
            self.logger.info(f"Find one query in {self.table_name} - Found: {result is not None}")
            if result:
                self.logger.debug(f"Found item: {result}")
            else:
                self.logger.debug(f"No items found. Response: {response}")
            return result
        except Exception as e:
            self.logger.error(f"Find one failed in {self.table_name}: {str(e)}")
            raise Exception(f"Error finding item: {str(e)}")
    
    async def find_all_by_query(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all items by query filters (optional)"""
        try:
            scan_kwargs = {}
            
            # Add filter if query provided
            if query:
                filter_expression = self._build_filter_expression(query)
                if filter_expression:
                    scan_kwargs['FilterExpression'] = filter_expression
            
            # DynamoDB Limit applies to items examined, not filtered results
            # When using filters, we need to scan without limit and apply limit in code
            if query and limit:
                # Scan without limit when filters are present
                all_items = []
                response = self.table.scan(**scan_kwargs)
                all_items.extend(response.get('Items', []))
                
                # Handle pagination to get all matching items
                while 'LastEvaluatedKey' in response and len(all_items) < limit * 10:  # Reasonable upper bound
                    scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                    response = self.table.scan(**scan_kwargs)
                    all_items.extend(response.get('Items', []))
                
                # Apply limit in application code
                items = all_items[:limit]
            else:
                # No filters or no limit - use DynamoDB limit directly
                if limit and not query:
                    scan_kwargs['Limit'] = limit
                
                response = self.table.scan(**scan_kwargs)
                items = response.get('Items', [])
            
            self.logger.info(f"Find all query in {self.table_name} - Items: {len(items)}")
            return items
        except Exception as e:
            self.logger.error(f"Find all failed in {self.table_name}: {str(e)}")
            raise Exception(f"Error getting items: {str(e)}")
    
    async def update_by_query(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update item by query - finds first match and updates it"""
        try:
            # First find the item
            item = await self.find_one_by_query(query)
            if not item:
                self.logger.warning(f"No item found to update in {self.table_name}")
                return None
            
            # Update the item - handle case where item might be a model object
            if hasattr(item, 'to_dict'):
                item_dict = item.to_dict()
            elif isinstance(item, dict):
                item_dict = item
            else:
                item_dict = dict(item)
            
            updated_item = {**item_dict, **update_data}
            
            # Convert float values to Decimal for DynamoDB compatibility
            for key, value in updated_item.items():
                if isinstance(value, float):
                    updated_item[key] = Decimal(str(value))
            
            self.table.put_item(Item=updated_item)
            
            self.logger.info(f"Updated item in {self.table_name}")
            return updated_item
        except Exception as e:
            self.logger.error(f"Update failed in {self.table_name}: {str(e)}")
            raise Exception(f"Error updating item: {str(e)}")
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if an item exists matching the query"""
        try:
            item = await self.find_one_by_query(query)
            exists = item is not None
            self.logger.debug(f"Exists check in {self.table_name} - Found: {exists}")
            return exists
        except Exception as e:
            self.logger.error(f"Exists check failed in {self.table_name}: {str(e)}")
            raise Exception(f"Error checking if item exists: {str(e)}")
    
    async def count_by_query(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count items matching the query without retrieving all data"""
        try:
            self.logger.debug(f"Count query in {self.table_name} - Query: {query}")
            
            scan_kwargs = {'Select': 'COUNT'}
            
            # Add filter if query provided
            if query:
                filter_expression = self._build_filter_expression(query)
                if filter_expression:
                    scan_kwargs['FilterExpression'] = filter_expression
            
            # Scan and count items
            total_count = 0
            response = self.table.scan(**scan_kwargs)
            total_count += response.get('Count', 0)
            
            # Handle pagination to get complete count
            while 'LastEvaluatedKey' in response:
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = self.table.scan(**scan_kwargs)
                total_count += response.get('Count', 0)
            
            self.logger.info(f"Count query in {self.table_name} - Total: {total_count}")
            return total_count
            
        except Exception as e:
            self.logger.error(f"Count failed in {self.table_name}: {str(e)}")
            raise Exception(f"Error counting items: {str(e)}")