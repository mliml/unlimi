"""
Intent Classifier module for identifying user message intent.

This module provides intent classification to detect:
- NORMAL: Regular conversation
- END_SESSION: User wants to end the session
- CRISIS: User expresses suicide/self-harm risk
"""
import json
import logging
from typing import Any

from app.schemas.intent import IntentResult

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Classifier for user message intent using LLM.

    This classifier analyzes user messages and session context to determine
    the user's intent, enabling appropriate routing and crisis detection.
    """

    def __init__(self, llm_service: Any):
        """
        Initialize the intent classifier.

        Args:
            llm_service: LLM service instance with chat() method
        """
        self.llm_service = llm_service

    def classify_intent(self, user_message: str, session_state: dict) -> IntentResult:
        """
        Classify the intent of a user message.

        Args:
            user_message: The user's input message
            session_state: Current session state containing:
                - elapsed_minutes: Minutes since session start
                - near_end: Boolean indicating if session is near end

        Returns:
            IntentResult: Classification result with intent type and confidence

        Examples:
            >>> classifier.classify_intent("I want to end this session", {"elapsed_minutes": 10, "near_end": False})
            IntentResult(intent="END_SESSION", confidence=0.95)
        """
        try:
            # Build the prompt for intent classification
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(user_message, session_state)

            # Call LLM for classification
            response = self.llm_service.generate_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o-mini",
                temperature=0
            )

            # Parse LLM response
            result = self._parse_response(response)
            logger.info(f"Intent classified as {result.intent} with confidence {result.confidence}")
            return result

        except Exception as e:
            logger.error(f"Error during intent classification: {str(e)}", exc_info=True)
            # Fallback to safe default
            return IntentResult(intent="NORMAL", confidence=0.0)

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for intent classification.

        Returns:
            System prompt string
        """
        return """You are an intent classifier for a therapy chatbot system.

Your task is to analyze user messages and classify them into one of three intents:

1. NORMAL: Regular conversation, questions, sharing feelings, seeking support
2. END_SESSION: User explicitly wants to end or stop the session
   - Examples: "I want to end this", "Let's stop here", "I'm done for today"
3. CRISIS: User expresses thoughts of suicide, self-harm, or severe harm to others
   - Examples: Suicidal ideation, plans to hurt self or others, severe immediate risk

You must respond with ONLY a JSON object in this exact format:
{"intent": "NORMAL|END_SESSION|CRISIS", "confidence": 0.XX}

Where confidence is a float between 0.0 and 1.0.

Guidelines:
- Be conservative with CRISIS classification (only for genuine risk)
- END_SESSION requires explicit intent to stop/end the conversation
- Most messages should be NORMAL
- Consider session context when available
- Output ONLY the JSON, no additional text"""

    def _build_user_prompt(self, user_message: str, session_state: dict) -> str:
        """
        Build the user prompt with message and context.

        Args:
            user_message: The user's message
            session_state: Session context

        Returns:
            User prompt string
        """
        elapsed = session_state.get("elapsed_minutes", 0)
        near_end = session_state.get("near_end", False)

        return f"""Classify this user message:

User message: "{user_message}"

Session context:
- Elapsed time: {elapsed} minutes
- Near session end: {near_end}

Respond with JSON only: {{"intent": "...", "confidence": 0.XX}}"""

    def _parse_response(self, response: str) -> IntentResult:
        """
        Parse LLM response into IntentResult.

        Args:
            response: Raw LLM response string

        Returns:
            IntentResult with parsed intent and confidence

        Falls back to NORMAL with 0.0 confidence if parsing fails.
        """
        try:
            # Try to parse as JSON
            data = json.loads(response.strip())

            # Extract intent and confidence
            intent = data.get("intent", "NORMAL")
            confidence = float(data.get("confidence", 0.0))

            # Validate intent value
            if intent not in ["NORMAL", "END_SESSION", "CRISIS"]:
                logger.warning(f"Invalid intent '{intent}', defaulting to NORMAL")
                intent = "NORMAL"
                confidence = 0.0

            # Validate confidence range
            confidence = max(0.0, min(1.0, confidence))

            return IntentResult(intent=intent, confidence=confidence)

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {str(e)}. Response: {response}")
            # Fallback to safe default
            return IntentResult(intent="NORMAL", confidence=0.0)
