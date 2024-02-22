[![CI](https://github.com/NickStrauch13/RAG-Fishing-Assistant/actions/workflows/python-ci.yml/badge.svg)](https://github.com/NickStrauch13/RAG-Fishing-Assistant/actions/workflows/python-ci.yml)

# Retreival Augmented Generation (RAG) Fishing Assistant
## (With Custom-Built Semantic Search)

Check out the site!  ---> (AI Angler NC)[https://ai-angler-nc.azurewebsites.net/] <---

<div align="center">
    <img src="img/readme_pic.jpg" width="500" height="375">
</div>

## Project Overview
In this project, I developed a Retreival Augmented Generation (RAG) system to greatly improve an Large Language Model's performance in regards to giving fishing advice relating to the North Carolina Coast. This system is very open-ended and could easily be modified to accomplish other tasks such as call center support, document summarization, educational tutoring, or customer service inquiries across various industries.

This RAG system is built upon ChatGPT-3.5-tubro using data from (Fisherman's Post)[https://www.fishermanspost.com/] (a popular fishing forum). I scraped every fishing report on the website and chunked the resulting data. The existing paragraph structure from the site was already well aligned with my desired chunking method; however, I also included the month, year, and location meta data in each chunk.

To embed the chunks, I selected the "text-embedding-3-small" embedding model from OpenAI. At the time I created this project, this was one of the top-performing embedding models given its relatively low dimensionality.

Instead of utilizing a vector database like Pinecone for storing and querying embedded vectors, I opted to perform semantic search manually using cosine similarity. This approach, while significantly slower, provided a valuable learning experience, allowing me to delve deeper into the mechanics of semantic search and understand the underlying algorithms. It served as an educational exercise, enhancing my understanding of vector space models and the practical implications of similarity measures in information retrieval.
