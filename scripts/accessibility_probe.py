"""Print actionable axe/browser accessibility findings for an Alora URL."""

from __future__ import annotations

import json
import os

from playwright.sync_api import sync_playwright


def main() -> None:
    url = os.getenv("ALORA_E2E_URL", "http://127.0.0.1:8501")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.get_by_text("Alora AI", exact=True).first.wait_for(timeout=60_000)
        page.wait_for_timeout(2_000)
        unlabeled = page.evaluate(
            """() => [...document.querySelectorAll('button')]
              .filter(el => !(el.innerText || el.getAttribute('aria-label') || el.title || '').trim())
              .map(el => el.outerHTML.slice(0, 500))"""
        )
        upload_hint = page.evaluate(
            """() => {
              const el = [...document.querySelectorAll('span')]
                .find(node => (node.textContent || '').includes('per file'));
              if (!el) return null;
              return {
                color: getComputedStyle(el).color,
                parents: [...function* () {
                  let node = el;
                  while (node && node !== document.body) {
                    yield node.outerHTML.slice(0, 220);
                    node = node.parentElement;
                  }
                }()].slice(0, 5)
              };
            }"""
        )
        page.add_script_tag(
            url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"
        )
        result = page.evaluate(
            """async () => await axe.run(document, {
              runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag22aa']}
            })"""
        )
        violations = []
        for violation in result["violations"]:
            if violation.get("impact") not in {"critical", "serious"}:
                continue
            violations.append(
                {
                    "id": violation["id"],
                    "impact": violation["impact"],
                    "nodes": [
                        {
                            "target": node["target"],
                            "html": node["html"],
                            "summary": node["failureSummary"],
                        }
                        for node in violation["nodes"]
                    ],
                }
            )
        print(
            json.dumps(
                {
                    "url": url,
                    "unlabeled_buttons": unlabeled,
                    "upload_hint": upload_hint,
                    "violations": violations,
                },
                indent=2,
            )
        )
        browser.close()


if __name__ == "__main__":
    main()
