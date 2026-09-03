import asyncio
import base64

import httpx

import config
from model import groq_client


async def describe_image(url: str) -> str:
    """Return a short description of the image at `url`, or '' on failure."""
    try:
        async with httpx.AsyncClient() as http:
            r = await http.get(url, timeout=10)
            r.raise_for_status()
            image_data = base64.standard_b64encode(r.content).decode("utf-8")
            content_type = (
                r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
            )

        response = await asyncio.to_thread(
            lambda: groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{image_data}"
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Describe this image concisely for a casual "
                                    "group chat context. 1-2 sentences max."
                                ),
                            },
                        ],
                    }
                ],
                max_tokens=150,
            )
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Image description error: {e}")
        return ""
