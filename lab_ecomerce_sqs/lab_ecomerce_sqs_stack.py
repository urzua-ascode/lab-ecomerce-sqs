from aws_cdk import (
    Duration,
    Stack,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_lambda_event_sources as eventsources,
    RemovalPolicy
)
from constructs import Construct

class EcommerceSqsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Base de Datos: DynamoDB
        # Aquí guardaremos el estado final de las órdenes.
        orders_table = dynamodb.Table(
            self, "OrdersTable",
            partition_key=dynamodb.Attribute(name="orderId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY # NOTA: Solo para desarrollo. En prod usar RETAIN.
        )

        # 2. Cola de Mensajes: Amazon SQS
        # El visibility_timeout debe ser mayor o igual al timeout de la Lambda que la consume.
        orders_queue = sqs.Queue(
            self, "OrdersQueue",
            queue_name="ecommerce-orders-queue",
            visibility_timeout=Duration.seconds(30)
        )

        # 3. Función Lambda: Productor (Recibe de API GW y envía a SQS)
        producer_lambda = _lambda.Function(
            self, "OrderProducerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="producer.handler",
            code=_lambda.Code.from_asset("src"),
            environment={
                "QUEUE_URL": orders_queue.queue_url
            }
        )
        # Otorgamos permisos de escritura en la cola (Principio de Mínimo Privilegio)
        orders_queue.grant_send_messages(producer_lambda)

        # 4. API Gateway: Exponemos nuestra Lambda Productora al frontend
        api = apigw.RestApi(
            self, "EcommerceOrdersApi",
            rest_api_name="Servicio de Ordenes E-commerce",
            description="API para procesar órdenes de compra."
        )
        
        # Endpoint: POST /orders
        orders_resource = api.root.add_resource("orders")
        orders_integration = apigw.LambdaIntegration(producer_lambda)
        orders_resource.add_method("POST", orders_integration)

        # 5. Función Lambda: Consumidor (Lee de SQS y escribe en DynamoDB)
        consumer_lambda = _lambda.Function(
            self, "OrderConsumerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="consumer.handler",
            code=_lambda.Code.from_asset("src"),
            timeout=Duration.seconds(10), # Mayor timeout por si hay lógica de negocio pesada
            environment={
                "TABLE_NAME": orders_table.table_name
            }
        )
        
        # Otorgamos permisos de escritura a DynamoDB
        orders_table.grant_write_data(consumer_lambda)
        
        # Conectamos SQS como "Event Source" (Trigger) de nuestra Lambda Consumidora
        # batch_size=5 significa que Lambda procesará hasta 5 mensajes de la cola al mismo tiempo.
        consumer_lambda.add_event_source(
            eventsources.SqsEventSource(orders_queue, batch_size=5)
        )