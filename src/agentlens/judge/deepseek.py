from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from .rubric import load_rubric

load_dotenv()


class DeepSeekJudge:
    """
    LLM-as-a-Judge using the DeepSeek API.
    """

    def __init__(self, model: str | None = None):
        api_key = os.getenv("DEEPSEEK_API_KEY")

        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not found. "
                "Please configure it in your .env file."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv(
                "DEEPSEEK_BASE_URL",
                "https://api.deepseek.com",
            ),
        )

        self.model = (
            model
            or os.getenv(
                "DEEPSEEK_MODEL",
                "deepseek-chat",
            )
        )

    def judge(
        self,
        prompt: str,
        answer: str,
        rubric_path: str = "rubrics/default.yaml",
    ) -> dict:
        """
        Evaluate an answer using the configured YAML rubric.
        """

        rubric = load_rubric(rubric_path)

        system_prompt = f"""
You are an expert evaluator.

Evaluate the agent's answer according to this rubric.

Rubric:
{json.dumps(rubric, indent=2)}

Return ONLY valid JSON.

Required format:

{{
    "score": 0.0,
    "passed": true,
    "reason": "Short explanation",
    "dimensions": {{
        "task_completion": {{
            "score": 0,
            "justification": ""
        }},
        "correctness": {{
            "score": 0,
            "justification": ""
        }},
        "groundedness": {{
            "score": 0,
            "justification": ""
        }},
        "reasoning": {{
            "score": 0,
            "justification": ""
        }},
        "safety": {{
            "score": 0,
            "justification": ""
        }}
    }}
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"Prompt:\n{prompt}\n\n"
                        f"Answer:\n{answer}"
                    ),
                },
            ],
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "DeepSeek returned invalid JSON.\n\n"
                f"{content}"
            ) from exc