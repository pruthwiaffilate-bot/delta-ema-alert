"""Entry point for delta-ema-alert bot."""
from __future__ import annotations

import sys
import traceback
from config import load_config
from logger import get_logger
from state import StateManager
from scheduler import Scheduler


def main() -> int:
    logger = get_logger("delta-ema-main")
    try:
        config = load_config()
        state = StateManager()
        # store some metadata
        state.set("symbols", config.symbols)
        sched = Scheduler(config, state)
        sched.start()
        return 0
    except Exception as exc:
        logger.exception("Unhandled error in main: %s", exc)
        try:
            # best-effort crash reporting
            from telegram_bot import TelegramBot
            tb = TelegramBot(
                token=getattr(locals().get('config', None), 'telegram_token', None) or "",
                chat_id=getattr(locals().get('config', None), 'chat_id', None) or "",
                state=StateManager(),
            )
            tb.send_error(f"Fatal error: {exc}\n{traceback.format_exc()}")
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
