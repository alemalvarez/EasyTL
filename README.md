---------------------------------------------------------------------------------------------------------------------------------------------------
**Table of Contents**

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Features](#features)
- [API Usage](#api-usage)
- [License](#license)
- [Contact](#contact)
- [Contribution](#contribution)
- [Notes](#notes)

---------------------------------------------------------------------------------------------------------------------------------------------------

## EasyTL

Wrapper for OpenAI, DeepL, and Gemini APIs for easy translation of text.

EasyTL has a Trello board for tracking features and issues:
https://trello.com/b/Td555CoW/easytl

---------------------------------------------------------------------------------------------------------------------------------------------------
**Quick Start**<a name="quick-start"></a>

To get started with EasyTL, install the package via pip:

```bash
pip install easytl
```

Then, you can translate Japanese text using by importing the global client.

For example, with DeepL:

```python
from easytl import EasyTL

## Set your API key
EasyTL.set_api_key("deepL", "your_api_key_here")

## You can also validate your API keys; translation functions will do this automatically
is_valid, e = EasyTL.validate_api_key("deepL")

translated_text = EasyTL.deepl_translate("私は日本語が話せます", "EN") ## Text to translate, language to translate to, only two "required" arguments but there are more optional arguments for additional functionality.
```

---------------------------------------------------------------------------------------------------------------------------------------------------

**Installation**<a name="installation"></a>

Python 3.10+

EasyTL can be installed using pip:

```bash
pip install easytl
```

This will install EasyTL along with its dependencies and requirements.

These are the dependencies/requirements that will be installed:
```
setuptools>=61.0
wheel
setuptools_scm>=6.0
tomli
google-generativeai==0.5.1
deepl==1.16.1
openai==1.13.3
backoff==2.2.1
tiktoken==0.6.0
```
---------------------------------------------------------------------------------------------------------------------------------------------------

**Features**<a name="features"></a>

EasyTL offers seamless integration with several translation APIs, allowing users to easily switch between services based on their needs. Key features include:

- Support for multiple translation APIs including OpenAI, DeepL, and Gemini.
- Simple API key management.
- Methods to validate API keys before usage.
- Cost estimation tools to help manage usage based on text length and service.
- Highly customizable translation options, with the API's original features.
- Lots of optional arguments for additional functionality. Such as decorators, semaphores, and rate-limit delays.

---------------------------------------------------------------------------------------------------------------------------------------------------

**API Usage**<a name="api-usage"></a>

### Translating Text

Use `deepl_translate`, `openai_translate`, or `gemini_translate` to translate text using the respective services. Each method accepts various parameters to customize the translation process, such as language, text format, and API-specific features like formality level or temperature for creative outputs.

### Cost Calculation

The `calculate_cost` method provides an estimate of the cost associated with translating a given text with specified settings for each supported service.

characters or tokens depending on the service.

```python
num_characters, cost, model = EasyTL.calculate_cost("Example text.", "deepL")
```

### API Key Management

API keys can be set and validated using `set_api_key` and `validate_api_key` methods to ensure they are active and correct before submitting translation requests.

---------------------------------------------------------------------------------------------------------------------------------------------------

**License**<a name="license"></a>

This project, EasyTL, is licensed under the GNU Lesser General Public License v2.1 (LGPLv2.1) - see the LICENSE file for complete details.

The LGPL is a permissive copyleft license that enables this software to be freely used, modified, and distributed. It is particularly designed for libraries, allowing them to be included in both open source and proprietary software. When using or modifying EasyTL, you can choose to release your work under the LGPLv2.1 to contribute back to the community or incorporate it into proprietary software as per the license's permissions.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Contact**<a name="contact"></a>

If you have any questions or suggestions, feel free to reach out to me at [Tetralon07@gmail.com](mailto:Tetralon07@gmail.com).

Also feel free to check out the [GitHub repository](https://github.com/Bikatr7/EasyTL) for this project.

Or the issue tracker [here](https://github.com/Bikatr7/EasyTL/issues).

---------------------------------------------------------------------------------------------------------------------------------------------------

**Contribution**<a name="contribution"></a>

Contributions are welcome! I don't have a specific format for contributions, but please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

---------------------------------------------------------------------------------------------------------------------------------------------------

**Notes**<a name="notes"></a>

EasyTL was originally developed as a part of [Kudasai](https://github.com/Bikatr7/Kudas

ai), a Japanese preprocessor later turned Machine Translator. It was later split off into its own package to be used independently of Kudasai for multiple reasons.

This package is also my second serious attempt at creating a Python package, so I'm sure there are some things that could be improved. Feedback is welcomed.

---------------------------------------------------------------------------------------------------------------------------------------------------