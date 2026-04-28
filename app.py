#!/usr/bin/env python3
import os
import aws_cdk as cdk

# Importamos nuestro stack (que definiremos en el archivo ecommerce_stack.py)
from lab_ecomerce_sqs.lab_ecomerce_sqs_stack import EcommerceSqsStack

app = cdk.App()

# Instanciamos el stack de nuestra arquitectura de e-commerce
EcommerceSqsStack(app, "EcommerceSqsStack",
    # Si deseas desplegar en una región o cuenta específica, descomenta la siguiente línea:
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()