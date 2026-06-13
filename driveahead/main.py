from __future__ import annotations


def main() -> None:
    try:
        from driveahead.modes.local_match import run_local_match
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependency"
        print(
            f"Missing dependency: {missing}. "
            'Install with: python -m pip install -e ".[dev]"'
        )
        raise SystemExit(1) from exc

    run_local_match()


if __name__ == "__main__":
    main()
