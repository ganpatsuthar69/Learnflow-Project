#!/usr/bin/env python3
import aws_cdk as cdk
from stack import LearnFlowLambdaStack

app = cdk.App()
LearnFlowLambdaStack(app, "LearnFlowLambdaStack",
    env=cdk.Environment(region="ap-south-1"),
)
app.synth()
