## Copyright Bikatr7 (https://github.com/Bikatr7)
## Use of this source code is governed by a GNU Lesser General Public License v2.1
## license that can be found in the LICENSE file.

## built-in libraries
import typing
import asyncio

## third party libraries
from google.generativeai import GenerationConfig
from google.generativeai.types import GenerateContentResponse, AsyncGenerateContentResponse

import google.generativeai as genai

## custom modules
from .util import _estimate_cost, _convert_iterable_to_str, _is_iterable_of_strings
from .decorators import _async_logging_decorator, _sync_logging_decorator

class GeminiService:

    _default_translation_instructions:str = "Please translate the following text into English."
    _default_model:str = "gemini-pro"

    _system_message = _default_translation_instructions

    _model:str = _default_model
    _temperature:float = 0.5
    _top_p:float = 0.9
    _top_k:int = 40
    _candidate_count:int = 1
    _stream:bool = False
    _stop_sequences:typing.List[str] | None = None
    _max_output_tokens:int | None = None

    _client:genai.GenerativeModel
    _generation_config:GenerationConfig

    _semaphore_value:int = 15
    _semaphore:asyncio.Semaphore = asyncio.Semaphore(_semaphore_value)

    _decorator_to_use:typing.Union[typing.Callable, None] = None

    _log_directory:str | None = None

    ## I don't plan to allow users to change these settings, as I believe that translations should be as accurate as possible, avoiding any censorship or filtering of content.
    _safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
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
        },
    ]

##-------------------start-of-_set_api_key()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _set_api_key(api_key:str) -> None:

        """

        Sets the API key for the Gemini client.

        Parameters:
        api_key (string) : The API key.

        """

        genai.configure(api_key=api_key)

##-------------------start-of-_set_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _set_decorator(decorator:typing.Callable) -> None:

        """

        Sets the decorator to use for the Gemini service. Should be a callable that returns a decorator.

        Parameters:
        decorator (callable) : The decorator to use.

        """

        GeminiService._decorator_to_use = decorator

##-------------------start-of-_set_attributes()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
    @staticmethod
    def _set_attributes(model:str="gemini-pro",
                        system_message:str = _default_translation_instructions,
                        temperature:float=0.5,
                        top_p:float=0.9,
                        top_k:int=40,
                        candidate_count:int=1,
                        stream:bool=False,
                        stop_sequences:typing.List[str] | None=None,
                        max_output_tokens:int | None=None,
                        semaphore:int | None=None,
                        logging_directory:str | None=None
                        ) -> None:
        
        """

        Sets the attributes for the Gemini service.

        """

        GeminiService._model = model
        GeminiService._system_message = system_message
        GeminiService._temperature = temperature
        GeminiService._top_p = top_p
        GeminiService._top_k = top_k
        GeminiService._candidate_count = candidate_count
        GeminiService._stream = stream
        GeminiService._stop_sequences = stop_sequences
        GeminiService._max_output_tokens = max_output_tokens

        ## if a semaphore is not provided, set it to the default value based on the model
        if(semaphore is not None):
            GeminiService._semaphore_value = semaphore

        else:
            GeminiService._semaphore_value = 15 if GeminiService._model != "gemini--1.5-pro-latest" else 2

        GeminiService._log_directory = logging_directory
        
##-------------------start-of-_redefine_client()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _redefine_client() -> None:

        """

        Redefines the Gemini client and generation config. This should be called before making any requests to the Gemini service, or after changing any of the service's settings.

        """

        ## as of now, the only model that allows for system instructions is gemini--1.5-pro-latest
        if(GeminiService._model == "gemini--1.5-pro-latest"):

            GeminiService._client = genai.GenerativeModel(model_name=GeminiService._model,
                                                        safety_settings=GeminiService._safety_settings,
                                                        system_instruction=GeminiService._system_message,
                                                        )
        else:
            GeminiService._client = genai.GenerativeModel(model_name=GeminiService._model,
                                                        safety_settings=GeminiService._safety_settings)


        GeminiService._generation_config = GenerationConfig(candidate_count=GeminiService._candidate_count,
                                                           stop_sequences=GeminiService._stop_sequences,
                                                           max_output_tokens=GeminiService._max_output_tokens,
                                                            temperature=GeminiService._temperature,
                                                            top_p=GeminiService._top_p,
                                                            top_k=GeminiService._top_k)
        
        GeminiService._semaphore = asyncio.Semaphore(GeminiService._semaphore_value)

##-------------------start-of-_redefine_client_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _redefine_client_decorator(func):

        """

        Wraps a function to redefine the Gemini client before doing anything that requires the client.

        Parameters:
        func (callable) : The function to wrap.

        Returns:
        wrapper (callable) : The wrapped function.

        """

        def wrapper(*args, **kwargs):
            GeminiService._redefine_client() 
            return func(*args, **kwargs)
        
        return wrapper
            
##-------------------start-of-_translate_text_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @_redefine_client_decorator
    @_async_logging_decorator
    async def _translate_text_async(text_to_translate:str) -> AsyncGenerateContentResponse:

        """

        Asynchronously translates a text.
        Instructions default to translating whatever text is input into English.

        Parameters:
        text_to_translate (string) : The text to translate.

        Returns:
        AsyncGenerateContentResponse : The translation.

        """

        if(GeminiService._decorator_to_use is None):
            return await GeminiService.__translate_text_async(text_to_translate)

        _decorated_function = GeminiService._decorator_to_use(GeminiService.__translate_text_async)
        return await _decorated_function(text_to_translate)
    
##-------------------start-of-_translate_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    @_redefine_client_decorator
    @_sync_logging_decorator
    def _translate_text(text_to_translate:str) -> GenerateContentResponse:

        """

        Synchronously translates a text.
        Instructions default to translating whatever text is input into English.

        Parameters:
        text_to_translate (string) : The text to translate.

        Returns:
        GenerateContentResponse : The translation.

        """

        if(GeminiService._decorator_to_use is None):
            return GeminiService.__translate_text(text_to_translate)

        _decorated_function = GeminiService._decorator_to_use(GeminiService.__translate_text)
        return _decorated_function(text_to_translate)
    
##-------------------start-of-__translate_text()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    def __translate_text(text_to_translate:str) -> GenerateContentResponse:

        """

        Synchronously translates text.

        Parameters:
        text_to_translate (string) : The text to translate.

        Returns:
        _response (GenerateContentResponse) : The translation.

        """

        text_request = f"{text_to_translate}" if GeminiService._model == "gemini--1.5-pro-latest" else f"{GeminiService._system_message}\n{text_to_translate}"

        _response = GeminiService._client.generate_content(
            contents=text_request,
            generation_config=GeminiService._generation_config,
            safety_settings=GeminiService._safety_settings,
            stream=GeminiService._stream
        )
        
        return _response

##-------------------start-of-__translate_message_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def __translate_text_async(text_to_translate:str) -> AsyncGenerateContentResponse:

        """

        Asynchronously translates text.

        Parameters:
        text_to_translate (string) : The text to translate.

        Returns:
        _response (AsyncGenerateContentResponse) : The translation.

        """

        async with GeminiService._semaphore:

            text_request = f"{text_to_translate}" if GeminiService._model == "gemini--1.5-pro-latest" else f"{GeminiService._system_message}\n{text_to_translate}"

            _response = await GeminiService._client.generate_content_async(
                contents=text_request,
                generation_config=GeminiService._generation_config,
                safety_settings=GeminiService._safety_settings,
                stream=GeminiService._stream
            )
            
            return _response
        
##-------------------start-of-test_api_key_validity()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    @_redefine_client_decorator
    def _test_api_key_validity() -> typing.Tuple[bool, typing.Union[Exception, None]]:

        """

        Tests the validity of the API key.

        Returns:
        validity (bool) : True if the API key is valid, False if it is not.
        e (Exception) : The exception that was raised, if any.

        """

        _validity = False

        try:

            _generation_config = GenerationConfig(candidate_count=1, max_output_tokens=1)

            GeminiService._client.generate_content(
                "Respond to this with 1",generation_config=_generation_config
            )

            _validity = True

            return _validity, None

        except Exception as _e:

            return _validity, _e
        
##-------------------start-of-_get_decorator()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _get_decorator() -> typing.Union[typing.Callable, None]:

        """

        Returns the decorator to use for the Gemini service.

        Returns:
        decorator (callable) : The decorator to use.

        """

        return GeminiService._decorator_to_use
    
##-------------------start-of-_calculate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    @_redefine_client_decorator
    def _calculate_cost(text:str | typing.Iterable, translation_instructions:str | None, model:str | None) -> typing.Tuple[int, float, str]:

        """

        Calculates the cost of the translation.

        Parameters:
        text (string | iterable) : The text to translate.
        translation_instructions (string) : The instructions for the translation.
        model (string) : The model to use for the translation.

        Returns:
        num_tokens (int) : The number of tokens in the text.
        cost (float) : The cost of the translation.
        model (string) : The model used for the translation.

        """

        if(translation_instructions is None):
            translation_instructions = GeminiService._default_translation_instructions

        if(isinstance(text, typing.Iterable)):

            if(not isinstance(text,str) and not _is_iterable_of_strings(text)):
                raise ValueError("The text must be a string or an iterable of strings.")

            ## since instructions are paired with the text, we need to repeat the instructions for index
            translation_instructions = translation_instructions * len(text) # type: ignore

            text = _convert_iterable_to_str(text)

        if(isinstance(translation_instructions, typing.Iterable)):
            translation_instructions = _convert_iterable_to_str(translation_instructions)

        if(model is None):
            model = GeminiService._default_model

        ## not exactly how the text will be formatted, but it's close enough for the purposes of estimating the cost as tokens should be the same
        total_text_to_estimate = f"{translation_instructions}\n{text}"
        
        _num_tokens, _cost, model = _estimate_cost(total_text_to_estimate, model)

        return _num_tokens, _cost, model  