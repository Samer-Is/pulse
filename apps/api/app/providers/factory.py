"""Provider factory for creating AI provider instances."""

import os
from typing import Optional

from .base import BaseProvider, ProviderType
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_vertex_provider import GoogleVertexProvider


class ProviderFactory:
    """Factory for creating provider instances."""

    _instances: dict[ProviderType, BaseProvider] = {}

    @classmethod
    def get_provider(
        cls,
        provider_type: ProviderType,
        api_key: Optional[str] = None,
    ) -> BaseProvider:
        """
        Get or create a provider instance.
        
        Args:
            provider_type: Type of provider
            api_key: Optional API key (uses env var if not provided)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider configuration is missing
        """
        # Return cached instance if available
        if provider_type in cls._instances:
            return cls._instances[provider_type]

        # Create new provider instance
        if provider_type == ProviderType.OPENAI:
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI_API_KEY not configured")
            provider = OpenAIProvider(api_key=key)

        elif provider_type == ProviderType.ANTHROPIC:
            key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            provider = AnthropicProvider(api_key=key)

        elif provider_type == ProviderType.GOOGLE:
            sa_json = api_key or os.getenv("GCP_VERTEX_SA_JSON")
            project_id = os.getenv("GCP_VERTEX_PROJECT_ID")
            location = os.getenv("GCP_VERTEX_LOCATION", "us-central1")
            
            if not sa_json or not project_id:
                raise ValueError(
                    "GCP_VERTEX_SA_JSON and GCP_VERTEX_PROJECT_ID not configured"
                )
            
            provider = GoogleVertexProvider(
                service_account_json=sa_json,
                project_id=project_id,
                location=location,
            )

        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        # Cache the instance
        cls._instances[provider_type] = provider
        return provider

    @classmethod
    def clear_cache(cls):
        """Clear provider cache (useful for testing)."""
        cls._instances.clear()


def get_provider(
    provider_type: ProviderType,
    api_key: Optional[str] = None,
) -> BaseProvider:
    """
    Convenience function to get a provider instance.
    
    Args:
        provider_type: Type of provider
        api_key: Optional API key
        
    Returns:
        Provider instance
    """
    return ProviderFactory.get_provider(provider_type, api_key)

