import json
import re
from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class ScrapedDocument:
    url: str
    summary: str
    main_topic: str
    key_points: List[str]
    structured_data: Dict[str, Any]
    metadata: Dict[str, Any]
    sources: List[str]
    raw_content: Optional[str] = None
    
    def __str__(self) -> str:
        """Return a pretty-printed JSON representation of the document."""
        return json.dumps({
            "url": self.url,
            "summary": self.summary,
            "main_topic": self.main_topic,
            "key_points": self.key_points,
            "structured_data": self.structured_data,
            "metadata": self.metadata,
            "sources": self.sources,
            "raw_content": self.raw_content
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_data: str) -> "ScrapedDocument":
        try:
            cleaned_json = json_data
            
            code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
            match = re.search(code_block_pattern, json_data)
            if match:
                cleaned_json = match.group(1)
            
            data = json.loads(cleaned_json)
            return cls(
                url=data.get("url", ""),
                summary=data.get("summary", ""),
                main_topic=data.get("main_topic", ""),
                key_points=data.get("key_points", []),
                structured_data=data.get("structured_data", {}),
                metadata=data.get("metadata", {}),
                sources=data.get("sources", []),
                raw_content=data.get("raw_content", "")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}\nJSON content: {json_data[:100]}...")
        except KeyError as e:
            raise ValueError(f"Missing required field in JSON data: {e}")
            
    def to_json(self) -> str:
        return json.dumps({
            "url": self.url,
            "summary": self.summary,
            "main_topic": self.main_topic,
            "key_points": self.key_points,
            "structured_data": self.structured_data,
            "metadata": self.metadata,
            "sources": self.sources,
            "raw_content": self.raw_content
        }, indent=2) 