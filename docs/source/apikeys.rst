
Obtaining API keys
==================

Anthropic
---------
1. Go to https://www.anthropic.com/api
2. Sign up / login to the API console
3. Click on 'Get API Keys'
4. Click on 'Create Key' and name it
5. Copy it and you're good to go!

The API key is something like: `sk_1234567890abcdef1234567890abcdef`

You can export it as an environment variable like so:

.. code-block:: bash

    export ANTHROPIC_API_KEY="your_api_key"

And pass it as an argument to the `set_credentials` function:

.. code-block:: python

    easytl.set_credentials("anthropic", os.environ["ANTHROPIC_API_KEY"])


Azure
-----
1. Go to https://portal.azure.com/
2. Sign in to your Azure account
3. Search for the service `Translator`, at Azure AI Services
4. Click on `Create`
5. Fill the form (choose Subscription, Resource group, Region, name and Tier)
6. To to the resource when it finishes deploying
7. Click on `Keys and Endpoint`
8. Copy one of the keys, the region and the endpoint for Text Translation

The API key is something like: '1234567890abcdef1234567890abcdef'
The region is something like: 'eastus'
The endpoint is normally: 'https://api.cognitive.microsofttranslator.com/'

You can export them as environment vars like so:

.. code-block:: bash

    export AZURE_API_KEY="your_api_key"
    export AZURE_REGION="your_region"
    export AZURE_ENDPOINT="your_endpoint"

And pass the key as an argument to the `set_credentials` function:

.. code-block:: python

    easytl.set_credentials(api_key=os.environ["AZURE_API_KEY"])

.. warning::

    Make sure that you pass the region and the endpoint to the `translate` function:

    .. code-block:: python

        easytl.azure_translate("Hello, world!", "en", "es", region=os.environ["AZURE_REGION"], endpoint=os.environ["AZURE_ENDPOINT"])

DeepL
-----
1. Go to https://www.deepl.com/pro-api
2. Sign up / login to your DeepL account
3. Navigate to 'API Keys' section
4. Click on 'Create API Key' and name it
5. Copy the generated API key

The API key is something like: `12345678-1234-1234-1234-1234567890ab`

You can export it as an environment variable like so:

.. code-block:: bash

    export DEEPL_API_KEY="your_api_key"

Or you can pass it as an argument to the `set_credentials` function:

.. code-block:: python

    easytl.set_credentials("deepl", os.environ["DEEPL_API_KEY"])

Gemini and Google translate
---------------------------

Gemini and Google Translate have some common steps

1. Go to https://console.cloud.google.com/
2. Sign up / login to your Google Cloud account
3. Create a new project or select an existing one

Now, for Gemini:

4. Go to https://aistudio.google.com/app/apikey
5. Click on 'Get API Key'
6. Select your project from the dropdown
7. Copy the key!

It looks something like: `AIzaSyA_1234567890abcdefakubgkuae`

You can export it as an environment variable like so:

.. code-block:: bash

    export GEMINI_API_KEY="your_api_key"

And pass it as an argument to the `set_credentials` function:

.. code-block:: python

    easytl.set_credentials("gemini", os.environ["GEMINI_API_KEY"])

For Google Translate:

4. From https://console.cloud.google.com/, go to the `APIs & Services` section
5. Click on `Enable APIs and Services`
6. Search for `Cloud Translation API` and enable it
7. Go to `Credentials` and click on `Create credentials`
8. Select `Service account`
9. Fill the form and click on `Done`
10. Click on the service account you just created
11. Under the page `Keys`, click on `Add Key` and select `JSON`
12. Store **securely** the JSON file

For using the translation service, you pass the path to the JSON file as an argument to the `set_credentials` function:

.. code-block:: python

    easytl.set_credentials("google translate", "path/to/your/credentials.json")

OpenAI
------
1. Go to https://platform.openai.com/
2. Sign up / login to your OpenAI account
3. Navigate to the 'API Keys' section
4. Click on 'Create new secret key'
5. Copy the generated API key

The API key is something like: `sk-1234567890abcdef1234567890abcdef`

You can export it as an environment variable like so:

.. code-block:: bash

    export OPENAI_API_KEY="your_api_key"

And pass it as an argument to the `set_credentials` function:

.. code-block:: python

    easytl.set_credentials("openai", os.environ["OPENAI_API_KEY"])