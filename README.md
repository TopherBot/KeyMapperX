# KeyMapperX

KeyMapperX is a small Python utility that allows you to define controller/key mappings via a JSON profile. The profile can be edited while the program is running – changes are hot‑reloaded.

## Features
- Modular JSON grip‑strength profiles
- Live‑reload on file change
- Configurable action callbacks
- Works with any HID gamepad supported by `pygame`

## Installation
```bash
pip install pygame watchdog
```

## Usage
```bash
python mapper.py profile.json
```
Edit `profile.json` to change mappings on the fly. The program will automatically pick up the changes.

## License
MIT
