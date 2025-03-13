from typing import Dict, Any, Optional


class Config:
    def __init__(self, **kwargs):
        self._settings: Dict[str, Any] = {
            "openai_model": "gpt-3.5-turbo",
            "max_retries": 3,
            "retry_delay": 1,
            "timeout": 60,
            "max_tokens_summary": 1000,
            "max_tokens_rag": 4000,
        }
        self._settings.update(kwargs)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value
    
    def update(self, settings: Dict[str, Any]) -> None:
        self._settings.update(settings)
    
    @property
    def settings(self) -> Dict[str, Any]:
        return self._settings.copy() 