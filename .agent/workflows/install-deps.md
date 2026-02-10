---
description: How to install Python dependencies on this system
---

# Install Python Dependencies

On this system, `pip` is **not** directly on the PATH. Always use the `py` launcher instead.

// turbo-all

1. Install from requirements.txt:
```
py -m pip install -r requirements.txt
```

2. Install a single package:
```
py -m pip install <package-name>
```

3. Upgrade pip itself:
```
py -m pip install --upgrade pip
```

> **Note:** Never use bare `pip` or `pip install` — it will fail with `CommandNotFoundException`.
