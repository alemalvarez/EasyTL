********
EasyTL
********


Seamless Multi-API Translation: Simplifying Language Barriers with universal translation provider support.

EasyTL provides a simple and consistent interface for translating text across multiple translation APIs. 🔄🔤 It offers a range of features to customize the translation process, manage costs, and validate credentials before submitting requests. ⚙️💰✔️

Currently it supports **Anthropic, Azure Translation Service, DeepL, Gemini, Google Translate, and OpenAI**. 🤖💻 To request new services, please open an issue on the GitHub repository or contact Bikatr7@proton.me or alemalvarez@icloud.com. 📩✉️

EasyTL has a Trello board for tracking planned features and issues: 📋🗂️

https://trello.com/b/Td555CoW/easytl

We've compiled a repository of examples and use cases for EasyTL at this [GitHub repository](https://github.com/Bikatr7/easytl-demo)

*****************
Table of Contents
*****************

- `Quick Start <quick start_>`_
- `Installation <installation_>`_
- `Features <features_>`_
- `API Usage <api usage_>`_
- `License <license_>`_
- `Contact <contact_>`_
- `Contribution <contribution_>`_
- `Notes <notes_>`_

---------------------------------------------------------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------------------------------------------------------
**Quick Start**
---------------------------------------------------------------------------------------------------------------------------------------------------

To get started with EasyTL, install the package via pip:

.. code-block:: bash

   pip install easytl

Then, you can translate text using by importing the global client.

For example, with DeepL:

.. code-block:: python

   from easytl import EasyTL

   ## Set your API key
   EasyTL.set_credentials("deepl", "YOUR_API_KEY")

   ## You can also validate your API keys; translation functions will do this automatically
   is_valid, e = EasyTL.validate_credentials("deepl")

   translated_text = EasyTL.deepl_translate("私は日本語が話せます", "EN-US") ## Text to translate, language to translate to, only two "required" arguments but there are more optional arguments for additional functionality and other services.

   print(translated_text) ## Output: "I can speak Japanese"


or with OpenAI:

.. code-block:: python

   from easytl import EasyTL

   import asyncio

   async def main():

    ## Set your API key
    EasyTL.set_credentials("openai", "YOUR_API_KEY")

    ## Get's the raw response from the API, allowing you to access the full response object
    raw_response = await EasyTL.openai_translate_async("I can speak Japanese", model="gpt-4o", translation_instructions="Translate this text to Japanese.", response_type="raw") 

    print(raw_response.choices[0].message.content) ## Output: "私は日本語が話せます" or something similar

   if(__name__ == "__main__"):
      asyncio.run(main())


---------------------------------------------------------------------------------------------------------------------------------------------------

**Installation**
----------------

Python 3.10+

EasyTL can be installed using pip:

.. code-block:: bash

   pip install easytl

This will install EasyTL along with its dependencies and requirements.

These are the dependencies/requirements that will be installed:

.. code-block:: bash

   setuptools>=61.0
   wheel
   setuptools_scm>=6.0
   tomli
   google-generativeai==0.5.4
   deepl==1.16.1
   openai==1.29.0
   backoff==2.2.1
   tiktoken==0.7.0
   google-cloud-translate==3.15.3
   anthropic==0.26.1
   requests>=2.31.0

---------------------------------------------------------------------------------------------------------------------------------------------------

**Features**
------------

EasyTL offers seamless integration with several translation APIs, allowing users to easily switch between services based on their needs. Key features include:

- Support for multiple translation APIs including OpenAI, DeepL, Gemini, and Google Translate.
- Simple API key and credential management.
- Methods to validate credentials before usage.
- Cost estimation tools to help manage usage based on text length, translation instructions for LLMs, and translation services.
- Highly customizable translation options, with the API's original features.
- Lots of optional arguments for additional functionality. Such as decorators, semaphores, and rate-limit delays.

---------------------------------------------------------------------------------------------------------------------------------------------------

**API Usage**
-------------

Translating Text
~~~~~~~~~~~~~~~~
Translate functions can be broken down into two categories: LLM and non-LLM. LLM ones can take instructions, while non-LLM ones require a target language. 

`deepl_translate`, `googletl_translate`, and `azure_translate` are non-LLM functions, while `openai_translate`, `gemini_translate`, and `anthropic_translate` are LLM functions.

Each method accepts various parameters to customize the translation process, such as language, text format, and API-specific features like formality level or temperature. However these vary wildly between services, so it is recommended to check the documentation for each service for more information.

All services offer asynchronous translation methods that return a future object for concurrent processing. These methods are suffixed with `_async` and can be awaited to retrieve the translated text.

Instead of receiving the translated text directly, you can also use the `response_type` parameter to get the raw response object, specify a json response where available, or both.
  
  `text` - Default. Returns the translated text.

  `json` - Returns the response as a JSON object. Not all services support this.

  `raw` - Returns the raw response object from the API. This can be useful for accessing additional information or debugging.
  
  `raw_json` - Returns the raw response object with the text but with the response also a json object. Again, not all services support this.
  
Generic Translation Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

EasyTL has generic translation methods `translate` and `translate_async` that can be used to translate text with any of the supported services. These methods accept the text, service, and kwargs of the respective service as parameters.

Cost Calculation
~~~~~~~~~~~~~~~~

The `calculate_cost` method provides an estimate of the cost associated with translating a given text with specified settings for each supported service.

characters or tokens depending on the service.

.. code-block:: python

   num_characters, cost, model = EasyTL.calculate_cost("This has a lot of characters", "deepl")

or

.. code-block:: python

   num_tokens, cost, model = EasyTL.calculate_cost("This has a lot of tokens.", "openai", model="gpt-4", translation_instructions="Translate this text to Japanese.")

Credentials Management
~~~~~~~~~~~~~~~~~~~~~~

Credentials can be set and validated using `set_credentials` and `validate_credentials` methods to ensure they are active and correct before submitting translation requests.

---------------------------------------------------------------------------------------------------------------------------------------------------

**License**
-----------

This project, EasyTL, is licensed under the GNU Lesser General Public License v2.1 (LGPLv2.1) - see the LICENSE file for complete details.

The LGPL is a permissive copyleft license that enables this software to be freely used, modified, and distributed. It is particularly designed for libraries, allowing them to be included in both open source and proprietary software. When using or modifying EasyTL, you can choose to release your work under the LGPLv2.1 to contribute back to the community or incorporate it into proprietary software as per the license's permissions.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Contact**
-----------

If you have any questions or suggestions, feel free to reach out to me at `Bikatr7@proton.me <mailto:Bikatr7@proton.me>`_

Also feel free to check out the `GitHub repository <https://github.com/Bikatr7/EasyTL>`_ for this project.

Or the issue tracker `here <https://github.com/Bikatr7/EasyTL/issues>`_.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Contribution**
----------------

Contributions are welcome! I don't have a specific format for contributions, but please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Notes**
---------

EasyTL was originally developed as a part of `Kudasai <https://github.com/Bikatr7/Kudasai>`_, a Japanese preprocessor later turned Machine Translator. It was later split off into its own package to be used independently of Kudasai for multiple reasons.

This package is also my second serious attempt at creating a Python package, so I'm sure there are some things that could be improved. Feedback is welcomed.