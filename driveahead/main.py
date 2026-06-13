from __future__ import annotations

import argparse


def main() -> None:
    try:
        from driveahead.modes.lan_match import run_lan_client, run_lan_host
        from driveahead.modes.local_match import run_local_match
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependency"
        print(
            f"Missing dependency: {missing}. "
            'Install with: python -m pip install -e ".[dev]"'
        )
        raise SystemExit(1) from exc

    args = _parse_args()
    if args.host:
        run_lan_host(port=args.port)
    elif args.join:
        run_lan_client(args.join, port=args.port)
    else:
        run_local_match()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DriveAhead MVP")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--host", action="store_true", help="Host a LAN 1v1 match as Player 1.")
    mode.add_argument("--join", metavar="HOST_IP", help="Join a LAN 1v1 match as Player 2.")
    parser.add_argument("--port", type=int, default=38271, help="UDP port for LAN play.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
