## Copyright (C) 2024 Kaden Bilyeu (Bikatr7) (https://github.com/Bikatr7), Alejandro Mata (https://github.com/alemalvarez)
## Use of this source code is governed by an GNU Lesser General Public License v2.1
## license that can be found in the LICENSE file.

## built-in libraries
import typing
import asyncio

import warnings

## third-party libraries
from .classes import Language, SplitSentences, Formality, GlossaryInfo, NOT_GIVEN, NotGiven

## custom modules
from .services.deepl_service import DeepLService
from .services.gemini_service import GeminiService
from .services.openai_service import OpenAIService
from .services.googletl_service import GoogleTLService
from .services.anthropic_service import AnthropicService
from .services.azure_service import AzureService

from. classes import ModelTranslationMessage, SystemTranslationMessage, TextResult, GenerateContentResponse, AsyncGenerateContentResponse, ChatCompletion, AnthropicMessage, AnthropicToolsBetaMessage, AnthropicTextBlock, AnthropicToolUseBlock
from .exceptions import DeepLException, GoogleAPIError, OpenAIError, InvalidAPITypeException, InvalidResponseFormatException, InvalidTextInputException, EasyTLException, AnthropicError, RequestException

from .util.util import _is_iterable_of_strings
from .util.llm_util import _validate_easytl_llm_translation_settings, _return_curated_gemini_settings, _return_curated_openai_settings, _validate_stop_sequences, _validate_response_schema,  _return_curated_anthropic_settings, _validate_text_length 

class EasyTL:

    """
    EasyTL global client, used to interact with Translation APIs.

    Use :meth:`set_credentials` to set the credentials for the specified API type. (e.g. :meth:`set_credentials("deepl", "your_api_key")` or :meth:`set_credentials("google translate", "path/to/your/credentials.json")`)

    Use :meth:`test_credentials` to test the validity of the credentials for the specified API type. (e.g. :meth:`test_credentials("deepl")`) (Optional) Done automatically when translating.

    Use :meth:`translate` to translate text using the specified service with its appropriate kwargs. Or specify the service by calling the specific translation function. (e.g. :meth:`openai_translate()`)

    Use :meth:`calculate_cost` to calculate the cost of translating text using the specified service. (Optional)

    See the documentation for each function for more information.
    """

##-------------------start-of-set_credentials()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def set_credentials(api_type:typing.Literal["deepl", "gemini", "openai", "google translate", "anthropic", "azure"], credentials:str) -> None:

        """
        Sets the credentials for the specified API type.

        :param api_type: The API type to set the credentials for. Supported types are 'deepl', 'gemini', 'openai', 'google translate', 'anthropic', and 'azure'.
        :type api_type: literal["deepl", "gemini", "openai", "google translate", "anthropic", "azure"]

        :param credentials: The credentials to set. This is an API key for deepl, gemini, anthropic, azure, and openai. For google translate, this is a path to your JSON that has your service account key.
        :type credentials: str
        """

        service_map = {
            "deepl": DeepLService._set_api_key,
            "gemini": GeminiService._set_api_key,
            "openai": OpenAIService._set_api_key,
            "google translate": GoogleTLService._set_credentials,
            "anthropic": AnthropicService._set_api_key,
            "azure": AzureService._set_api_key

        }

        assert api_type in service_map, InvalidAPITypeException("Invalid API type specified. Supported types are 'deepl', 'gemini', 'openai', 'google translate', 'anthropic' and 'azure'.")

        service_map[api_type](credentials)

##-------------------start-of-test_credentials()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def test_credentials(api_type:typing.Literal["deepl", "gemini", "openai", "google translate", "anthropic", "azure"]) -> typing.Tuple[bool, typing.Optional[Exception]]:

        """
        Tests the validity of the credentials for the specified API type.

        :param api_type: The API type to test the credentials for. (literal["deepl", "gemini", "openai", "google translate", "anthropic", "azure"])
        :type api_type: str

        :return: Whether the credentials are valid. (bool)
        :rtype: bool

        :return: The exception that was raised, if any. None otherwise. (Exception)
        :rtype: Exception
        """

        api_services = {
            "deepl": {"service": DeepLService, "exception": DeepLException, "test_func": DeepLService._test_api_key_validity},
            "gemini": {"service": GeminiService, "exception": GoogleAPIError, "test_func": GeminiService._test_api_key_validity},
            "openai": {"service": OpenAIService, "exception": OpenAIError, "test_func": OpenAIService._test_api_key_validity},
            "google translate": {"service": GoogleTLService, "exception": GoogleAPIError, "test_func": GoogleTLService._test_credentials},
            "anthropic": {"service": AnthropicService, "exception": AnthropicError, "test_func": AnthropicService._test_api_key_validity},
            "azure": {"service": AzureService, "exception": RequestException, "test_func": AzureService._test_credentials}
        }

        assert api_type in api_services, InvalidAPITypeException("Invalid API type specified. Supported types are 'deepl', 'gemini', 'openai', 'google translate', 'anthropic' and 'azure'.")

        _is_valid, _e = api_services[api_type]["test_func"]()

        if(not _is_valid):
            ## Done to make sure the exception is due to the specified API type and not the fault of EasyTL
            assert isinstance(_e, api_services[api_type]["exception"]), _e
            return False, _e

        return True, None
    
##-------------------start-of-googletl_translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def googletl_translate(text:typing.Union[str, typing.Iterable[str]],
                           target_lang:str = "en",
                           override_previous_settings:bool = True,
                           decorator:typing.Callable | None = None,
                           logging_directory:str | None = None,
                           response_type:typing.Literal["text", "raw"] | None = "text",
                           translation_delay:float | None = None,
                           format:typing.Literal["text", "html"] = "text",
                           source_lang:str | None = None) -> typing.Union[typing.List[str], str, typing.List[typing.Any], typing.Any]:
        
        """
        Translates the given text to the target language using Google Translate.

        This function assumes that the credentials have already been set.

        It is unknown whether Google Translate has backoff retrying implemented. Assume it does not exist.

        Google Translate v2 API is poorly documented and type hints are near non-existent. typing.Any return types are used for the raw response type.

        :param text: The text to translate. It can be a string or an iterable.
        :type text: Union[str, Iterable[str]]
        :param target_lang: The target language to translate to.
        :type target_lang: str
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to a Google Translate function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying.
        :type decorator: Callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response.
        :type response_type: Literal["text", "raw"]
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param format: The format of the text. Can be 'text' or 'html'. Default is 'text'. Google Translate appears to be able to translate html but this has not been tested thoroughly by EasyTL.
        :type format: Literal["text", "html"]
        :param source_lang: The source language to translate from.
        :type source_lang: str or None

        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of any objects if the response type is 'raw' and input was an iterable, an any object otherwise.
        :rtype: Union[str, List[str], Any, List[Any]]
        """

        assert response_type in ["text", "raw"], InvalidResponseFormatException("Invalid response type specified. Must be 'text' or 'raw'.")

        assert format in ["text", "html"], InvalidResponseFormatException("Invalid format specified. Must be 'text' or 'html'.")

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("google translate")

        if(override_previous_settings == True):
            GoogleTLService._set_attributes(target_language=target_lang, 
                                            format=format, 
                                            source_language=source_lang, 
                                            decorator=decorator, 
                                            logging_directory=logging_directory, 
                                            semaphore=None, 
                                            rate_limit_delay=translation_delay)
            
        ## This section may seem overly complex, but it is necessary to apply the decorator outside of the function call to avoid infinite recursion.
        ## Attempting to dynamically apply the decorator within the function leads to unexpected behavior, where this function's arguments are passed to the function instead of the intended translation function.

        def translate(text):
            return GoogleTLService._translate_text(text)
        
        if(decorator is not None):
            translate = GoogleTLService._decorator_to_use(GoogleTLService._translate_text) ## type: ignore

        else:
            translate = GoogleTLService._translate_text
            
        if(isinstance(text, str)):
            result = translate(text)
        
            assert not isinstance(result, list), EasyTLException("Malformed response received. Please try again.")

            result = result if response_type == "raw" else result["translatedText"]
        
        elif(_is_iterable_of_strings(text)):

            results = [translate(t) for t in text]

            assert isinstance(results, list), EasyTLException("Malformed response received. Please try again.")

            result = [r["translatedText"] for r in results] if response_type == "text" else results # type: ignore
            
        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result
    
##-------------------start-of-googletl_translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def googletl_translate_async(text:typing.Union[str, typing.Iterable[str]],
                                       target_lang:str = "en",
                                       override_previous_settings:bool = True,
                                       decorator:typing.Callable | None = None,
                                       logging_directory:str | None = None,
                                       response_type:typing.Literal["text", "raw"] | None = "text",
                                       semaphore:int | None = 15,
                                       translation_delay:float | None = None,
                                       format:typing.Literal["text", "html"] = "text",
                                       source_lang:str | None = None) -> typing.Union[typing.List[str], str, typing.List[typing.Any], typing.Any]:
        
        """
        Asynchronous version of googletl_translate().

        Translates the given text to the target language using Google Translate.
        Will generally be faster for iterables. Order is preserved.

        This function assumes that the credentials have already been set.

        It is unknown whether Google Translate has backoff retrying implemented. Assume it does not exist.

        Google Translate v2 API is poorly documented and type hints are near non-existent. typing.Any return types are used for the raw response type.

        :param text: The text to translate. It can be a string or an iterable.
        :type text: str or iterable
        :param target_lang: The target language to translate to.
        :type target_lang: str
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to a Google Translate function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response.
        :type response_type: literal["text", "raw"]
        :param semaphore: The number of concurrent requests to make. Default is 15.
        :type semaphore: int
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param format: The format of the text. Can be 'text' or 'html'. Default is 'text'. Google Translate appears to be able to translate html but this has not been tested thoroughly by EasyTL.
        :type format: str or None
        :param source_lang: The source language to translate from.
        :type source_lang: str or None

        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of any objects if the response type is 'raw' and input was an iterable, an any object otherwise.
        :rtype: str or list[str] or any or list[any]
        """

        assert response_type in ["text", "raw"], InvalidResponseFormatException("Invalid response type specified. Must be 'text' or 'raw'.")

        assert format in ["text", "html"], InvalidResponseFormatException("Invalid format specified. Must be 'text' or 'html'.")

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("google translate")

        if(override_previous_settings == True):
            GoogleTLService._set_attributes(target_language=target_lang, 
                                            format=format, 
                                            source_language=source_lang, 
                                            decorator=decorator, 
                                            logging_directory=logging_directory, 
                                            semaphore=semaphore, 
                                            rate_limit_delay=translation_delay)
            
        ## This section may seem overly complex, but it is necessary to apply the decorator outside of the function call to avoid infinite recursion.
        ## Attempting to dynamically apply the decorator within the function leads to unexpected behavior, where this function's arguments are passed to the function instead of the intended translation function.
        def translate(text):
            return GoogleTLService._translate_text_async(text)
        
        if(decorator is not None):
            translate = GoogleTLService._decorator_to_use(GoogleTLService._translate_text_async) ## type: ignore

        else:
            translate = GoogleTLService._translate_text_async
            
        if(isinstance(text, str)):
            _result = await translate(text)

            assert not isinstance(_result, list), EasyTLException("Malformed response received. Please try again.")

            result = _result if response_type == "raw" else _result["translatedText"]
            
        elif(_is_iterable_of_strings(text)):
            _tasks = [translate(t) for t in text]
            _results = await asyncio.gather(*_tasks)
            
            assert isinstance(_results, list), EasyTLException("Malformed response received. Please try again.")

            result = [_r["translatedText"] for _r in _results] if response_type == "text" else _results # type: ignore
                
        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result
    
##-------------------start-of-deepl_translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def deepl_translate(text:typing.Union[str, typing.Iterable[str]],
                        target_lang:str | Language = "EN-US",
                        override_previous_settings:bool = True,
                        decorator:typing.Callable | None = None,
                        logging_directory:str | None = None,
                        response_type:typing.Literal["text", "raw"] | None = "text",
                        translation_delay:float | None = None,
                        source_lang:str | Language | None = None,
                        context:str | None = None,
                        split_sentences:typing.Literal["OFF", "ALL", "NO_NEWLINES"] |  SplitSentences | None = "ALL",
                        preserve_formatting:bool | None = None,
                        formality:typing.Literal["default", "more", "less", "prefer_more", "prefer_less"] | Formality | None = None,
                        glossary:str | GlossaryInfo | None = None,
                        tag_handling:typing.Literal["xml", "html"] | None = None,
                        outline_detection:bool | None = None,
                        non_splitting_tags:str | typing.List[str] | None = None,
                        splitting_tags:str | typing.List[str] | None = None,
                        ignore_tags:str | typing.List[str] | None = None) -> typing.Union[typing.List[str], str, typing.List[TextResult], TextResult]:
        
        """
        Translates the given text to the target language using DeepL.

        This function assumes that the API key has already been set.

        :param text: The text to translate. It can be a string or an iterable.
        :type text: str or iterable
        :param target_lang: The target language to translate to.
        :type target_lang: str or Language
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to a DeepL translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying. If this parameter is None, DeepL will retry your request 5 times before failing. Otherwise, the given decorator will be used.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, a TextResult object.
        :type response_type: literal["text", "raw"]
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param source_lang: The source language to translate from.
        :type source_lang: str or Language or None
        :param context: Additional information for the translator to be considered when translating. Not translated itself. This is a DeepL alpha feature and may be removed at any time.
        :type context: str or None
        :param split_sentences: How to split sentences.
        :type split_sentences: literal or SplitSentences or None
        :param preserve_formatting: Whether to preserve formatting.
        :type preserve_formatting: bool or None
        :param formality: The formality level to use.
        :type formality: literal or Formality or None
        :param glossary: The glossary to use.
        :type glossary: str or GlossaryInfo or None
        :param tag_handling: How to handle tags.
        :type tag_handling: literal or None
        :param outline_detection: Whether to detect outlines.
        :type outline_detection: bool or None
        :param non_splitting_tags: Tags that should not be split.
        :type non_splitting_tags: str or list or None
        :param splitting_tags: Tags that should be split.
        :type splitting_tags: str or list or None
        :param ignore_tags: Tags that should be ignored.
        :type ignore_tags: str or list or None

        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of TextResult objects if the response type is 'raw' and input was an iterable, a TextResult object otherwise.
        :rtype: str or list - str or TextResult or list - TextResult
        """

        assert response_type in ["text", "raw"], InvalidResponseFormatException("Invalid response type specified. Must be 'text' or 'raw'.")

        EasyTL.test_credentials("deepl")

        if(override_previous_settings == True):
            DeepLService._set_attributes(target_lang = target_lang, 
                                        source_lang = source_lang, 
                                        context = context, 
                                        split_sentences = split_sentences,
                                        preserve_formatting = preserve_formatting, 
                                        formality = formality, 
                                        glossary = glossary, 
                                        tag_handling = tag_handling, 
                                        outline_detection = outline_detection, 
                                        non_splitting_tags = non_splitting_tags, 
                                        splitting_tags = splitting_tags, 
                                        ignore_tags = ignore_tags,
                                        decorator=decorator,
                                        logging_directory=logging_directory,
                                        semaphore=None,
                                        rate_limit_delay=translation_delay)
            
        ## This section may seem overly complex, but it is necessary to apply the decorator outside of the function call to avoid infinite recursion.
        ## Attempting to dynamically apply the decorator within the function leads to unexpected behavior, where this function's arguments are passed to the function instead of the intended translation function.
        def translate(text):
            return DeepLService._translate_text(text)
        
        if(decorator is not None):
            translate = DeepLService._decorator_to_use(DeepLService._translate_text) ## type: ignore

        else:
            translate = DeepLService._translate_text

        if(isinstance(text, str)):
            result = translate(text)
        
            assert not isinstance(result, list), EasyTLException("Malformed response received. Please try again.")

            result = result if response_type == "raw" else result.text
        
        elif(_is_iterable_of_strings(text)):

            results = [translate(t) for t in text]

            assert isinstance(results, list), EasyTLException("Malformed response received. Please try again.")

            result = [_r.text for _r in results] if response_type == "text" else results # type: ignore    
            
        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result  ## type: ignore
        
##-------------------start-of-deepl_translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def deepl_translate_async(text:typing.Union[str, typing.Iterable[str]],
                            target_lang:str | Language = "EN-US",
                            override_previous_settings:bool = True,
                            decorator:typing.Callable | None = None,
                            logging_directory:str | None = None,
                            response_type:typing.Literal["text", "raw"] | None = "text",
                            semaphore:int | None = 15,
                            translation_delay:float | None = None,
                            source_lang:str | Language | None = None,
                            context:str | None = None,
                            split_sentences:typing.Literal["OFF", "ALL", "NO_NEWLINES"] |  SplitSentences | None = "ALL",
                            preserve_formatting:bool | None = None,
                            formality:typing.Literal["default", "more", "less", "prefer_more", "prefer_less"] | Formality | None = None,
                            glossary:str | GlossaryInfo | None = None,
                            tag_handling:typing.Literal["xml", "html"] | None = None,
                            outline_detection:bool | None = None,
                            non_splitting_tags:str | typing.List[str] | None = None,
                            splitting_tags:str | typing.List[str] | None = None,
                            ignore_tags:str | typing.List[str] | None = None) -> typing.Union[typing.List[str], str, typing.List[TextResult], TextResult]:
        
        """
        Asynchronous version of deepl_translate().

        Translates the given text to the target language using DeepL.

        Will generally be faster for iterables. Order is preserved.

        This function assumes that the API key has already been set.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: Union[str, Iterable[str]]
        :param target_lang: The target language to translate to.
        :type target_lang: Union[str, Language]
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to a DeepL translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying. If this parameter is None, DeepL will retry your request 5 times before failing. Otherwise, the given decorator will be used.
        :type decorator: Callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: Union[str, None]
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, a TextResult object.
        :type response_type: Literal['text', 'raw']
        :param semaphore: The number of concurrent requests to make. Default is 15.
        :type semaphore: int
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: Union[float, None]
        :param source_lang: The source language to translate from.
        :type source_lang: Union[str, Language, None]
        :param context: Additional information for the translator to be considered when translating. Not translated itself. This is a DeepL alpha feature and may be removed at any time.
        :type context: Union[str, None]
        :param split_sentences: How to split sentences.
        :type split_sentences: Literal['OFF', 'ALL', 'NO_NEWLINES', SplitSentences, None]
        :param preserve_formatting: Whether to preserve formatting.
        :type preserve_formatting: Union[bool, None]
        :param formality: The formality level to use.
        :type formality: Literal['default', 'more', 'less', 'prefer_more', 'prefer_less', Formality, None]
        :param glossary: The glossary to use.
        :type glossary: Union[str, GlossaryInfo, None]
        :param tag_handling: How to handle tags.
        :type tag_handling: Union[Literal['xml', 'html'], None]
        :param outline_detection: Whether to detect outlines.
        :type outline_detection: Union[bool, None]
        :param non_splitting_tags: Tags that should not be split.
        :type non_splitting_tags: Union[str, List[str], None]
        :param splitting_tags: Tags that should be split.
        :type splitting_tags: Union[str, List[str], None]
        :param ignore_tags: Tags that should be ignored.
        :type ignore_tags: Union[str, List[str], None]
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of TextResult objects if the response type is 'raw' and input was an iterable, a TextResult object otherwise.
        :rtype: Union[List[str], str, List[TextResult], TextResult]
        """

        assert response_type in ["text", "raw"], InvalidResponseFormatException("Invalid response type specified. Must be 'text' or 'raw'.")

        EasyTL.test_credentials("deepl")

        if(override_previous_settings == True):
            DeepLService._set_attributes(target_lang=target_lang, 
                                        source_lang=source_lang, 
                                        context=context, 
                                        split_sentences=split_sentences,
                                        preserve_formatting=preserve_formatting, 
                                        formality=formality, 
                                        glossary=glossary, 
                                        tag_handling=tag_handling, 
                                        outline_detection=outline_detection, 
                                        non_splitting_tags=non_splitting_tags, 
                                        splitting_tags=splitting_tags, 
                                        ignore_tags=ignore_tags,
                                        decorator=decorator,
                                        logging_directory=logging_directory,
                                        semaphore=semaphore,
                                        rate_limit_delay=translation_delay)
            
        ## This section may seem overly complex, but it is necessary to apply the decorator outside of the function call to avoid infinite recursion.
        ## Attempting to dynamically apply the decorator within the function leads to unexpected behavior, where this function's arguments are passed to the function instead of the intended translation function.
        def translate(text):
            return DeepLService._translate_text_async(text)
        
        if(decorator is not None):
            translate = DeepLService._decorator_to_use(DeepLService._translate_text_async) ## type: ignore

        else:
            translate = DeepLService._translate_text_async

        if(isinstance(text, str)):
            _result = await translate(text)

            assert not isinstance(_result, list), EasyTLException("Malformed response received. Please try again.")

            result = _result if response_type == "raw" else _result.text
            
        elif(_is_iterable_of_strings(text)):
            _tasks = [translate(t) for t in text]
            _results = await asyncio.gather(*_tasks)
            
            assert isinstance(_results, list), EasyTLException("Malformed response received. Please try again.")

            result = [_r.text for _r in _results] if response_type == "text" else _results # type: ignore
                
        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result
            
##-------------------start-of-gemini_translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def gemini_translate(text:typing.Union[str, typing.Iterable[str]],
                        override_previous_settings:bool = True,
                        decorator:typing.Callable | None = None,
                        logging_directory:str | None = None,
                        response_type:typing.Literal["text", "raw", "json", "raw_json"] | None = "text",
                        response_schema:str | typing.Mapping[str, typing.Any] | None = None,
                        translation_delay:float | None = None,
                        translation_instructions:str | None = None,
                        model:str="gemini-pro",
                        temperature:float=0.5,
                        top_p:float=0.9,
                        top_k:int=40,
                        stop_sequences:typing.List[str] | None=None,
                        max_output_tokens:int | None=None) -> typing.Union[typing.List[str], str, GenerateContentResponse, typing.List[GenerateContentResponse]]:
        
        """
        Translates the given text using Gemini.

        This function assumes that the API key has already been set.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: str or iterable
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to a Gemini translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, a GenerateContentResponse object, 'json' returns a json-parseable string. 'raw_json' returns the raw response, a GenerateContentResponse object, but with the content as a json-parseable string.
        :type response_type: str, literal["text", "raw", "json", "raw_json"]
        :param response_schema: The schema to use for the response. If None, no schema is used. This is only used if the response type is 'json' or 'json_raw'. EasyTL only validates the schema to the extend that it is None or a valid json. It does not validate the contents of the json.
        :type response_schema: str or mapping or None
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param translation_instructions: The translation instructions to use. If None, the default system message is used. If you plan on using the json response type, you must specify that you want a json output and it's format in the instructions. The default system message will ask for a generic json if the response type is json.
        :type translation_instructions: str or None
        :param model: The model to use. (E.g. 'gemini-pro' or 'gemini-pro-1.5-latest')
        :type model: str
        :param temperature: The temperature to use. The higher the temperature, the more creative the output. Lower temperatures are typically better for translation.
        :type temperature: float
        :param top_p: The nucleus sampling probability. The higher the value, the more words are considered for the next token. Generally, alter this or temperature, not both.
        :type top_p: float
        :param top_k: The top k tokens to consider. Generally, alter this or temperature or top_p, not all three.
        :type top_k: int
        :param stop_sequences: String sequences that will cause the model to stop translating if encountered, generally useless.
        :type stop_sequences: list or None
        :param max_output_tokens: The maximum number of tokens to output.
        :type max_output_tokens: int or None

        :returns: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of GenerateContentResponse objects if the response type is 'raw' and input was an iterable, a GenerateContentResponse object otherwise.
        :rtype: str or list[str] or GenerateContentResponse or list[GenerateContentResponse]
        """

        assert response_type in ["text", "raw", "json", "raw_json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text', 'raw', 'json' or 'raw_json'.")

        _settings = _return_curated_gemini_settings(locals())

        _validate_easytl_llm_translation_settings(_settings, "gemini")

        _validate_stop_sequences(stop_sequences)

        _validate_text_length(text, model, service="gemini")

        response_schema = _validate_response_schema(response_schema)

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("gemini")

        json_mode = True if response_type in ["json", "raw_json"] else False

        if(override_previous_settings == True):
            GeminiService._set_attributes(model=model,
                                          system_message=translation_instructions,
                                          temperature=temperature,
                                          top_p=top_p,
                                          top_k=top_k,
                                          candidate_count=1,
                                          stream=False,
                                          stop_sequences=stop_sequences,
                                          max_output_tokens=max_output_tokens,
                                          decorator=decorator,
                                          logging_directory=logging_directory,
                                          semaphore=None,
                                          rate_limit_delay=translation_delay,
                                          json_mode=json_mode,
                                          response_schema=response_schema)
            
            ## Done afterwards, cause default translation instructions can change based on set_attributes()       
            GeminiService._system_message = translation_instructions or GeminiService._default_translation_instructions
        
        if(isinstance(text, str)):
            _result = GeminiService._translate_text(text)
            
            assert not isinstance(_result, list) and hasattr(_result, "text"), EasyTLException("Malformed response received. Please try again.")
            
            result = _result if response_type in ["raw", "raw_json"] else _result.text

        elif(_is_iterable_of_strings(text)):
            
            _results = [GeminiService._translate_text(t) for t in text]

            assert isinstance(_results, list) and all([hasattr(_r, "text") for _r in _results]), EasyTLException("Malformed response received. Please try again.")

            result = [_r.text for _r in _results] if response_type in ["text","json"] else _results # type: ignore
            
        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result

##-------------------start-of-gemini_translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    async def gemini_translate_async(text:typing.Union[str, typing.Iterable[str]],
                                    override_previous_settings:bool = True,
                                    decorator:typing.Callable | None = None,
                                    logging_directory:str | None = None,
                                    response_type:typing.Literal["text", "raw", "json", "raw_json"] | None = "text",
                                    response_schema:str | typing.Mapping[str, typing.Any] | None = None,
                                    semaphore:int | None = 5,
                                    translation_delay:float | None = None,
                                    translation_instructions:str | None = None,
                                    model:str="gemini-pro",
                                    temperature:float=0.5,
                                    top_p:float=0.9,
                                    top_k:int=40,
                                    stop_sequences:typing.List[str] | None=None,
                                    max_output_tokens:int | None=None) -> typing.Union[typing.List[str], str, AsyncGenerateContentResponse, typing.List[AsyncGenerateContentResponse]]:
        
        """
        Asynchronous version of gemini_translate().
        
        Translates the given text using Gemini.
        
        This function assumes that the API key has already been set.
        
        Translation instructions default to translating the text to English. To change this, specify the instructions.
        
        This function is not for use for real-time translation, nor for generating multiple translation candidates. Another function may be implemented for this given demand.
        
        It is not known whether Gemini has backoff retrying implemented. Assume it does not exist.
        
        :param text: The text to translate. Can be a string or an iterable of strings.
        :type text: str or iterable
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to a Gemini translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, an AsyncGenerateContentResponse object, 'json' returns a json-parseable string. 'raw_json' returns the raw response, an AsyncGenerateContentResponse object, but with the content as a json-parseable string.
        :type response_type: str
        :param response_schema: The schema to use for the response. If None, no schema is used. This is only used if the response type is 'json' or 'json_raw'. EasyTL only validates the schema to the extend that it is None or a valid json. It does not validate the contents of the json.
        :type response_schema: str or mapping or None
        :param semaphore: The number of concurrent requests to make. Default is 5 for 1.0 and 2 for 1.5 gemini models. For Gemini, it is recommend to use translation_delay along with the semaphore to prevent rate limiting.
        :type semaphore: int
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param translation_instructions: The translation instructions to use. If None, the default system message is used. If you plan on using the json response type, you must specify that you want a json output and it's format in the instructions. The default system message will ask for a generic json if the response type is json.
        :type translation_instructions: str or None
        :param model: The model to use. (E.g. 'gemini-pro' or 'gemini-pro-1.5-latest')
        :type model: str
        :param temperature: The temperature to use. The higher the temperature, the more creative the output. Lower temperatures are typically better for translation.
        :type temperature: float
        :param top_p: The nucleus sampling probability. The higher the value, the more words are considered for the next token. Generally, alter this or temperature, not both.
        :type top_p: float
        :param top_k: The top k tokens to consider. Generally, alter this or temperature or top_p, not all three.
        :type top_k: int
        :param stop_sequences: String sequences that will cause the model to stop translating if encountered, generally useless.
        :type stop_sequences: list or None
        :param max_output_tokens: The maximum number of tokens to output.
        :type max_output_tokens: int or None
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of AsyncGenerateContentResponse objects if the response type is 'raw' and input was an iterable, a AsyncGenerateContentResponse object otherwise.
        :rtype: str or list or AsyncGenerateContentResponse
        """

        assert response_type in ["text", "raw", "json", "raw_json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text', 'raw', 'json' or 'raw_json'.")

        _settings = _return_curated_gemini_settings(locals())

        _validate_easytl_llm_translation_settings(_settings, "gemini")

        _validate_stop_sequences(stop_sequences)

        _validate_text_length(text, model, service="gemini")

        response_schema = _validate_response_schema(response_schema)

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("gemini")

        json_mode = True if response_type in ["json", "raw_json"] else False

        if(override_previous_settings == True):
            GeminiService._set_attributes(model=model,
                                          system_message=translation_instructions,
                                          temperature=temperature,
                                          top_p=top_p,
                                          top_k=top_k,
                                          candidate_count=1,
                                          stream=False,
                                          stop_sequences=stop_sequences,
                                          max_output_tokens=max_output_tokens,
                                          decorator=decorator,
                                          logging_directory=logging_directory,
                                          semaphore=semaphore,
                                          rate_limit_delay=translation_delay,
                                          json_mode=json_mode,
                                          response_schema=response_schema)
            
            ## Done afterwards, cause default translation instructions can change based on set_attributes()
            GeminiService._system_message = translation_instructions or GeminiService._default_translation_instructions
            
        if(isinstance(text, str)):
            _result = await GeminiService._translate_text_async(text)

            result = _result if response_type in ["raw", "raw_json"] else _result.text
            
        elif(_is_iterable_of_strings(text)):
            _tasks = [GeminiService._translate_text_async(_t) for _t in text]
            _results = await asyncio.gather(*_tasks)

            result = [_r.text for _r in _results] if response_type in ["text","json"] else _results # type: ignore

        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result
            
##-------------------start-of-openai_translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def openai_translate(text:typing.Union[str, typing.Iterable[str], ModelTranslationMessage, typing.Iterable[ModelTranslationMessage]],
                        override_previous_settings:bool = True,
                        decorator:typing.Callable | None = None,
                        logging_directory:str | None = None,
                        response_type:typing.Literal["text", "raw", "json", "raw_json"] | None = "text",
                        translation_delay:float | None = None,
                        translation_instructions:str | SystemTranslationMessage | None = None,
                        model:str="gpt-4",
                        temperature:float | None | NotGiven = NOT_GIVEN,
                        top_p:float | None | NotGiven = NOT_GIVEN,
                        stop:typing.List[str] | None | NotGiven = NOT_GIVEN,
                        max_tokens:int | None | NotGiven = NOT_GIVEN,
                        presence_penalty:float | None | NotGiven = NOT_GIVEN,
                        frequency_penalty:float | None | NotGiven = NOT_GIVEN
                        ) -> typing.Union[typing.List[str], str, typing.List[ChatCompletion], ChatCompletion]:
        
        """
        Translates the given text using OpenAI.

        This function assumes that the API key has already been set.

        Translation instructions default to translating the text to English. To change this, specify the instructions.

        Due to how OpenAI's API works, NOT_GIVEN is treated differently than None. If a parameter is set to NOT_GIVEN, it is not passed to the API. If it is set to None, it is passed to the API as None.
        
        This function is not for use for real-time translation, nor for generating multiple translation candidates. Another function may be implemented for this given demand.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: str or iterable
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to an OpenAI translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying. If this is None, OpenAI will retry the request twice if it fails.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, a ChatCompletion object, 'json' returns a json-parseable string. 'raw_json' returns the raw response, a ChatCompletion object, but with the content as a json-parseable string.
        :type response_type: str, literal["text", "raw", "json", "raw_json"]
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param translation_instructions: The translation instructions to use. If None, the default system message is used. If you plan on using the json response type, you must specify that you want a json output and it's format in the instructions. The default system message will ask for a generic json if the response type is json.
        :type translation_instructions: str or SystemTranslationMessage or None
        :param model: The model to use. (E.g. 'gpt-4', 'gpt-3.5-turbo-0125', 'gpt-4o', etc.)
        :type model: str
        :param temperature: The temperature to use. The higher the temperature, the more creative the output. Lower temperatures are typically better for translation.
        :type temperature: float
        :param top_p: The nucleus sampling probability. The higher the value, the more words are considered for the next token. Generally, alter this or temperature, not both.
        :type top_p: float
        :param stop: String sequences that will cause the model to stop translating if encountered, generally useless.
        :type stop: list or None
        :param max_tokens: The maximum number of tokens to output.
        :type max_tokens: int or None
        :param presence_penalty: The presence penalty to use. This penalizes the model from repeating the same content in the output. Shouldn't be messed with for translation.
        :type presence_penalty: float
        :param frequency_penalty: The frequency penalty to use. This penalizes the model from using the same words too frequently in the output. Shouldn't be messed with for translation.
        :type frequency_penalty: float

        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of ChatCompletion objects if the response type is 'raw' and input was an iterable, a ChatCompletion object otherwise.
        :rtype: str or list[str] or ChatCompletion or list[ChatCompletion]
        """

        assert response_type in ["text", "raw", "json", "raw_json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text', 'raw', 'json' or 'raw_json'.")

        _settings = _return_curated_openai_settings(locals())

        _validate_easytl_llm_translation_settings(_settings, "openai")

        _validate_stop_sequences(stop)

        _validate_text_length(text, model, service="openai")

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("openai")

        json_mode = True if response_type in ["json", "raw_json"] else False
        
        if(override_previous_settings == True):
            OpenAIService._set_attributes(model=model,
                                        temperature=temperature,
                                        logit_bias=None,
                                        top_p=top_p,
                                        n=1,
                                        stop=stop,
                                        max_tokens=max_tokens,
                                        presence_penalty=presence_penalty,
                                        frequency_penalty=frequency_penalty,
                                        decorator=decorator,
                                        logging_directory=logging_directory,
                                        semaphore=None,
                                        rate_limit_delay=translation_delay,
                                        json_mode=json_mode)

            ## Done afterwards, cause default translation instructions can change based on set_attributes()
            translation_instructions = translation_instructions or OpenAIService._default_translation_instructions
        
        else:
            translation_instructions = OpenAIService._system_message

        assert isinstance(text, str) or _is_iterable_of_strings(text) or isinstance(text, ModelTranslationMessage) or _is_iterable_of_strings(text), InvalidTextInputException("text must be a string, an iterable of strings, a ModelTranslationMessage or an iterable of ModelTranslationMessages.")

        translation_batches = OpenAIService._build_translation_batches(text, translation_instructions)
        
        translations = []
        
        for _text, _translation_instructions in translation_batches:

            _result = OpenAIService._translate_text(_translation_instructions, _text)

            assert not isinstance(_result, list) and hasattr(_result, "choices"), EasyTLException("Malformed response received. Please try again.")

            translation = _result if response_type in ["raw", "raw_json"] else _result.choices[0].message.content
            
            translations.append(translation)
        
        ## If originally a single text was provided, return a single translation instead of a list
        result = translations if isinstance(text, typing.Iterable) and not isinstance(text, str) else translations[0]
        
        return result
    
##-------------------start-of-openai_translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def openai_translate_async(text:typing.Union[str, typing.Iterable[str], ModelTranslationMessage, typing.Iterable[ModelTranslationMessage]],
                                    override_previous_settings:bool = True,
                                    decorator:typing.Callable | None = None,
                                    logging_directory:str | None = None,
                                    response_type:typing.Literal["text", "raw", "json", "raw_json"] | None = "text",
                                    semaphore:int | None = 5,
                                    translation_delay:float | None = None,
                                    translation_instructions:str | SystemTranslationMessage | None = None,
                                    model:str="gpt-4",
                                    temperature:float | None | NotGiven = NOT_GIVEN,
                                    top_p:float | None | NotGiven = NOT_GIVEN,
                                    stop:typing.List[str] | None | NotGiven = NOT_GIVEN,
                                    max_tokens:int | None | NotGiven = NOT_GIVEN,
                                    presence_penalty:float | None | NotGiven = NOT_GIVEN,
                                    frequency_penalty:float | None | NotGiven = NOT_GIVEN
                                    ) -> typing.Union[typing.List[str], str, typing.List[ChatCompletion], ChatCompletion]:
        
        """
        Asynchronous version of openai_translate().

        Translates the given text using OpenAI.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: Union[str, Iterable[str]]
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to an OpenAI translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying. If this is None, OpenAI will retry the request twice if it fails.
        :type decorator: Callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, a ChatCompletion object, 'json' returns a json-parseable string. 'raw_json' returns the raw response, a ChatCompletion object, but with the content as a json-parseable string.
        :type response_type: Literal["text", "raw", "json", "raw_json"]
        :param semaphore: The number of concurrent requests to make. Default is 5.
        :type semaphore: int
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param translation_instructions: The translation instructions to use. If None, the default system message is used. If you plan on using the json response type, you must specify that you want a json output and it's format in the instructions. The default system message will ask for a generic json if the response type is json.
        :type translation_instructions: str or SystemTranslationMessage or None
        :param model: The model to use. (E.g. 'gpt-4', 'gpt-3.5-turbo-0125', 'gpt-4o', etc.)
        :type model: str
        :param temperature: The temperature to use. The higher the temperature, the more creative the output. Lower temperatures are typically better for translation.
        :type temperature: float
        :param top_p: The nucleus sampling probability. The higher the value, the more words are considered for the next token. Generally, alter this or temperature, not both.
        :type top_p: float
        :param stop: String sequences that will cause the model to stop translating if encountered, generally useless.
        :type stop: List[str] or None
        :param max_tokens: The maximum number of tokens to output.
        :type max_tokens: int or None
        :param presence_penalty: The presence penalty to use. This penalizes the model from repeating the same content in the output. Shouldn't be messed with for translation.
        :type presence_penalty: float
        :param frequency_penalty: The frequency penalty to use. This penalizes the model from using the same words too frequently in the output. Shouldn't be messed with for translation.
        :type frequency_penalty: float

        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of ChatCompletion objects if the response type is 'raw' and input was an iterable, a ChatCompletion object otherwise.
        :rtype: Union[List[str], str, List[ChatCompletion], ChatCompletion]
        """

        assert response_type in ["text", "raw", "json", "raw_json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text', 'raw', 'json' or 'raw_json'.")

        _settings = _return_curated_openai_settings(locals())

        _validate_easytl_llm_translation_settings(_settings, "openai")

        _validate_stop_sequences(stop)

        _validate_text_length(text, model, service="openai")

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("openai")

        json_mode = True if response_type in ["json", "raw_json"] else False

        if(override_previous_settings == True):
            OpenAIService._set_attributes(model=model,
                                        temperature=temperature,
                                        logit_bias=None,
                                        top_p=top_p,
                                        n=1,
                                        stop=stop,
                                        max_tokens=max_tokens,
                                        presence_penalty=presence_penalty,
                                        frequency_penalty=frequency_penalty,
                                        decorator=decorator,
                                        logging_directory=logging_directory,
                                        semaphore=semaphore,
                                        rate_limit_delay=translation_delay,
                                        json_mode=json_mode)
            
            ## Done afterwards, cause default translation instructions can change based on set_attributes()
            translation_instructions = translation_instructions or OpenAIService._default_translation_instructions

        else:
            translation_instructions = OpenAIService._system_message        
            
        assert isinstance(text, str) or _is_iterable_of_strings(text) or isinstance(text, ModelTranslationMessage) or _is_iterable_of_strings(text), InvalidTextInputException("text must be a string, an iterable of strings, a ModelTranslationMessage or an iterable of ModelTranslationMessages.")

        _translation_batches = OpenAIService._build_translation_batches(text, translation_instructions)

        _translation_tasks = []

        for _text, _translation_instructions in _translation_batches:
            _task = OpenAIService._translate_text_async(_translation_instructions, _text)
            _translation_tasks.append(_task)

        _results = await asyncio.gather(*_translation_tasks)

        _results:typing.List[ChatCompletion] = _results

        assert all([hasattr(_r, "choices") for _r in _results]), EasyTLException("Malformed response received. Please try again.")

        translation = _results if response_type in ["raw","raw_json"] else [result.choices[0].message.content for result in _results if result.choices[0].message.content is not None]

        result = translation if isinstance(text, typing.Iterable) and not isinstance(text, str) else translation[0]

        return result
    
##-------------------start-of-anthropic_translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def anthropic_translate(text:typing.Union[str, typing.Iterable[str], ModelTranslationMessage, typing.Iterable[ModelTranslationMessage]],
                            override_previous_settings:bool = True,
                            decorator:typing.Callable | None = None,
                            logging_directory:str | None = None,
                            response_type:typing.Literal["text", "raw", "json", "raw_json"] | None = "text",
                            response_schema:str | typing.Mapping[str, typing.Any] | None = None,
                            translation_delay:float | None = None,
                            translation_instructions:str | None = None,
                            model:str="claude-3-haiku-20240307",
                            temperature:float | NotGiven = NOT_GIVEN,
                            top_p:float | NotGiven = NOT_GIVEN,
                            top_k:int | NotGiven = NOT_GIVEN,
                            stop_sequences:typing.List[str] | NotGiven = NOT_GIVEN,
                            max_output_tokens:int | NotGiven = NOT_GIVEN) -> typing.Union[typing.List[str], str, 
                                                                                          AnthropicMessage, typing.List[AnthropicMessage],
                                                                                          AnthropicToolsBetaMessage, typing.List[AnthropicToolsBetaMessage]]:
        
        """
        Translates the given text using Anthropic.

        This function assumes that the API key has already been set.

        Translation instructions default to translating the text to English. To change this, specify the instructions.

        This function is not for use for real-time translation, nor for generating multiple translation candidates. Another function may be implemented for this given demand.

        Due to how Anthropic's API works, NOT_GIVEN is treated differently than None. If a parameter is set to NOT_GIVEN, it is not passed to the API. 

        Anthropic's JSON response is quite unsophisticated and also in Beta, it costs a lot of extra tokens to return a json response. It's also inconsistent. Be careful when using it.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: Union[str, Iterable[str], ModelTranslationMessage, Iterable[ModelTranslationMessage]]
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to an Anthropic translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying. If this is None, Anthropic will retry the request twice if it fails.
        :type decorator: Callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, an AnthropicMessage object, 'json' returns a json-parseable string. 'raw_json' returns the raw response, an AnthropicMessage object, but with the content as a json-parseable string.
        :type response_type: Literal["text", "raw", "json", "raw_json"] or None
        :param response_schema: The schema to use for the response. If None, no schema is used. This is only used if the response type is 'json' or 'json_raw'. EasyTL only validates the schema to the extend that it is None or a valid json. It does not validate the contents of the json.
        :type response_schema: str or Mapping[str, Any] or None
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param translation_instructions: The translation instructions to use. If None, the default system message is used. If you plan on using the json response type, you must specify that you want a json output and it's format in the instructions. The default system message will ask for a generic json if the response type is json.
        :type translation_instructions: str or SystemTranslationMessage or None
        :param model: The model to use. (E.g. 'claude-3-haiku-20240307', 'claude-3-sonnet-20240229' or 'claude-3-opus-20240229')
        :type model: str
        :param temperature: The temperature to use. The higher the temperature, the more creative the output. Lower temperatures are typically better for translation.
        :type temperature: float or NotGiven
        :param top_p: The nucleus sampling probability. The higher the value, the more words are considered for the next token. Generally, alter this or temperature, not both.
        :type top_p: float or NotGiven
        :param top_k: The top k tokens to consider. Generally, alter this or temperature or top_p, not all three.
        :type top_k: int or NotGiven
        :param stop_sequences: String sequences that will cause the model to stop translating if encountered, generally useless.
        :type stop_sequences: List[str] or NotGiven
        :param max_output_tokens: The maximum number of tokens to output.
        :type max_output_tokens: int or NotGiven
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of AnthropicMessage objects if the response type is 'raw' and input was an iterable, an AnthropicMessage object otherwise. A list of AnthropicToolsBetaMessage objects if the response type is 'raw' and input was an iterable, an AnthropicToolsBetaMessage object otherwise.
        :rtype: Union[List[str], str, AnthropicMessage, List[AnthropicMessage], AnthropicToolsBetaMessage, List[AnthropicToolsBetaMessage]]
        """

        assert response_type in ["text", "raw", "json", "raw_json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text', 'raw', 'json' or 'raw_json'.")

        _settings = _return_curated_anthropic_settings(locals())

        _validate_easytl_llm_translation_settings(_settings, "anthropic")

        _validate_stop_sequences(stop_sequences)

        _validate_text_length(text, model, service="anthropic")

        response_schema = _validate_response_schema(response_schema)

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("anthropic")

        json_mode = True if response_type in ["json", "raw_json"] else False

        if(override_previous_settings == True):
            AnthropicService._set_attributes(model=model,
                                            system=translation_instructions,
                                            temperature=temperature,
                                            top_p=top_p,
                                            top_k=top_k,
                                            stop_sequences=stop_sequences,
                                            stream=False,
                                            max_tokens=max_output_tokens,
                                            decorator=decorator,
                                            logging_directory=logging_directory,
                                            semaphore=None,
                                            rate_limit_delay=translation_delay,
                                            json_mode=json_mode,
                                            response_schema=response_schema)
            
            ## Done afterwards, cause default translation instructions can change based on set_attributes()
            AnthropicService._system = translation_instructions or AnthropicService._default_translation_instructions

        assert isinstance(text, str) or _is_iterable_of_strings(text) or isinstance(text, ModelTranslationMessage) or _is_iterable_of_strings(text), InvalidTextInputException("text must be a string, an iterable of strings, a ModelTranslationMessage or an iterable of ModelTranslationMessages.")

        _translation_batches = AnthropicService._build_translation_batches(text)

        _translations = []

        for _text in _translation_batches:

            _result = AnthropicService._translate_text(AnthropicService._system, _text)

            assert not isinstance(_result, list) and hasattr(_result, "content"), EasyTLException("Malformed response received. Please try again.")

            if(response_type in ["raw", "raw_json"]):
                translation = _result

            ## response structure is different for beta
            elif(isinstance(_result, AnthropicToolsBetaMessage)):
                content = _result.content

                if(isinstance(content[0], AnthropicTextBlock)):
                    translation = content[0].text

                elif(isinstance(content[0], AnthropicToolUseBlock)):
                    translation = content[0].input

            elif(isinstance(_result, AnthropicMessage)):
                translation = _result.content[0].text
                            
            _translations.append(translation)

        ## If originally a single text was provided, return a single translation instead of a list
        result = _translations if isinstance(text, typing.Iterable) and not isinstance(text, str) else _translations[0]

        return result
    
##-------------------start-of-anthropic_translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def anthropic_translate_async(text:typing.Union[str, typing.Iterable[str], ModelTranslationMessage, typing.Iterable[ModelTranslationMessage]],
                                        override_previous_settings:bool = True,
                                        decorator:typing.Callable | None = None,
                                        logging_directory:str | None = None,
                                        response_type:typing.Literal["text", "raw", "json", "raw_json"] | None = "text",
                                        response_schema:str | typing.Mapping[str, typing.Any] | None = None,
                                        semaphore:int | None = 5,
                                        translation_delay:float | None = None,
                                        translation_instructions:str | None = None,
                                        model:str="claude-3-haiku-20240307",
                                        temperature:float | NotGiven = NOT_GIVEN,
                                        top_p:float | NotGiven = NOT_GIVEN,
                                        top_k:int | NotGiven = NOT_GIVEN,
                                        stop_sequences:typing.List[str] | NotGiven = NOT_GIVEN,
                                        max_output_tokens:int | NotGiven = NOT_GIVEN) -> typing.Union[typing.List[str], str, 
                                                                                                    AnthropicMessage, typing.List[AnthropicMessage],
                                                                                                    AnthropicToolsBetaMessage, typing.List[AnthropicToolsBetaMessage]]:
        
        """
        Asynchronous version of anthropic_translate().
        
        Translates the given text using Anthropic.
        
        This function assumes that the API key has already been set.
        
        Translation instructions default to translating the text to English. To change this, specify the instructions.
        
        This function is not for use for real-time translation, nor for generating multiple translation candidates. Another function may be implemented for this given demand.
        
        Due to how Anthropic's API works, NOT_GIVEN is treated differently than None. If a parameter is set to NOT_GIVEN, it is not passed to the API.
        
        Anthropic's JSON response is quite unsophisticated and also in Beta, it costs a lot of extra tokens to return a json response. It's also inconsistent. Be careful when using it.
        
        :param text: The text to translate. It can be a string, a ModelTranslationMessage, or an iterable of strings or ModelTranslationMessages.
        :type text: Union[str, typing.Iterable[str], ModelTranslationMessage, typing.Iterable[ModelTranslationMessage]]
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to an Anthropic translation function.
        :type override_previous_settings: bool, optional
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying. If this is None, Anthropic will retry the request twice if it fails.
        :type decorator: Callable or None, optional
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None, optional
        :param response_type: The type of response to return. 'text' returns the translated text, 'raw' returns the raw response, an AnthropicMessage object, 'json' returns a json-parseable string. 'raw_json' returns the raw response, an AnthropicMessage object, but with the content as a json-parseable string.
        :type response_type: Literal["text", "raw", "json", "raw_json"] or None, optional
        :param response_schema: The schema to use for the response. If None, no schema is used. This is only used if the response type is 'json' or 'json_raw'. EasyTL only validates the schema to the extend that it is None or a valid json. It does not validate the contents of the json.
        :type response_schema: str or typing.Mapping[str, typing.Any] or None, optional
        :param semaphore: The number of concurrent requests to make. Default is 5.
        :type semaphore: int or None, optional
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None, optional
        :param translation_instructions: The translation instructions to use. If None, the default system message is used. If you plan on using the json response type, you must specify that you want a json output and it's format in the instructions. The default system message will ask for a generic json if the response type is json.
        :type translation_instructions: str or SystemTranslationMessage or None, optional
        :param model: The model to use. (E.g. 'claude-3-haiku-20240307', 'claude-3-sonnet-20240229' or 'claude-3-opus-20240229')
        :type model: str, optional
        :param temperature: The temperature to use. The higher the temperature, the more creative the output. Lower temperatures are typically better for translation.
        :type temperature: float or NotGiven, optional
        :param top_p: The nucleus sampling probability. The higher the value, the more words are considered for the next token. Generally, alter this or temperature, not both.
        :type top_p: float or NotGiven, optional
        :param top_k: The top k tokens to consider. Generally, alter this or temperature or top_p, not all three.
        :type top_k: int or NotGiven, optional
        :param stop_sequences: String sequences that will cause the model to stop translating if encountered, generally useless.
        :type stop_sequences: List[str] or NotGiven, optional
        :param max_output_tokens: The maximum number of tokens to output.
        :type max_output_tokens: int or NotGiven, optional
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of AnthropicMessage objects if the response type is 'raw' and input was an iterable, an AnthropicMessage object otherwise. A list of AnthropicToolsBetaMessage objects if the response type is 'raw' and input was an iterable, an AnthropicToolsBetaMessage object otherwise.
        :rtype: Union[List[str], str, AnthropicMessage, List[AnthropicMessage], AnthropicToolsBetaMessage, List[AnthropicToolsBetaMessage]]
        """

        assert response_type in ["text", "raw", "json", "raw_json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text', 'raw', 'json' or 'raw_json'.")

        _settings = _return_curated_anthropic_settings(locals())

        _validate_easytl_llm_translation_settings(_settings, "anthropic")

        _validate_stop_sequences(stop_sequences)

        _validate_text_length(text, model, service="anthropic")

        response_schema = _validate_response_schema(response_schema)

        ## Should be done after validating the settings to reduce cost to the user
        EasyTL.test_credentials("anthropic")

        json_mode = True if response_type in ["json", "raw_json"] else False

        if(override_previous_settings == True):
            AnthropicService._set_attributes(model=model,
                                            system=translation_instructions,
                                            temperature=temperature,
                                            top_p=top_p,
                                            top_k=top_k,
                                            stop_sequences=stop_sequences,
                                            stream=False,
                                            max_tokens=max_output_tokens,
                                            decorator=decorator,
                                            logging_directory=logging_directory,
                                            semaphore=semaphore,
                                            rate_limit_delay=translation_delay,
                                            json_mode=json_mode,
                                            response_schema=response_schema)
            
            ## Done afterwards, cause default translation instructions can change based on set_attributes()
            AnthropicService._system = translation_instructions or AnthropicService._default_translation_instructions
        
        assert isinstance(text, str) or _is_iterable_of_strings(text) or isinstance(text, ModelTranslationMessage) or _is_iterable_of_strings(text), InvalidTextInputException("text must be a string, an iterable of strings, a ModelTranslationMessage or an iterable of ModelTranslationMessages.")

        _translation_batches = AnthropicService._build_translation_batches(text)

        _translations_tasks = []

        for _text in _translation_batches:
            _task = AnthropicService._translate_text_async(AnthropicService._system, _text)
            _translations_tasks.append(_task)

        _results = await asyncio.gather(*_translations_tasks)

        _results:typing.List[AnthropicMessage | AnthropicToolsBetaMessage] = _results

        assert all([hasattr(_r, "content") for _r in _results]), EasyTLException("Malformed response received. Please try again.")

        if(response_type in ["raw", "raw_json"]):
            translations = _results

        ## response structure is different for beta
        elif(isinstance(_results[0], AnthropicToolsBetaMessage)):
            translations = [result.content[0].input if isinstance(result.content[0], AnthropicToolUseBlock) else result.content[0].text for result in _results]
        
        elif(isinstance(_results[0], AnthropicMessage)):
            translations = [result.content[0].text for result in _results if isinstance(result.content[0], AnthropicTextBlock)]
                
        result = translations if isinstance(text, typing.Iterable) and not isinstance(text, str) else translations[0]

        return result # type: ignore
    
##-------------------start-of-azure_translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def azure_translate(text: typing.Union[str, typing.Iterable[str]],
                        target_lang:str = 'en',
                        override_previous_settings:bool = True,
                        decorator:typing.Callable | None = None,
                        logging_directory:str | None = None,
                        response_type:typing.Literal["text", "json"] | None = "text",
                        translation_delay:float | None = None,
                        api_version:str = '3.0',
                        azure_region:str = "global",
                        azure_endpoint:str = "https://api.cognitive.microsofttranslator.com/",
                        source_lang:str | None = None) -> typing.Union[typing.List[str], str]:
        
        """
        Translates the given text to the target language using Azure.

        This function assumes that the API key has already been set.

        It is unknown whether Azure Translate has backoff retrying implemented. Assume it does not exist.

        Default api_version, azure_region, and azure_endpoint values should be fine for most users.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: str or iterable
        :param target_lang: The target language for translation. Default is 'en'. These are ISO 639-1 language codes.
        :type target_lang: str
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to an Azure translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'json' returns the original response in json format.
        :type response_type: literal["text", "json"]
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param api_version: The version of the Azure Translator API. Default is '3.0'.
        :type api_version: str
        :param azure_region: The Azure region to use for translation. Default is 'global'.
        :type azure_region: str
        :param azure_endpoint: The Azure Translator API endpoint. Default is 'https://api.cognitive.microsofttranslator.com/'.
        :type azure_endpoint: str
        :param source_lang: The source language of the text. If None, the service will attempt to detect the language.
        :type source_lang: str or None
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise.
        :rtype: str or list[str]
        """

        assert response_type in ["text", "json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text' or 'json'.")

        EasyTL.test_credentials("azure")

        if(override_previous_settings == True):
            AzureService._set_attributes(target_language=target_lang,
                                        api_version=api_version,
                                        azure_region=azure_region,
                                        azure_endpoint=azure_endpoint,
                                        source_language=source_lang,
                                        decorator=decorator,
                                        log_directory=logging_directory,
                                        semaphore=None,
                                        rate_limit_delay=translation_delay)
            
        ## This section may seem overly complex, but it is necessary to apply the decorator outside of the function call to avoid infinite recursion.
        ## Attempting to dynamically apply the decorator within the function leads to unexpected behavior, where this function's arguments are passed to the function instead of the intended translation function.

        def translate(text):
            return AzureService._translate_text(text)
        
        if(decorator is not None):
            translate = AzureService._decorator_to_use(AzureService._translate_text) # type: ignore

        else:
            translate = AzureService._translate_text

        if(isinstance(text, str)):

            result = translate(text)[0]

            assert not isinstance(result, list), EasyTLException("Malformed response received. Please try again.")

            result = result if response_type == "json" else result['translations'][0]['text']
        
        elif(_is_iterable_of_strings(text)):

            _results = [translate(_t) for _t in text]

            assert isinstance(_results, list), EasyTLException("Malformed response received. Please try again.")

            result = _results if response_type == "json" else [result[0]['translations'][0]['text'] for result in _results]

        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")

        return result # type: ignore

##-------------------start-of-azure_translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    async def azure_translate_async(text: typing.Union[str, typing.Iterable[str]],
                                    target_lang:str = 'en',
                                    override_previous_settings:bool = True,
                                    decorator:typing.Callable | None = None,
                                    logging_directory:str | None = None,
                                    response_type:typing.Literal["text", "json"] | None = "text",
                                    semaphore:int | None = 15,
                                    translation_delay:float | None = None,
                                    api_version:str = '3.0',
                                    azure_region:str = "global",
                                    azure_endpoint:str = "https://api.cognitive.microsofttranslator.com/",
                                    source_lang:str | None = None) -> typing.Union[typing.List[str], str]:
        """
        Asynchronous version of azure_translate().

        Translates the given text to the target language using Azure.

        :param text: The text to translate. It can be a string or an iterable of strings.
        :type text: str or iterable
        :param target_lang: The target language for translation. Default is 'en'. These are ISO 639-1 language codes.
        :type target_lang: str
        :param override_previous_settings: Whether to override the previous settings that were used during the last call to an Azure translation function.
        :type override_previous_settings: bool
        :param decorator: The decorator to use when translating. Typically for exponential backoff retrying.
        :type decorator: callable or None
        :param logging_directory: The directory to log to. If None, no logging is done. This'll append the text result and some function information to a file in the specified directory. File is created if it doesn't exist.
        :type logging_directory: str or None
        :param response_type: The type of response to return. 'text' returns the translated text, 'json' returns the original response in json format.
        :type response_type: literal["text", "json"]
        :param semaphore: The number of concurrent requests to make. Default is 15.
        :type semaphore: int
        :param translation_delay: If text is an iterable, the delay between each translation. Default is none. This is more important for asynchronous translations where a semaphore alone may not be sufficient.
        :type translation_delay: float or None
        :param api_version: The version of the Azure Translator API. Default is '3.0'.
        :type api_version: str
        :param azure_region: The Azure region to use for translation. Default is 'global'.
        :type azure_region: str
        :param azure_endpoint: The Azure Translator API endpoint. Default is 'https://api.cognitive.microsofttranslator.com/'.
        :type azure_endpoint: str
        :param source_lang: The source language of the text. If None, the service will attempt to detect the language.
        :type source_lang: str or None
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise.
        :rtype: str or list[str]
        """

        assert response_type in ["text", "json"], InvalidResponseFormatException("Invalid response type specified. Must be 'text' or 'json'.")

        EasyTL.test_credentials("azure")

        if(override_previous_settings == True):
            AzureService._set_attributes(target_language=target_lang,
                                        api_version=api_version,
                                        azure_region=azure_region,
                                        azure_endpoint=azure_endpoint,
                                        source_language=source_lang,
                                        decorator=decorator,
                                        log_directory=logging_directory,
                                        semaphore=semaphore,
                                        rate_limit_delay=translation_delay)
            
        ## This section may seem overly complex, but it is necessary to apply the decorator outside of the function call to avoid infinite recursion.
        ## Attempting to dynamically apply the decorator within the function leads to unexpected behavior, where this function's arguments are passed to the function instead of the intended translation function.

        async def translate(text):
            return await AzureService._translate_text_async(text)
        
        if(decorator is not None):
            translate = AzureService._decorator_to_use(AzureService._translate_text_async) # type: ignore

        else:
            translate = AzureService._translate_text_async

        if(isinstance(text, str)):

            result = (await translate(text))[0]

            assert not isinstance(result, list), EasyTLException("Malformed response received. Please try again.")

            result = result if response_type == "json" else result['translations'][0]['text']

        elif(_is_iterable_of_strings(text)):

            _tasks = [translate(_t) for _t in text]
            _results = await asyncio.gather(*_tasks)

            assert isinstance(_results, list), EasyTLException("Malformed response received. Please try again.")

            result = _results if response_type == "json" else [result[0]['translations'][0]['text'] for result in _results]

        else:
            raise InvalidTextInputException("text must be a string or an iterable of strings.")
        
        return result # type: ignore

##-------------------start-of-translate()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
    @staticmethod
    def translate(text:str | typing.Iterable[str],
                  service:typing.Optional[typing.Literal["deepl", "openai", "gemini", "google translate", "anthropic", "azure"]] = "deepl",
                  **kwargs) -> typing.Union[typing.List[str], str, 
                                            typing.List[TextResult], TextResult, 
                                            typing.List[ChatCompletion], ChatCompletion,
                                            typing.List[GenerateContentResponse], GenerateContentResponse, 
                                            typing.List[typing.Any], typing.Any,
                                            typing.List[AnthropicMessage], AnthropicMessage]:
        
        """

        Translates the given text to the target language using the specified service.

        Please see the documentation for the specific translation function for the service you want to use.

        DeepL: deepl_translate() 
        OpenAI: openai_translate() 
        Gemini: gemini_translate() 
        Google Translate: googletl_translate() 
        Anthropic: anthropic_translate()
        Azure: azure_translate()

        All functions can return a list of strings or a string, depending on the input. The response type can be specified to return the raw response instead:
        DeepL: TextResult
        OpenAI: ChatCompletion
        Gemini: GenerateContentResponse
        Google Translate: any
        Anthropic: AnthropicMessage or AnthropicToolsBetaMessage
        Azure: str

        :param service: The service to use for translation.
        :type service: str
        :param text: The text to translate.
        :type text: str or typing.Iterable[str]
        :param **kwargs: The keyword arguments to pass to the translation function.
        :returns: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of TextResult objects if the response type is 'raw' and input was an iterable, a TextResult object otherwise. A list of GenerateContentResponse objects if the response type is 'raw' and input was an iterable, a GenerateContentResponse object otherwise. A list of ChatCompletion objects if the response type is 'raw' and input was an iterable, a ChatCompletion object otherwise. A list of any objects if the response type is 'raw' and input was an iterable, an any object otherwise. A list of AnthropicMessage objects if the response type is 'raw' and input was an iterable, an AnthropicMessage object otherwise. A list of AnthropicToolsBetaMessage objects if the response type is 'raw' and input was an iterable, an AnthropicToolsBetaMessage object otherwise.
        :rtype: str or typing.List[str] or TextResult or typing.List[TextResult] or GenerateContentResponse or typing.List[GenerateContentResponse] or ChatCompletion or typing.List[ChatCompletion] or typing.Any or typing.List[typing.Any] or AnthropicMessage or typing.List[AnthropicMessage] or AnthropicToolsBetaMessage or typing.List[AnthropicToolsBetaMessage]

        """

        assert service in ["deepl", "openai", "gemini", "google translate", "anthropic", "azure"], InvalidAPITypeException("Invalid service specified. Must be 'deepl', 'openai', 'gemini', 'google translate', 'anthropic' or 'azure'.")

        if(service == "deepl"):
            return EasyTL.deepl_translate(text, **kwargs)

        elif(service == "openai"):
            return EasyTL.openai_translate(text, **kwargs)

        elif(service == "gemini"):
           return EasyTL.gemini_translate(text, **kwargs)
        
        elif(service == "google translate"):
            return EasyTL.googletl_translate(text, **kwargs)
        
        elif(service == "anthropic"):
            return EasyTL.anthropic_translate(text, **kwargs)
        
        elif(service == "azure"):
            return EasyTL.azure_translate(text, **kwargs)
        
##-------------------start-of-translate_async()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    @staticmethod
    async def translate_async(text:str | typing.Iterable[str],
                              service:typing.Optional[typing.Literal["deepl", "openai", "gemini", "google translate", "anthropic", "azure"]] = "deepl",
                              **kwargs) -> typing.Union[typing.List[str], str, 
                                                        typing.List[TextResult], TextResult,  
                                                        typing.List[ChatCompletion], ChatCompletion,
                                                        typing.List[AsyncGenerateContentResponse], AsyncGenerateContentResponse,
                                                        typing.List[typing.Any], typing.Any,
                                                        typing.List[AnthropicMessage], AnthropicMessage]:

        
        """
        Asynchronous version of :meth:`translate`.

        Translates the given text to the target language using the specified service.
        This function assumes that the API key has already been set.
        :meth:`translate_async` will generally be faster for iterables. Order is preserved.

        Please see the documentation for the specific translation function for the service you want to use.

        - DeepL: :meth:`deepl_translate_async`
        - OpenAI: :meth:`openai_translate_async`
        - Gemini: :meth:`gemini_translate_async`
        - Google Translate: :meth:`googletl_translate_async`
        - Anthropic: :meth:`anthropic_translate_async`
        - Azure: :meth:`azure_translate_async`

        All functions can return a list of strings or a string, depending on the input. The response type can be specified to return the raw response instead:

        - DeepL: :class:`TextResult`
        - OpenAI: :class:`ChatCompletion`
        - Gemini: :class:`AsyncGenerateContentResponse`
        - Google Translate: any
        - Anthropic: :class:`AnthropicMessage` or :class:`AnthropicToolsBetaMessage`
        - Azure: str

        :param service: The service to use for translation.
        :type service: str
        :param text: The text to translate.
        :type text: str or typing.Iterable[str]
        :param kwargs: The keyword arguments to pass to the translation function.
        :return: The translation result. A list of strings if the input was an iterable, a string otherwise. A list of :class:`TextResult` objects if the response type is 'raw' and input was an iterable, a :class:`TextResult` object otherwise. A list of :class:`AsyncGenerateContentResponse` objects if the response type is 'raw' and input was an iterable, an :class:`AsyncGenerateContentResponse` object otherwise. A list of :class:`ChatCompletion` objects if the response type is 'raw' and input was an iterable, a :class:`ChatCompletion` object otherwise. A list of any objects if the response type is 'raw' and input was an iterable, an any object otherwise. A list of :class:`AnthropicMessage` objects if the response type is 'raw' and input was an iterable, an :class:`AnthropicMessage` object otherwise. A list of :class:`AnthropicToolsBetaMessage` objects if the response type is 'raw' and input was an iterable, an :class:`AnthropicToolsBetaMessage` object otherwise.
        :rtype: typing.Union[typing.List[str], str, typing.List[TextResult], TextResult, typing.List[ChatCompletion], ChatCompletion, typing.List[AsyncGenerateContentResponse], AsyncGenerateContentResponse, typing.List[typing.Any], typing.Any, typing.List[AnthropicMessage], AnthropicMessage, typing.List[AnthropicToolsBetaMessage], AnthropicToolsBetaMessage]terable, an AnthropicMessage object otherwise. A list of AnthropicToolsBetaMessage objects if the response type is 'raw' and input was an iterable, an AnthropicToolsBetaMessage object otherwise.
        """

        assert service in ["deepl", "openai", "gemini", "google translate", "anthropic", "azure"], InvalidAPITypeException("Invalid service specified. Must be 'deepl', 'openai', 'gemini', 'google translate', 'anthropic' or 'azure'.")

        if(service == "deepl"):
            return await EasyTL.deepl_translate_async(text, **kwargs)

        elif(service == "openai"):
            return await EasyTL.openai_translate_async(text, **kwargs)

        elif(service == "gemini"):
            return await EasyTL.gemini_translate_async(text, **kwargs)
        
        elif(service == "google translate"):
            return await EasyTL.googletl_translate_async(text, **kwargs)
        
        elif(service == "anthropic"):
            return await EasyTL.anthropic_translate_async(text, **kwargs)
        
        elif(service == "azure"):
            return await EasyTL.azure_translate_async(text, **kwargs)

##-------------------start-of-calculate_cost()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
    @staticmethod
    def calculate_cost(text:str | typing.Iterable[str],
                       service:typing.Optional[typing.Literal["deepl", "openai", "gemini", "google translate", "anthropic", "azure"]] = "deepl",
                       model:typing.Optional[str] = None,
                       translation_instructions:typing.Optional[str] = None
                       ) -> typing.Tuple[int, float, str]:
        
        """
        Calculates the cost of translating the given text using the specified service.

        For LLMs, the cost is based on the default model unless specified.

        Model and Translation Instructions are ignored for DeepL, Google Translate, and Azure.

        For DeepL, Azure, and Google Translate, the number of tokens is the number of characters in the text. The returned model is the name of the service.

        Note that Anthropic's cost estimate is pretty sketchy and can be inaccurate. Refer to the actual response object for the cost or the API panel. This is because their tokenizer is not public, and we're forced to estimate.

        :param text: The text to translate.
        :type text: str or iterable
        :param service: The service to use for translation.
        :type service: str
        :param model: The model to use for translation. If None, the default model is used.
        :type model: str or None
        :param translation_instructions: The translation instructions to use.
        :type translation_instructions: str or None
        :return: The number of tokens/characters in the text, the cost of translating the text, and the model used for translation.
        :rtype: tuple[int, float, str]
        """

        assert service in ["deepl", "openai", "gemini", "google translate", "anthropic", "azure"], InvalidAPITypeException("Invalid service specified. Must be 'deepl', 'openai', 'gemini', 'google translate', 'anthropic' or 'azure'.")

        if(service == "deepl"):
            return DeepLService._calculate_cost(text)
        
        elif(service == "openai"):
            return OpenAIService._calculate_cost(text, translation_instructions, model)

        elif(service == "gemini"):
            return GeminiService._calculate_cost(text, translation_instructions, model)
        
        elif(service == "google translate"):
            return GoogleTLService._calculate_cost(text)
        
        elif(service == "anthropic"):
            return AnthropicService._calculate_cost(text, translation_instructions, model)
        
        elif(service == "azure"):
            return AzureService._calculate_cost(text)