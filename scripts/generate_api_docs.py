#!/usr/bin/env python3
"""Generate API documentation in various formats."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.api.main import app


def generate_openapi_json():
    """Generate OpenAPI JSON schema."""
    schema = app.openapi()
    
    # Save to file
    output_path = Path(__file__).parent.parent / "docs" / "api" / "openapi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ OpenAPI schema saved to {output_path}")
    return schema


def generate_markdown_docs(schema):
    """Generate Markdown documentation from OpenAPI schema."""
    output_path = Path(__file__).parent.parent / "docs" / "api" / "API_REFERENCE.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        # Header
        f.write(f"# {schema['info']['title']} API Reference\n\n")
        f.write(f"Version: {schema['info']['version']}\n\n")
        f.write(schema['info']['description'])
        f.write("\n\n")
        
        # Servers
        f.write("## Servers\n\n")
        for server in schema['servers']:
            f.write(f"- **{server['description']}**: `{server['url']}`\n")
        f.write("\n")
        
        # Authentication
        f.write("## Authentication\n\n")
        f.write("This API uses JWT Bearer token authentication. Include the token in the Authorization header:\n\n")
        f.write("```\nAuthorization: Bearer <your-token>\n```\n\n")
        
        # Endpoints by tag
        paths = schema['paths']
        tags = {}
        
        # Group endpoints by tag
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    tag_list = operation.get('tags', ['Other'])
                    for tag in tag_list:
                        if tag not in tags:
                            tags[tag] = []
                        tags[tag].append((path, method, operation))
        
        # Write endpoints
        f.write("## Endpoints\n\n")
        for tag, endpoints in sorted(tags.items()):
            f.write(f"### {tag}\n\n")
            
            for path, method, operation in endpoints:
                # Operation summary
                f.write(f"#### {operation.get('summary', 'No summary')}\n\n")
                f.write(f"`{method.upper()} {path}`\n\n")
                
                # Description
                if 'description' in operation:
                    f.write(f"{operation['description']}\n\n")
                
                # Parameters
                if 'parameters' in operation:
                    f.write("**Parameters:**\n\n")
                    for param in operation['parameters']:
                        required = "required" if param.get('required', False) else "optional"
                        f.write(f"- `{param['name']}` ({param['in']}, {required}): {param.get('description', 'No description')}\n")
                    f.write("\n")
                
                # Request body
                if 'requestBody' in operation:
                    f.write("**Request Body:**\n\n")
                    content = operation['requestBody'].get('content', {})
                    for content_type, media_type in content.items():
                        if 'schema' in media_type:
                            schema_ref = media_type['schema'].get('$ref', '')
                            if schema_ref:
                                schema_name = schema_ref.split('/')[-1]
                                f.write(f"Content-Type: `{content_type}`\n\n")
                                f.write(f"Schema: `{schema_name}`\n\n")
                    f.write("\n")
                
                # Responses
                f.write("**Responses:**\n\n")
                for status_code, response in operation.get('responses', {}).items():
                    f.write(f"- `{status_code}`: {response.get('description', 'No description')}\n")
                f.write("\n---\n\n")
    
    print(f"✅ Markdown documentation saved to {output_path}")


def generate_postman_collection(schema):
    """Generate Postman collection from OpenAPI schema."""
    collection = {
        "info": {
            "name": schema['info']['title'],
            "description": schema['info']['description'],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "baseUrl",
                "value": schema['servers'][0]['url'],
                "type": "string"
            },
            {
                "key": "accessToken",
                "value": "",
                "type": "string"
            }
        ]
    }
    
    # Group by tags
    tag_folders = {}
    
    for path, methods in schema['paths'].items():
        for method, operation in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete']:
                tags = operation.get('tags', ['Other'])
                
                for tag in tags:
                    if tag not in tag_folders:
                        tag_folders[tag] = {
                            "name": tag,
                            "item": []
                        }
                    
                    # Create Postman request
                    request = {
                        "name": operation.get('summary', path),
                        "request": {
                            "method": method.upper(),
                            "header": [],
                            "url": {
                                "raw": "{{baseUrl}}" + path,
                                "host": ["{{baseUrl}}"],
                                "path": path.strip('/').split('/')
                            },
                            "description": operation.get('description', '')
                        }
                    }
                    
                    # Add auth header if needed
                    if 'security' in operation:
                        request['request']['header'].append({
                            "key": "Authorization",
                            "value": "Bearer {{accessToken}}",
                            "type": "text"
                        })
                    
                    # Add request body if present
                    if 'requestBody' in operation:
                        content = operation['requestBody'].get('content', {})
                        if 'application/json' in content:
                            request['request']['body'] = {
                                "mode": "raw",
                                "raw": json.dumps({"example": "data"}, indent=2),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            }
                    
                    tag_folders[tag]['item'].append(request)
    
    # Add folders to collection
    collection['item'] = list(tag_folders.values())
    
    # Save collection
    output_path = Path(__file__).parent.parent / "docs" / "api" / "postman_collection.json"
    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)
    
    print(f"✅ Postman collection saved to {output_path}")


if __name__ == "__main__":
    print("🚀 Generating API documentation...")
    
    # Generate OpenAPI JSON
    schema = generate_openapi_json()
    
    # Generate Markdown docs
    generate_markdown_docs(schema)
    
    # Generate Postman collection
    generate_postman_collection(schema)
    
    print("\n✨ API documentation generated successfully!")