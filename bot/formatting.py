"""Превращаем данные из core.market в красивый текст для Telegram (HTML)."""
from html import escape

from core.market import PriceInfo, Overview

CURRENCY_SIGNS = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "RUB": "₽"}


def money(value: float, currency: str) -> str:
    sign = CURRENCY_SIGNS.get(currency)
    return f"{sign}{value:,.2f}" if sign else f"{value:,.2f} {currency}"


def big_number(value: float | None) -> str:
    """5118960861184 -> 5.12T"""
    if value is None:
        return "—"
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if abs(value) >= limit:
            return f"{value / limit:.2f}{suffix}"
    return f"{value:,.0f}"


def num(value: float | None, suffix: str = "") -> str:
    return "—" if value is None else f"{value:.2f}{suffix}"


def format_price(p: PriceInfo) -> str:
    arrow = "🟢" if p.change >= 0 else "🔴"
    sign = "+" if p.change >= 0 else ""
    return (
        f"📈 <b>{escape(p.name)}</b> ({p.ticker})\n"
        f"\n"
        f"Цена: <b>{money(p.price, p.currency)}</b>\n"
        f"За день: {sign}{p.change:.2f} ({sign}{p.change_pct:.2f}%) {arrow}\n"
        f"\n"
        f"Подробнее: /overview {p.ticker}"
    )


def format_overview(o: Overview) -> str:
    lines = [f"🏢 <b>{escape(o.name)}</b> ({o.ticker})", ""]

    if o.sector or o.industry:
        lines.append(f"Сектор: {escape(o.sector or '—')} / {escape(o.industry or '—')}")
    if o.country:
        lines.append(f"Страна: {escape(o.country)}")
    lines += [
        "",
        "<b>Ключевые метрики</b>",
        f"Капитализация: {big_number(o.market_cap)} {o.currency}",
        f"P/E (за 12 мес.): {num(o.trailing_pe)}",
        f"P/E (прогноз): {num(o.forward_pe)}",
        f"Дивидендная доходность: {num(o.dividend_yield, '%')}",
    ]
    if o.low_52w is not None and o.high_52w is not None:
        lines.append(
            f"Диапазон за 52 недели: {money(o.low_52w, o.currency)} — {money(o.high_52w, o.currency)}"
        )
    if o.summary:
        # Полное описание длинное — обрезаем до ~400 символов
        short = o.summary if len(o.summary) <= 400 else o.summary[:400].rsplit(" ", 1)[0] + "…"
        lines += ["", f"<i>{escape(short)}</i>"]
    if o.website:
        lines += ["", escape(o.website)]
    return "\n".join(lines)
