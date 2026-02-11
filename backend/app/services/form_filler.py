"""
Google Form Auto-Filler Engine using Playwright.
Detects all field types dynamically and fills them using profile data + AI.
"""
import asyncio
import datetime
import re
from typing import Dict, List, Optional, Any

try:
    from playwright.async_api import async_playwright, Page, Locator
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

from app.config import HEADLESS, SLOW_MO
from app.services.question_matcher import match_question_to_field
from app.services.ai_agent import generate_answer


class FormFillerEngine:
    """Automated Google Form filler using Playwright."""

    def __init__(self, profile_data: Dict[str, str], learned_mappings: Dict[str, str] = None):
        self.profile = profile_data
        self.learned = learned_mappings or {}
        self.log: List[Dict[str, Any]] = []
        self.questions_detected = 0
        self.questions_filled = 0
        self.ai_answers_used = 0
        self.form_title = ""
        self.new_mappings: List[Dict[str, str]] = []

    def _add_log(self, question: str, field_type: str, answer: str, source: str, status: str):
        self.log.append({
            "question": question,
            "field_type": field_type,
            "answer": answer,
            "source": source,
            "status": status,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        })

    def _get_answer(self, question: str) -> tuple:
        """
        Get answer for question.
        Returns: (answer, source) where source is 'profile', 'learned', or 'ai'
        """
        # 1. Check learned mappings first
        q_lower = question.strip().lower()
        for learned_q, learned_val in self.learned.items():
            if learned_q.lower() == q_lower:
                return learned_val, "learned"

        # 2. Try matching to profile field
        field_name, confidence = match_question_to_field(question)
        if field_name and field_name in self.profile:
            value = self.profile[field_name]
            if value and value.strip():
                # Save as learned mapping for future
                self.new_mappings.append({
                    "question": question,
                    "field": field_name,
                    "value": value,
                    "confidence": int(confidence * 100),
                })
                return value, f"profile ({field_name}, {confidence:.0%})"

        # 3. Use AI agent to generate answer
        ai_answer = generate_answer(question, self.profile)
        self.ai_answers_used += 1
        self.new_mappings.append({
            "question": question,
            "field": "ai_generated",
            "value": ai_answer,
            "confidence": 70,
        })
        return ai_answer, "ai_generated"

    async def _fill_text_input(self, container: 'Locator', question: str):
        """Fill a short text input field."""
        answer, source = self._get_answer(question)
        input_el = container.locator('input[type="text"], input[type="email"], input[type="url"], input[type="tel"], input:not([type])')
        
        try:
            first_input = input_el.first
            if await first_input.count() > 0:
                await first_input.click()
                await first_input.fill("")
                await first_input.fill(str(answer))
                self.questions_filled += 1
                self._add_log(question, "text", str(answer), source, "filled")
                return True
        except Exception as e:
            self._add_log(question, "text", str(answer), source, f"error: {e}")
        return False

    async def _fill_textarea(self, container: 'Locator', question: str):
        """Fill a paragraph/textarea field."""
        answer, source = self._get_answer(question)
        textarea = container.locator("textarea")
        
        try:
            if await textarea.count() > 0:
                await textarea.first.click()
                await textarea.first.fill("")
                await textarea.first.fill(str(answer))
                self.questions_filled += 1
                self._add_log(question, "paragraph", str(answer), source, "filled")
                return True
        except Exception as e:
            self._add_log(question, "paragraph", str(answer), source, f"error: {e}")
        return False

    async def _fill_radio(self, container: 'Locator', question: str):
        """Select a radio button option."""
        answer, source = self._get_answer(question)
        options = container.locator('[role="radio"], [data-value]')
        
        try:
            count = await options.count()
            if count == 0:
                options = container.locator('label, .docssharedWizToggleLabeledContent')
                count = await options.count()

            if count > 0:
                answer_lower = str(answer).lower().strip()
                best_match = None
                best_score = 0

                for i in range(count):
                    opt = options.nth(i)
                    text = (await opt.inner_text()).strip().lower()
                    data_val = await opt.get_attribute("data-value") or ""

                    if text == answer_lower or data_val.lower() == answer_lower:
                        best_match = i
                        best_score = 1.0
                        break

                    if answer_lower in text or text in answer_lower:
                        score = len(answer_lower) / max(len(text), 1)
                        if score > best_score:
                            best_match = i
                            best_score = score

                if best_match is not None:
                    await options.nth(best_match).click()
                    self.questions_filled += 1
                    selected_text = (await options.nth(best_match).inner_text()).strip()
                    self._add_log(question, "radio", selected_text, source, "filled")
                    return True
                else:
                    await options.first.click()
                    self.questions_filled += 1
                    selected_text = (await options.first.inner_text()).strip()
                    self._add_log(question, "radio", selected_text, "fallback_first", "filled")
                    return True
        except Exception as e:
            self._add_log(question, "radio", str(answer), source, f"error: {e}")
        return False

    async def _fill_checkbox(self, container: 'Locator', question: str):
        """Select checkbox options."""
        answer, source = self._get_answer(question)
        options = container.locator('[role="checkbox"], label.docssharedWizToggleLabeledContent')
        
        try:
            count = await options.count()
            if count > 0:
                answer_parts = [a.strip().lower() for a in str(answer).split(",")]
                checked = False
                for i in range(count):
                    opt = options.nth(i)
                    text = (await opt.inner_text()).strip().lower()
                    for part in answer_parts:
                        if part in text or text in part:
                            await opt.click()
                            checked = True
                            break
                if not checked:
                    await options.first.click()
                self.questions_filled += 1
                self._add_log(question, "checkbox", str(answer), source, "filled")
                return True
        except Exception as e:
            self._add_log(question, "checkbox", str(answer), source, f"error: {e}")
        return False

    async def _fill_dropdown(self, container: 'Locator', question: str):
        """Select from a dropdown menu."""
        answer, source = self._get_answer(question)
        try:
            dropdown = container.locator('[role="listbox"], .quantumWizMenuPaperselectEl')
            if await dropdown.count() > 0:
                await dropdown.first.click()
                await asyncio.sleep(0.5)
                options = container.locator('[role="option"], .quantumWizMenuPaperselectOption')
                count = await options.count()
                answer_lower = str(answer).lower().strip()
                best_match = None
                for i in range(count):
                    text = (await options.nth(i).inner_text()).strip().lower()
                    if text == answer_lower or answer_lower in text:
                        best_match = i
                        break
                if best_match is not None:
                    await options.nth(best_match).click()
                else:
                    idx = 1 if count > 1 else 0
                    await options.nth(idx).click()
                self.questions_filled += 1
                self._add_log(question, "dropdown", str(answer), source, "filled")
                return True
        except Exception as e:
            self._add_log(question, "dropdown", str(answer), source, f"error: {e}")
        return False

    async def _fill_date(self, container: 'Locator', question: str):
        """Fill a date input field."""
        answer, source = self._get_answer(question)
        try:
            date_input = container.locator('input[type="date"]')
            if await date_input.count() > 0:
                await date_input.first.fill(str(answer))
                self.questions_filled += 1
                self._add_log(question, "date", str(answer), source, "filled")
                return True
            inputs = container.locator("input")
            count = await inputs.count()
            if count >= 2:
                today = datetime.date.today()
                date_parts = [str(today.day), str(today.month), str(today.year)]
                for i in range(min(count, 3)):
                    await inputs.nth(i).fill(date_parts[i] if i < len(date_parts) else "")
                self.questions_filled += 1
                self._add_log(question, "date", f"{today}", source, "filled")
                return True
        except Exception as e:
            self._add_log(question, "date", str(answer), source, f"error: {e}")
        return False

    async def _detect_and_fill_question(self, container: 'Locator'):
        """Detect field type and fill."""
        question_label = container.locator('[role="heading"], .freebirdFormviewerComponentsQuestionBaseTitle, .M7eMe')
        question_text = ""
        try:
            if await question_label.count() > 0:
                question_text = (await question_label.first.inner_text()).strip()
        except: pass
        if not question_text:
            try:
                all_text = await container.inner_text()
                lines = [l.strip() for l in all_text.split("\n") if l.strip()]
                question_text = lines[0] if lines else ""
            except: return
        if not question_text or len(question_text) < 2: return
        self.questions_detected += 1
        
        if await container.locator("textarea").count() > 0:
            await self._fill_textarea(container, question_text)
        elif await container.locator('[role="radio"]').count() > 0:
            await self._fill_radio(container, question_text)
        elif await container.locator('[role="checkbox"]').count() > 0:
            await self._fill_checkbox(container, question_text)
        elif await container.locator('[role="listbox"]').count() > 0:
            await self._fill_dropdown(container, question_text)
        elif await container.locator('input[type="date"]').count() > 0:
            await self._fill_date(container, question_text)
        else:
            text_inputs = container.locator('input[type="text"], input[type="email"], input[type="url"], input[type="tel"], input[type="number"], input:not([type])')
            if await text_inputs.count() > 0:
                await self._fill_text_input(container, question_text)
            else:
                self._add_log(question_text, "unknown", "", "none", "skipped")

    async def fill_form(self, form_url: str, auto_submit: bool = False) -> Dict[str, Any]:
        """Main entry: fill form (Lite protected)."""
        result = {
            "status": "pending", "form_title": "", "questions_detected": 0,
            "questions_filled": 0, "ai_answers_used": 0, "auto_submitted": False,
            "error_message": "", "fill_log": [], "new_mappings": [],
        }

        if not HAS_PLAYWRIGHT:
            result["status"] = "failed"
            result["error_message"] = "Browser automation is disabled in this environment (Lite mode)."
            return result

        async with async_playwright() as p:
            browser = None
            try:
                browser = await p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
                context = await browser.new_context(viewport={"width": 1280, "height": 900})
                page = await context.new_page()
                await page.goto(form_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                try:
                    title_el = page.locator('[role="heading"][aria-level="1"], .freebirdFormviewerViewHeaderTitle, .F9yp7e')
                    if await title_el.count() > 0:
                        self.form_title = (await title_el.first.inner_text()).strip()
                except: self.form_title = "Untitled Form"
                result["form_title"] = self.form_title

                for page_attempt in range(5): # Multi-page support
                    question_containers = page.locator('[role="listitem"], .geS5n, .Qr7Oae')
                    count = await question_containers.count()
                    for i in range(count):
                        await self._detect_and_fill_question(question_containers.nth(i))
                    
                    next_btn = page.locator('div[role="button"]:has-text("Next"), span:has-text("Next")')
                    if await next_btn.count() > 0:
                        await next_btn.first.click()
                        await asyncio.sleep(1.5)
                    else: break

                if auto_submit:
                    submit_btn = page.locator('div[role="button"]:has-text("Submit"), .freebirdFormviewerNavigationSubmitButton')
                    if await submit_btn.count() > 0:
                        await submit_btn.first.click()
                        await asyncio.sleep(2)
                        result["auto_submitted"] = True

                result["status"] = "completed"
            except Exception as e:
                result["status"] = "failed"
                result["error_message"] = str(e)
            finally:
                if browser: await browser.close()

        result["questions_detected"] = self.questions_detected
        result["questions_filled"] = self.questions_filled
        result["ai_answers_used"] = self.ai_answers_used
        result["fill_log"] = self.log
        result["new_mappings"] = self.new_mappings
        return result
