# Lambda Layers

The `shared/` folder is packaged as a Lambda Layer during deployment.
It provides common utilities (db, llm, sqs, config) to all functions.

## Build Layer

```bash
cd ../shared
pip install -r requirements.txt -t python/
zip -r layer.zip python/
```

Upload the zip as a Lambda Layer or let CDK handle it automatically.
