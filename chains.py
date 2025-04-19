import os
import json
import re
from together import Together
from langchain.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Chain:
    def __init__(self):
        """Initialize the Chain class with TogetherAI API."""
        self.api_key = os.getenv("TOGETHER_API_KEY")

        if not self.api_key:
            raise ValueError("❌ API Key not found. Please set the TOGETHER_API_KEY environment variable.")

        self.client = Together(api_key=self.api_key)
        self.model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    def extract_jobs(self, cleaned_text):
        """Extract job details from a scraped webpage and return structured JSON."""
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            
            ### INSTRUCTION:
            Extract job postings and return a JSON array with:
            - `role` (Job title)
            - `experience` (Years of experience or "Unknown" if missing)
            - `skills` (List of relevant skills)
            - `description` (Brief job description)

            Output ONLY valid JSON enclosed in triple backticks.
            Example:
            ```
            [{"role": "Software Engineer", "experience": "3 years", "skills": ["Python", "ML"], "description": "Exciting opportunity in AI"}]
            ```
            """
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt_extract.format(page_data=cleaned_text)}]
        )

        raw_content = response.choices[0].message.content.strip()
        print("🔍 Raw Response from LLM:", raw_content)  # ✅ Debugging step

        try:
            # Extract JSON from markdown formatting (if LLM returns triple backticks)
            match = re.search(r"```(?:json)?\n(.*)\n```", raw_content, re.DOTALL)
            json_text = match.group(1).strip() if match else raw_content.strip()

            res_json = json.loads(json_text)

            if not isinstance(res_json, list):
                res_json = [res_json]

            return res_json
        except json.JSONDecodeError as e:
            raise OutputParserException(
                f"❌ JSON parsing error: {str(e)}\n\n🔍 Raw Response:\n{raw_content[:500]}"
            )

    def write_mail(self, job, links):
        """Generate a cold email based on the job description and company links."""
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Adithya, a business development executive at AtliQ, an AI & Software Consulting company.
            Write a cold email explaining how AtliQ can fulfill their needs.

            Include relevant links: {link_list}

            Output only the email content.
            """
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt_email.format(job_description=str(job), link_list=links)}]
        )

        return response.choices[0].message.content if response.choices else "Error: No response from model."
