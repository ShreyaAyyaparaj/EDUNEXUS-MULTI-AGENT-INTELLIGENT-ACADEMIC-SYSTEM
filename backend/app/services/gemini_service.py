import json

from google import genai
from google.genai import types

from app.db.database import settings


class GeminiService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        # Verified working model for the current API key.
        self.model = "models/gemini-3.5-flash-lite"

    def _generate_json(self, prompt: str) -> dict:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        try:
            return json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Gemini returned invalid JSON: {response.text}"
            ) from exc

    def parse_attendance(self, text: str) -> dict:

        prompt = f"""
You are an academic attendance data extraction system.

Extract attendance information from the faculty's message.

Return ONLY valid JSON with exactly this structure:

{{
    "subject_code": null,
    "date": null,
    "period": null,
    "section": null,
    "absent_student_ids": []
}}

Rules:

1. Extract subject_code if present.
2. Extract date if explicitly provided.
3. Date must use YYYY-MM-DD format.
4. Extract period as an integer if present.
5. Extract section if present.
6. Section must be A or B.
7. Extract all absent student register numbers.
8. Do not invent missing information.
9. Use null when information is not present.
10. Return only JSON.
11. Do not include explanations.

Faculty message:

{text}
"""

        return self._generate_json(prompt)

    def parse_marks(self, text: str) -> dict:

        prompt = f"""
You are an academic marks data extraction system.

Extract marks information from the faculty's message.

Return ONLY valid JSON with exactly this structure:

{{
    "assessment_name": null,
    "assessment_type": null,
    "subject_code": null,
    "max_marks": null,
    "records": []
}}

Each record must have this structure:

{{
    "register_number": "string",
    "marks": 0
}}

Rules:

1. Extract the subject code.
2. Extract the assessment name.
3. Extract assessment type if explicitly provided.
4. Extract maximum marks if provided.
5. Extract every student's register number.
6. Extract every student's marks.
7. Marks must be numeric.
8. Preserve register numbers exactly.
9. Do not invent information.
10. If information is missing, use null.
11. Return an empty records list if there are no student marks.
12. Return ONLY JSON.
13. Do not include explanations.

Faculty message:

{text}
"""

        return self._generate_json(prompt)


gemini_service = GeminiService()
