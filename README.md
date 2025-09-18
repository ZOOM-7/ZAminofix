
# ZAminofix ✨
Elegant and powerful Python framework for creating Amino bots and automation scripts.


---

## 🚀 Quick Navigation
- [Installation](#-installation) | [Quick Start](#-quick-start) | [Documentation](#-documentation) | [Examples](#-examples) | [Support](#-support) | [Contributing](#-contributing)

---

## ⚡ Installation
```bash
pip install ZAmino.fix
````

---

## ⚙️ Quick Start

```python
from ZAminofix import Client, SubClient, ChatEvent
client = Client()
client.login("your_email@example.com", "your_password")
client.pubkey()

```

---

## 📚 Documentation

### Core Components

**Client - Main Connection Handler:** The `Client` class manages your connection to Amino services and handles global operations.
**Authentication Options:**

```python
client.login("email@example.com", "password123")

client.login("+1234567890", "password123")

client.login("your_sid")
```

**Event System:**

```python
import ZAminofix
c = ZAminofix.Client()

def on_text_message(data: ZAminofix.objects.Event):
    print(f"Message: {data.message.content}")
c.register_events(globals())
```

**SubClient - Community Operations:**

```python
sub_client = SubClient(comId=123456)
sub_client.send_message(chatId="chat_id", message="Hello World!")
```

---

## 🧪 Examples

### Command Bot

```python
from ZAminofix import Client, SubClient
import random
client = Client()
client.login("email", "password")
client.pubkey()
commands = {
    '/help': 'Available commands:\n/dice - Roll a dice\n/joke - Get a random joke',
    '/dice': lambda: f'You rolled: {random.randint(1, 6)}!'
}

def handle_command(data):
    message = data.message.content.lower()
    if message in commands:
        sub_client = SubClient(comId=data.comId)
        response = commands[message]
        if callable(response): response = response()
        sub_client.send_message(chatId=data.message.chatId, message=response)

c.register_events(globals())
```

---

## 🛠️ Support

Telegram: [@ZAminoZ](https://t.me/ZAminoZ)

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! Please follow the standard GitHub pull request workflow.
