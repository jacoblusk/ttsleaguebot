# Installation
You can install directly from GitHub using the command below,
```
pip install git+https://github.com/jacoblusk/ttsleaguebot
```
# Usage

After installation, you'll have access to the following programs,
- `ttsleaguebot`

You must ensure you have your service account's credentials in `credentials.json`, placed in the directory you invoke the bot.
Learn more about creating a Google service account [here]([here](https://cloud.google.com/iam/docs/service-accounts-create)).

You will also need a Discord Bot token inside a file named `bot_token`, which will be placed in the same directory you invoke the bot.

## Troubleshooting

If you don't have `ttsleaguebot` in your path, ensure you have your `Scripts`, which is found in your Python installation folder, in your path.
Run the following to find your Python installation folder.
```py
import sys
print(sys.exec_prefix)
```
