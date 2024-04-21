from datetime import datetime
from time import sleep
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai import client
from google.generativeai.types import content_types
from google.generativeai.types import generation_types


# https://ai.google.dev/docs/safety_setting_gemini
SAFETY_SETTINGS = [
    # new settings
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    }
]


GENERATE_CONTENT_ASYNC_TIMEOUT = 60 * 5  # 5 minutes
GENERATE_CONTENT_NOT_ASYNC_TIMEOUT = 60 * 7  # 5 minutes
GEMINI_GET_RESPONSE_MAX_RETRIES = 5  # 5 seconds
GEMINI_GET_RESPONSE_DELAY_TIME = 10  # 1 second


def gemini_text_response(
        responses,
        start_time: datetime,
        timeout: int,
        retry_number: int = 0,
        delay_time: int = GEMINI_GET_RESPONSE_DELAY_TIME,
        max_retries: int = GEMINI_GET_RESPONSE_MAX_RETRIES,
        is_async: bool = False,
):
    if (datetime.now() - start_time).total_seconds() > timeout:
        return None
    try:
        if is_async:
            sleep(delay_time)
        try:
            full_response_text = ''
            for response in responses:
                if response.text:
                    full_response_text += response.text
        except Exception as e:
            full_response_text = ''
            for response in responses:
                for part in response.parts:
                    full_response_text += part.text
        return full_response_text
    except Exception as ex:
        if retry_number >= max_retries or '503' not in str(ex) or '504' not in str(ex) or '400' in str(
                ex) or not is_async:
            return None
        print(f"Gemini retry number: {retry_number + 1}")
        return gemini_text_response(responses=responses, retry_number=retry_number + 1, delay_time=delay_time,
                                    start_time=start_time, timeout=timeout)


class CustomGenerativeModel(GenerativeModel):
    def custom_generate_content(
            self,
            contents: content_types.ContentsType,
            *,
            generation_config=None,
            safety_settings=None,
            stream: bool = False,
            timeout: int = 60 * 10,  # 10 minutes
            **kwargs,
    ) -> generation_types.GenerateContentResponse:
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=SAFETY_SETTINGS if safety_settings is None else safety_settings,
            **kwargs,
        )
        if self._client is None:
            self._client = client.get_default_generative_client()

        if stream:
            with generation_types.rewrite_stream_error():
                iterator = self._client.stream_generate_content(request, timeout=timeout)
            return generation_types.GenerateContentResponse.from_iterator(iterator)
        else:
            response = self._client.generate_content(request, timeout=timeout)
            return generation_types.GenerateContentResponse.from_response(response)

    async def custom_generate_content_async(
            self,
            contents: content_types.ContentsType,
            *,
            generation_config=None,
            safety_settings=None,
            stream: bool = False,
            timeout: int = 60 * 10,  # 10 minutes
            **kwargs,
    ) -> generation_types.AsyncGenerateContentResponse:
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            **kwargs,
        )
        if self._async_client is None:
            self._async_client = client.get_default_generative_async_client()

        if stream:
            with generation_types.rewrite_stream_error():
                iterator = await self._async_client.stream_generate_content(request, timeout=timeout)
            return await generation_types.AsyncGenerateContentResponse.from_aiterator(iterator)
        else:
            response = await self._async_client.generate_content(request, timeout=timeout)
            return generation_types.AsyncGenerateContentResponse.from_response(response)


class CustomGemini:
    def __init__(self):
        self.model = None
        self.gen_key = None

    def set_key(self, gen_key: str):
        self.gen_key = genai.configure(api_key=gen_key)

    def set_model(self, gen_model: str = 'gemini-pro'):
        self.model = CustomGenerativeModel(gen_model)

    def custom_generate_content(
            self, prompt: str,
            max_output_tokens: int = 8192,
            temperature: float = 0,
            top_p: int = 1,
            timeout: int = GENERATE_CONTENT_ASYNC_TIMEOUT
    ):
        try:
            responses = self.model.custom_generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_output_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                },
                stream=False,
                timeout=GENERATE_CONTENT_NOT_ASYNC_TIMEOUT
            )
            full_response_text = gemini_text_response(
                responses=responses,
                timeout=GENERATE_CONTENT_NOT_ASYNC_TIMEOUT,
                start_time=datetime.now()
            )
            if not full_response_text:
                print('Gemini response is None. Trying to get response async')
                responses = self.model.custom_generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": max_output_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                    },
                    stream=True,
                    timeout=timeout
                )
                full_response_text = gemini_text_response(
                    responses=responses, is_async=True,
                    timeout=timeout,
                    start_time=datetime.now()
                )

            return full_response_text
        except Exception as ex:
            print('an error chat CustomGemini:', ex)
            return None


gemini = CustomGemini()
gemini.set_key('AIzaSyDYKWbhIrY0iKKUvWBLNj5bKXU3kxbGspw')
gemini.set_model()
# prompt = 'What is the meaning of life?'
prompt = input("Enter a prompt: ")
response = gemini.custom_generate_content(prompt)
print(response)
# pip install google-generativeai==0.3.2
