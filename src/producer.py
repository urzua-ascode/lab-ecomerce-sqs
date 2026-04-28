import json
import boto3
import os
import uuid

# Inicializamos el cliente SQS fuera del handler para reutilizar conexiones (Mejor Práctica)
sqs_client = boto3.client('sqs')
QUEUE_URL = os.environ['QUEUE_URL']

def handler(event, context):
    try:
        # Parseamos el body que viene del API Gateway
        body = json.loads(event.get('body', '{}'))
        
        if not body.get('item') or not body.get('customer'):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Faltan datos de la orden (item o customer)'})
            }
        
        # Generamos un ID único para la orden
        order_id = str(uuid.uuid4())
        
        # Preparamos el mensaje para la cola SQS
        order_message = {
            'orderId': order_id,
            'customer': body['customer'],
            'item': body['item'],
            'quantity': body.get('quantity', 1),
            'status': 'PENDING'
        }
        
        # Enviamos el mensaje a SQS
        response = sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(order_message)
        )
        
        # Respondemos de inmediato al cliente (La API no espera a que se guarde en BD)
        return {
            'statusCode': 202, # 202 Accepted es ideal para procesos asíncronos
            'body': json.dumps({
                'message': 'Orden recibida y encolada para procesamiento',
                'orderId': order_id,
                'sqsMessageId': response['MessageId']
            })
        }
        
    except Exception as e:
        print(f"Error en el Productor: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error interno del servidor'})
        }