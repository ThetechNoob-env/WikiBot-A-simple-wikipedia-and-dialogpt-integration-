import re
import wikipedia

class WikipediaHandler:
    def __init__(self):
        wikipedia.set_lang("en")  # Set the language to English

    def fetch_wikipedia_info(self, query, summary_type="Medium"):
        """Fetch summary from Wikipedia based on the query."""
        try:
            # Fetch the page using the user's query
            page = wikipedia.page(query)

            # Extract the summary
            summary = page.summary

            # Clean the summary by removing citations
            summary = self.remove_citations(summary)

            # Adjust summary length based on summary_type
            if summary_type == "Medium":
                # Limit to first 3 sentences
                summary = '. '.join(summary.split('. ')[:3]) + '.'
            elif summary_type == "Detailed":
                # Return the full summary without alteration
                pass  # No change needed for detailed summary

            return summary, page.url
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation with a user-friendly message
            return (f"Disambiguation error: There are multiple results for '{query}'. "
                    f"Suggestions: {', '.join(e.options)}"), None
        except wikipedia.exceptions.PageError:
            # Handle the case when no page is found
            return (f"Error: No Wikipedia page found for '{query}'. "
                    "Please check the spelling or try a different term."), None
        except Exception as e:
            # Generic error handling
            return f"Error fetching Wikipedia info: {str(e)}", None

    def remove_citations(self, text):
        """Remove citation references from the text."""
        return re.sub(r'\[\d+\]', '', text)
