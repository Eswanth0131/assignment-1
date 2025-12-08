version: '3.9'

services:
  erica-app:
    container_name: erica_app
    image: python:3.10
    working_dir: /app
    volumes:
      - ./:/app
    command: tail -f /dev/null
    tty: true

Erica AI Tutor

This project implements the Erica AI Tutor system.  
It builds a knowledge graph from extracted entities, constructs concept relationships, retrieves subgraphs for user questions, and generates final answers using a local LLM. Everything runs inside a lightweight Docker container.


#1 Setup Instructions

Install Requirements

You need:
Docker Desktop  
Ollama installed locally: https://ollama.com/download  
Qwen model pulled:

```bash
ollama pull qwen2.5:1.5b

# Make sure Ollama is running:

ollama serve

# Start Docker Environment

docker compose up -d
docker compose exec erica-app /bin/bash

# You should now be inside the container:

root@erica_app:/app#

⸻

#2. Running the System

Inside the container run:
python src/query.py

You will see:

Enter a question (or 'exit'):

Ask any question, for example:

What is attention in transformers and can you provide a python example of how it is used?

The system will:
	1.	Extract concepts from the question
	2.	Match nodes in the KG
	3.	Build a subgraph
	4.	Gather resource nodes
	5.	Create a context prompt
	6.	Query Ollama for the final answer
	7.	Save the subgraph + resources to data/m4_subgraphs.jsonl
	8.	Print only the final answer in the terminal

To exit:

exit

⸻

3. Milestones

M1 — Environment and Tooling Milestone
The environment is set up, please refer to the docker compose file.


M2 — Ingestion Milestone
Ingested the website lecture slides, pdfs linked in the website, and tried to extract youtube
videos as well. Please refer to m2.ipynb for the all of the URLs that have been ingested.


M3 — GraphRAG Construction Milestone
Please refer to m3.ipynb for presenting elements of the KG that highlight a concept and its relationships to other concepts, resources, and examples.

M4 — Query and Generation Milestone
When the user asks a question, the graph is search for all relevant nodes and neigbhors, etc. This information and the question is given to Qwen, which provides an answer. For the subgraphs and all other information about the 3 questions please refer to m4_subgraphs.jsonl. For the screenshots of the queries, please refer to the images q1, q2, and q3.
