import aws_cdk as core
import aws_cdk.assertions as assertions

from lab_ecomerce_sqs.lab_ecomerce_sqs_stack import LabEcomerceSqsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in lab_ecomerce_sqs/lab_ecomerce_sqs_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LabEcomerceSqsStack(app, "lab-ecomerce-sqs")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
