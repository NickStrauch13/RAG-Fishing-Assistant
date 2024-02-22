[![CI](https://github.com/NickStrauch13/RAG-Fishing-Assistant/actions/workflows/python-ci.yml/badge.svg)](https://github.com/NickStrauch13/RAG-Fishing-Assistant/actions/workflows/python-ci.yml)

# Retreival Augmented Generation (RAG) Fishing Assistant
## (With Custom-Built Semantic Search)

Check out the site! ---> [AI Angler NC](https://ai-angler-nc.azurewebsites.net/) <---

Click here for a video breakdown of the project! ---> [YouTube Video](https://youtu.be/WReJGNw2hrg) <---

<div align="center">
    <img src="img/readme_pic.jpg" width="500" height="375">
</div>

## Project Overview
In this project, I developed a Retreival Augmented Generation (RAG) system to greatly improve an Large Language Model's performance in regards to giving fishing advice relating to the North Carolina Coast. This system is very open-ended and could easily be modified to accomplish other tasks such as call center support, document summarization, educational tutoring, or customer service inquiries across various industries.

This RAG system is built upon ChatGPT-3.5-tubro using data from [Fisherman's Post](https://www.fishermanspost.com/) (a popular fishing forum). I scraped every fishing report on the website and chunked the resulting data. The existing paragraph structure from the site was already well aligned with my desired chunking method; however, I also included the month, year, and location meta data in each chunk.

To embed the chunks, I selected the "text-embedding-3-small" embedding model from OpenAI. At the time I created this project, this was one of the top-performing embedding models given its relatively low dimensionality.

Instead of utilizing a vector database like Pinecone for storing and querying embedded vectors, I opted to perform semantic search manually using cosine similarity. This approach, while significantly slower, provided a valuable learning experience, allowing me to delve deeper into the mechanics of semantic search and understand the underlying algorithms. It served as an educational exercise, enhancing my understanding of vector space models and the practical implications of similarity measures in information retrieval.

## Model Performance

The RAG system’s performance metrics are compared to the base ChatGPT-3.5-turbo model below. These metric scores were calculated from the average performance on the questions below using human evaluation.

**Metrics**: (Score rated on a scale of 1-10)
- `Relevance`: How relevant is the response to the input prompt?
- `Accuracy`: How correct is all of the information provided in the response?
- `Informativeness`: How informative or useful is the response?
- `Specificity`: How detailed is the response? 

|                | Relevance | Accuracy | Informativeness | Specificity |
|----------------|-----------|----------|-----------------|-------------|
| ChatGPT-3.5-turbo | 9.133     | 8.800    | 6.067           | 5.933       |
| RAG System     | 9.800     | 9.467    | 7.400           | 7.867       |
| Δ              | 0.667     | 0.667    | 1.333           | 1.934       |


