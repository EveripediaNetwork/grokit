<div align="center">
  <img src="./misc/grokit.svg" alt="Logo" height="70" />
  <p><strong>Unofficial Python client for Grok models</strong></p>
</div>
<br/>

<p align="center">
    <a href="https://pypi.python.org/pypi/grokit/"><img alt="PyPi" src="https://img.shields.io/pypi/v/grokit.svg?style=flat-square"></a>
    <a href="https://github.com/EveripediaNetwork/grokit/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/EveripediaNetwork/grokit.svg?style=flat-square"></a>
</p>

## Installation

```bash
pip install grokit
```

## Usage
Import the `Grokit` class and create an instance:

```python
from grokit import Grokit
Generate a response:
# Or use the X_AUTH_TOKEN and X_CSRF_TOKEN environment variables
grok = Grokit(
    # auth_token='your_auth_token_here',
    # csrf_token='your_csrf_token_here',
)
```

## Generate

```python
response = grok.generate('Who are you?', model_id='grok-2-mini')
print(response)
```

## Stream

```python
for chunk in grok.stream('Who are you?', model_id='grok-2'):
    print(chunk, end='', flush=True)
```

## Credentials

To obtain the necessary credentials for using Grokit, follow these steps:

1. Log in to [x.com](https://x.com) with a Premium account.

2. Open your browser's Developer Tools.

3. Navigate to the Network tab in the Developer Tools.

4. Load [x.com/i/grok](https://x.com/i/grok) in your browser.

5. In the Network tab, look for the first request.

6. Click on this request to view its details.

7. In the Headers section, find the "Cookie" header under Request Headers.

8. From the cookie string, extract the following values:
   - `ct0`: This is your X_CSRF_TOKEN
   - `auth_token`: This is your X_AUTH_TOKEN
