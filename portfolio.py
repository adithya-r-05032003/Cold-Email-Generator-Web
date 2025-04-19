import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path="app/resource/portfolio.csv"):
        """Initialize the Portfolio class and load portfolio data from CSV."""
        self.file_path = file_path

        try:
            self.data = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error loading portfolio CSV: {e}")

        if not {"Techstack", "Links"}.issubset(self.data.columns):
            raise ValueError("CSV file must contain 'Techstack' and 'Links' columns.")

        self.chroma_client = chromadb.PersistentClient(path="vectorstore")
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        """Populate ChromaDB with portfolio data if not already added."""
        if self.collection.count() == 0:
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row["Techstack"]],
                    metadatas=[{"links": row["Links"]}],
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        """Query ChromaDB for relevant portfolio links based on skills."""
        try:
            if not skills:
                return []

            query_result = self.collection.query(query_texts=skills, n_results=2)

            if "metadatas" in query_result and query_result["metadatas"]:
                return [item["links"] for sublist in query_result["metadatas"] for item in sublist if "links" in item]

            return []

        except Exception as e:
            print(f"Error querying portfolio: {e}")
            return []
