import re
import wikipedia
import json
import os
import time
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

class WikipediaCompleter(Completer):
    def __init__(self, wiki_handler):
        """Initialize the completer with a Wikipedia handler."""
        self.wiki_handler = wiki_handler

    def get_completions(self, document, complete_event):
        """Yield suggestions as the user types."""
        query = document.text
        if len(query) >= 3:  # Start suggesting after 3 characters
            suggestions = self.wiki_handler.auto_suggest(query)
            for suggestion in suggestions:
                yield Completion(suggestion, start_position=-len(query))


class WikipediaHandler:
    def __init__(self, cache_file='cache.json'):
        """Initialize the Wikipedia handler with optional caching."""
        wikipedia.set_lang("en")  # Set the language to English
        self.cache_file = cache_file
        self.load_cache()

    def load_cache(self):
        """Load cached results from a JSON file."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def save_cache(self):
        """Save cached results to a JSON file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def fetch_wikipedia_info(self, query, summary_type="Medium"):
        """Fetch summary from Wikipedia based on the query."""
        if query in self.cache:
            cached_summary, cached_url, timestamp = self.cache[query]
            if time.time() - timestamp < 3600:  # Cache for 1 hour
                return cached_summary, cached_url

        try:
            page = wikipedia.page(query)
            summary = page.summary
            summary = self.remove_citations(summary)

            if summary_type == "Medium":
                summary = '. '.join(summary.split('. ')[:3]) + '.'  # Limit to first 3 sentences
            # No change needed for Detailed summary

            self.cache[query] = (summary, page.url, time.time())
            self.save_cache()

            return summary, page.url
        except wikipedia.exceptions.DisambiguationError as e:
            options = ', '.join(e.options)
            return (f"Disambiguation error: Multiple results found for '{query}'. "
                    f"Suggestions: {options}"), None
        except wikipedia.exceptions.PageError:
            return (f"Error: No Wikipedia page found for '{query}'. "
                    "Please check the spelling or try a different term."), None
        except Exception as e:
            return f"Error fetching Wikipedia info: {str(e)}", None

    def remove_citations(self, text):
        """Remove citation references from the text."""
        return re.sub(r'\[\d+\]', '', text)

    def auto_suggest(self, query):
        """Return a list of auto-suggestions based on the query."""
        return wikipedia.search(query)


# Example usage:
if __name__ == "__main__":

    wiki_handler = WikipediaHandler()
    completer = WikipediaCompleter(wiki_handler)

    query = prompt("Enter a topic to search: ", completer=completer)

    summary_type = input("\nEnter summary type (Medium/Detailed): ").capitalize()
    summary, url = wiki_handler.fetch_wikipedia_info(query, summary_type)

    print(f"\nSummary:\n{summary}\nMore info: {url}")
