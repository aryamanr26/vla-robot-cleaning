def banner(title: str):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def section(title: str):
    print("\n" + "-" * 72)
    print(title)
    print("-" * 72)


def log(msg: str):
    print(f"  {msg}")


def ok(msg: str):
    print(f"  [OK]    {msg}")


def fail(msg: str):
    print(f"  [FAIL]  {msg}")
