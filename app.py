from flask import Flask, render_template, request
from app.chains import Chain
from app.portfolio import Portfolio
from app.utils import clean_text
from langchain_community.document_loaders import WebBaseLoader

app = Flask(__name__)

chain = Chain()
portfolio = Portfolio()

@app.route("/", methods=["GET", "POST"])
def index():
    email_results = []
    error = None

    if request.method == "POST":
        url = request.form.get("job_url")
        try:
            loader = WebBaseLoader(url)
            page_data = loader.load()

            if not page_data:
                error = "No data found at the provided URL."
            else:
                text = clean_text(page_data[0].page_content)
                portfolio.load_portfolio()
                jobs = chain.extract_jobs(text)

                if not jobs:
                    error = "No job postings found."
                else:
                    for job in jobs:
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        email = chain.write_mail(job, links)
                        email_results.append({
                            "role": job.get("role", "Unknown"),
                            "email": email
                        })

        except Exception as e:
            error = str(e)

    return render_template("index.html", email_results=email_results, error=error)

if __name__ == "__main__":
    app.run(debug=True)
