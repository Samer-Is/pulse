"""AWS Secrets Manager integration."""

import os
import json
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any


def get_secret(secret_name: str, region: Optional[str] = None) -> str:
    """
    Get secret from AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret
        region: AWS region (defaults to env AWS_REGION)
        
    Returns:
        Secret value
        
    Raises:
        Exception: If secret cannot be retrieved
    """
    region = region or os.getenv("AWS_REGION", "eu-central-1")
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region,
    )
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise Exception(f"Failed to retrieve secret {secret_name}: {str(e)}")
    
    # Secrets Manager returns the secret as a string
    if "SecretString" in get_secret_value_response:
        return get_secret_value_response["SecretString"]
    else:
        # Binary secrets (not typically used for API keys)
        import base64
        return base64.b64decode(get_secret_value_response["SecretBinary"]).decode("utf-8")


def load_secrets_to_env() -> None:
    """
    Load secrets from AWS Secrets Manager to environment variables.
    
    This function loads all API keys and secrets needed for the application.
    It only loads secrets if they're not already set in the environment.
    """
    # Skip in local development if secrets are already set
    if os.getenv("SKIP_SECRETS_MANAGER") == "true":
        print("Skipping AWS Secrets Manager (local development mode)")
        return
    
    secret_mappings = {
        "pulse/openai-api-key": "OPENAI_API_KEY",
        "pulse/anthropic-api-key": "ANTHROPIC_API_KEY",
        "pulse/gcp-vertex-project-id": "GCP_VERTEX_PROJECT_ID",
        "pulse/gcp-vertex-location": "GCP_VERTEX_LOCATION",
        "pulse/gcp-vertex-sa-json": "GCP_VERTEX_SA_JSON",
        "pulse/google-oauth-client-id": "GOOGLE_OAUTH_CLIENT_ID",
        "pulse/google-oauth-client-secret": "GOOGLE_OAUTH_CLIENT_SECRET",
        "pulse/google-redirect-uri": "GOOGLE_REDIRECT_URI",
        "pulse/jwt-secret": "JWT_SECRET",
        "pulse/runway-api-key": "RUNWAY_API_KEY",
        "pulse/pika-api-key": "PIKA_API_KEY",
    }
    
    for secret_name, env_var in secret_mappings.items():
        # Skip if already set in environment
        if os.getenv(env_var):
            continue
        
        try:
            secret_value = get_secret(secret_name)
            os.environ[env_var] = secret_value
            print(f"Loaded secret: {env_var}")
        except Exception as e:
            print(f"Warning: Could not load secret {secret_name}: {str(e)}")
            # Don't fail on missing secrets during development
            pass


def get_all_secrets_as_dict() -> Dict[str, Any]:
    """
    Get all application secrets as a dictionary.
    
    Useful for debugging and verification (sanitize before logging!)
    
    Returns:
        Dictionary of secret names to boolean indicating if they're set
    """
    secret_keys = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GCP_VERTEX_PROJECT_ID",
        "GCP_VERTEX_LOCATION",
        "GCP_VERTEX_SA_JSON",
        "GOOGLE_OAUTH_CLIENT_ID",
        "GOOGLE_OAUTH_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI",
        "JWT_SECRET",
        "RUNWAY_API_KEY",
        "PIKA_API_KEY",
    ]
    
    return {
        key: bool(os.getenv(key))
        for key in secret_keys
    }

