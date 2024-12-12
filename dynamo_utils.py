import logging
from typing import Optional, List, Dict
import boto3
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.types import TypeDeserializer
from datetime import datetime
from bedrock_utils import get_secret

logger = logging.getLogger(__name__)
deserializer = TypeDeserializer()

def init_dynamodb():
    """Initialize and return DynamoDB resource"""
    try:
        # Get secrets from AWS Secrets Manager
        secrets = get_secret()
        if not secrets:
            raise Exception("Failed to get secrets from AWS Secrets Manager")
        
        # Set default region if not specified in secrets
        region = secrets.get('AWS_REGION', 'us-east-1')
        
        # Common AWS credentials
        aws_config = {
            'aws_access_key_id': secrets.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': secrets.get('AWS_SECRET_ACCESS_KEY'),
            'region_name': region
        }
        
        # Initialize DynamoDB resource with explicit configuration
        dynamodb = boto3.resource('dynamodb', **aws_config)
        
        return dynamodb
        
    except Exception as e:
        logger.error(f"Error initializing DynamoDB: {str(e)}")
        raise e

def get_customer_orders(dynamodb, first_name: str, last_name: str) -> Optional[List[Dict]]:
    """
    Retrieve customer orders from DynamoDB by customer name
    Returns None if customer not found
    """
    table = dynamodb.Table('Rivertownball-cus')
    
    try:
        # Convert input names to title case for consistency
        first_name = first_name.title()
        last_name = last_name.title()
        
        logger.info(f"Querying DynamoDB for {first_name} {last_name}")
        
        response = table.scan(
            FilterExpression='#fn = :fn and #ln = :ln',
            ExpressionAttributeNames={
                '#fn': 'first_name',
                '#ln': 'last_name'
            },
            ExpressionAttributeValues={
                ':fn': first_name,
                ':ln': last_name
            }
        )
        
        logger.debug(f"Raw DynamoDB response: {response}")
        
        items = response.get('Items', [])
        logger.info(f"Found {len(items)} matching customers")
        
        if not items:
            logger.info("No customer found")
            return None
            
        customer = items[0]
        logger.debug(f"Customer data: {customer}")
        
        orders = []
        if 'orders' in customer:
            order_list = customer['orders']
            logger.debug(f"Raw orders data: {order_list}")
            
            for order in order_list:
                try:
                    # Convert date to more readable format
                    date_obj = datetime.strptime(order['order_date'], '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    
                    processed_order = {
                        'order_id': order['order_id'],
                        'product': order['product'],
                        'quantity': int(order['quantity']),
                        'order_date': formatted_date,
                        'total_price': float(order['total_price'])
                    }
                    logger.debug(f"Processed order: {processed_order}")
                    orders.append(processed_order)
                except Exception as e:
                    logger.error(f"Error processing order: {e}")
                    logger.error(f"Problem order data: {order}")
                    continue
            
            logger.info(f"Successfully processed {len(orders)} orders")
            return orders
        
        logger.info("No orders found in customer record")
        return []
        
    except Exception as e:
        logger.error(f"Error querying DynamoDB: {e}", exc_info=True)
        return None
