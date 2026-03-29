from app.model_schemas.question_and_answer_models import Questions_And_Answers
from app.services.base_scraper import BaseScraperStrategy
import asyncio


class QuestionScraperStrategy(BaseScraperStrategy):
    async def scrape(self):
        tasks = [asyncio.create_task(self._parse(url=url['url'])) for url in self.scraping_metadata['scraping_metadata']]
        question_data = await self.get_results(label=f"Scraping {self.scraping_metadata['subject']} data", tasks=tasks)
        return question_data

    async def _parse(self, url, **kwargs):
        soup = await self._fetch(url)
        question_elements = soup.select('div.question-desc.mb-3 p')
        question = " ".join([x.get_text(strip=True) for x in question_elements if x])

        # Extract exam details
        exam_info = soup.select("div.mb-2.badge.bg-success.text-light")
        subject = exam_info[0].get_text() if len(exam_info) > 0 else 'N/A'
        exam_details = exam_info[1].get_text().split() if len(exam_info) > 1 else ['N/A', 'N/A']
        exam_type = exam_details[0]
        year = exam_details[1]

        # Extract options
        options_elements = soup.select('ul.list-unstyled li')
        options = []
        for option in options_elements:
            option_text = option.get_text(strip=True)
            options.append(option_text)
        options = options or 'N/A'
        # Extract the correct answer
        correct_answer_element = soup.select_one("#page-content-section > div.mb-4 > h5.text-success.mb-3")
        correct_answer = correct_answer_element.get_text(strip=True) if correct_answer_element else 'N/A'

        # Extract and clean explanation
        explanation_element = soup.select_one("#page-content-section > div.mb-4")

        if explanation_element:
            explanation_element.attrs = {}
            explanation_text = explanation_element.get_text(strip=True)
            explanation_text = explanation_text if 'No official explanation' not in explanation_text and 'See page' not in explanation_text else 'N/A'
            for tag in explanation_element.find_all(True):
                tag.attrs = {}
                if tag.get_text(strip=True).startswith('There is an explanation') \
                        or 'See page' in tag.get_text(strip=True) or tag.get_text(
                    strip=True).strip() == 'Explanation' or tag.get_text(strip=True) == correct_answer:
                    tag.decompose()

            explanation_html = explanation_element.prettify()
            explanation_cleaned = explanation_html.replace('\n', '')
            explanation_cleaned = explanation_cleaned.replace('&amp;', '&')
            if 'No official explanation' in explanation_cleaned:
                explanation = 'N/A'
            else:
                explanation = explanation_cleaned
        else:
            explanation = 'N/A'
            explanation_text = 'N/A'

        image_element = soup.select_one('#page-content-section > div.question-desc.mb-3 > div.mb-4 > img')
        image_url = image_element.get('src') if image_element else 'N/A'

        return Questions_And_Answers(
            question=question,
            options=str(options),
            correct_answer=correct_answer,
            explanation_html=str(explanation),
            explanation_text=explanation_text,
            subject=subject,
            exam_type=exam_type,
            year=year,
            url=url,
            image_url=image_url
        )
