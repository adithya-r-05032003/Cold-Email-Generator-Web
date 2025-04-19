from flask import Flask, render_template, request
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
from langchain_community.document_loaders import WebBaseLoader

app = Flask(__name__)
chain = Chain()
portfolio = Portfolio()

@app.route("/", methods=["GET", "POST"])
def home():
    email_results = []
    error_message = None

    if request.method == "POST":
        try:
            job_url = request.form.get("job_url", "").strip()
            if not job_url:
                error_message = "Please enter a valid job posting URL."
            else:
                loader = WebBaseLoader(job_url)
                page_data = loader.load()

                if not page_data:
                    error_message = "No content found at the provided URL."
                else:
                    data = clean_text(page_data[0].page_content)
                    portfolio.load_portfolio()
                    jobs = chain.extract_jobs(data)

                    if not jobs:
                        error_message = "No job postings found in the webpage."
                    else:
                        for job in jobs:
                            skills = job.get("skills", [])
                            links = portfolio.query_links(skills)
                            email = chain.write_mail(job, links)
                            email_results.append({
                                "role": job.get("role", "Unknown Role"),
                                "email": email
                            })
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"

    return render_template("index.html", results=email_results, error=error_message)

if __name__ == "__main__":
    app.run(debug=True)
