"""Opt-in cross-browser smoke tests for local or deployed Alora."""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import sync_playwright

pytestmark = pytest.mark.e2e

BASE_URL = os.getenv("ALORA_E2E_URL", "").strip()


@pytest.mark.skipif(not BASE_URL, reason="Set ALORA_E2E_URL for browser tests")
@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_alora_shell_cross_browser(browser_name):
    with sync_playwright() as playwright:
        browser_type = getattr(playwright, browser_name)
        browser = browser_type.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120_000)
            page.get_by_text("Alora AI", exact=True).first.wait_for(timeout=120_000)
            page.wait_for_timeout(2_000)
            body = page.locator("body").inner_text()
            assert "Upload Your Lesson" in body
            assert "AI service ready" in body or "Administrator settings" in body
            expected = os.getenv("ALORA_EXPECTED_VERSION", "").strip()
            if expected:
                assert f"v{expected}" in body

            # Minimal runtime accessibility gate; full WCAG testing remains separate.
            assert page.locator("h1, h2, h3").count() > 0
            assert page.locator("button").count() > 0
            assert page.evaluate(
                """() => [...document.querySelectorAll('button')].every(
                  el => (el.innerText || el.getAttribute('aria-label') || el.title || '').trim().length > 0
                )"""
            )
        finally:
            browser.close()


@pytest.mark.skipif(not BASE_URL, reason="Set ALORA_E2E_URL for browser tests")
@pytest.mark.parametrize("viewport", [(320, 800), (768, 1024), (1440, 1000)])
def test_responsive_shell_has_no_document_overflow(viewport):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120_000)
            page.get_by_text("Alora AI", exact=True).first.wait_for(timeout=120_000)
            page.wait_for_timeout(2_000)
            overflow = page.evaluate(
                """() => Math.max(
                  document.documentElement.scrollWidth,
                  document.body.scrollWidth
                ) - window.innerWidth"""
            )
            assert overflow <= 2
        finally:
            browser.close()


@pytest.mark.skipif(not BASE_URL, reason="Set ALORA_E2E_URL for browser tests")
def test_dashboard_has_no_critical_or_serious_axe_violations():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120_000)
            page.get_by_text("Alora AI", exact=True).first.wait_for(timeout=120_000)
            page.wait_for_timeout(2_000)
            page.add_script_tag(
                url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"
            )
            result = page.evaluate(
                """async () => await axe.run(document, {
                  resultTypes: ['violations'],
                  runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag22aa']}
                })"""
            )
            blockers = [
                violation
                for violation in result["violations"]
                if violation.get("impact") in {"critical", "serious"}
            ]
            assert blockers == [], [
                {
                    "id": item["id"],
                    "impact": item["impact"],
                    "nodes": len(item.get("nodes") or []),
                }
                for item in blockers
            ]
        finally:
            browser.close()
