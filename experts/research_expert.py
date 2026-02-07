import json
import logging
import os
import time
from typing import Any, Union

try:
    from github import Github

    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


import wikipedia
from duckduckgo_search import DDGS

from .base_expert import BaseExpert

logger = logging.getLogger(__name__)


class ResearchExpert(BaseExpert):
    def __init__(self, brain_ref):
        super().__init__(
            name="ResearchExpert",
            description="Hybrid Researcher...",
            version="3.0-Hybrid",
            model_name="llama3.1:8b",  # <--- CHANGED
        )
        self.brain = brain_ref
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_name = os.getenv("GITHUB_REPO", "mrX1007/FusionBrain")

        self.gh_client = None
        if GITHUB_AVAILABLE and self.github_token:
            self.gh_client = Github(self.github_token)

    def run(self, params: str | dict[str, Any]) -> str:
        raw_topic = params.get("prompt", "") if isinstance(params, dict) else str(params)

        topic = raw_topic.strip(" .?!")

        logger.info(f"Starting research on: {topic}")
        print(f"\n[ResearchExpert] 🕵️‍♂️ Analyzing topic: '{topic}'...")

        results = self._fetch_data_hybrid(topic)

        if not results:
            return "No information found. Try a broader topic."

        report = []
        print(f"[ResearchExpert] Found {len(results)} sources. AI Filtering started...")

        for item in results[:5]:
            title = item.get("title", "No Title")
            snippet = item.get("body", "")
            link = item.get("href", "")

            try:
                score, reason = self._evaluate_relevance(title, snippet)
            except Exception as e:
                logger.error(f"Evaluation failed: {e}")
                continue

            if score < 5:
                print(f"   🗑️ [Skip] {title[:30]}... (Score: {score})")
                continue

            print(f"   ✅ [Keep] {title[:30]}... (Score: {score})")

            if score >= 6:
                self._save_to_memory(title, snippet, link, score)

            # GitHub Issue
            if score >= 8:
                self._create_github_proposal(title, snippet, link, reason)

            report.append(
                f"### {title} (Score: {score}/10)\n_{reason}_\n> {snippet[:200]}...\n[Source]({link})\n"
            )
            time.sleep(0.2)

        return "\n".join(report) if report else "Found nothing relevant enough."

    def _fetch_data_hybrid(self, query: str) -> list[dict[str, str]]:
        """
        Стратегия:
        1. DuckDuckGo (свежие новости).
        2. Если пусто -> Wikipedia (базовые знания).
        """
        results = []

        try:
            with DDGS() as ddgs:
                ddg_gen = ddgs.text(query, max_results=5, backend="lite")
                if ddg_gen:
                    results = list(ddg_gen)
                    print(f"   [Source] DuckDuckGo returned {len(results)} results.")
        except Exception as e:
            logger.warning(f"DDG Search failed: {e}")

        if len(results) < 2:
            print("   [Source] Engaging Wikipedia fallback...")
            try:
                wikipedia.set_lang("en")

                wiki_pages = wikipedia.search(query, results=2)

                for page_name in wiki_pages:
                    try:
                        summary = wikipedia.summary(page_name, sentences=3)
                        url = wikipedia.page(page_name).url
                        results.append(
                            {"title": f"Wiki: {page_name}", "body": summary, "href": url}
                        )
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"Wikipedia search failed: {e}")

        return results

    def _evaluate_relevance(self, title: str, snippet: str) -> tuple[int, str]:
        system_prompt = (
            "You are a technical filter for an AGI project."
            "Evaluate relevance (0-10) of the content for a developer."
            'Return raw JSON: {"score": int, "reason": "string"}.'
        )
        user_prompt = f"Topic: {title}\nDetails: {snippet}"

        raw_response = self._ask_model(user_prompt, system_prompt)

        # Robust JSON cleaning
        clean_json = raw_response.strip()
        if "```" in clean_json:
            clean_json = clean_json.split("```json")[-1].split("```")[0].strip()

        try:
            data = json.loads(clean_json)
            return int(data.get("score", 0)), data.get("reason", "Interesting")
        except Exception:
            if "quantum" in title.lower() or "ai" in title.lower():
                return 7, "Keyword match (Auto-approved)"
            return 5, "Parsing failed"

    def _save_to_memory(self, title: str, snippet: str, link: str, score: int):
        if hasattr(self.brain, "knowledge"):
            fact = f"RESEARCH (Score {score}): {title}. {snippet} Source: {link}"
            self.brain.knowledge.add(fact, category="research", tags=["auto"])

    def _create_github_proposal(self, title: str, snippet: str, link: str, reason: str):
        if not self.gh_client:
            return

        try:
            repo = self.gh_client.get_repo(self.repo_name)
            for issue in repo.get_issues(state="open"):
                if title[:30] in issue.title:
                    return

            body = f"**Relevance:** {reason}\n\n**Context:**\n{snippet}\n\n**Source:** {link}"
            repo.create_issue(title=f"[Research] {title}", body=body, labels=["enhancement"])
            print(f"   💎 [GitHub] Created Issue: {title}")
        except Exception as e:
            logger.error(f"GitHub Error: {e}")
