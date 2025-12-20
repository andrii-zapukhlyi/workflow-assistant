# Multi-Agent Workflow Assistant

![Project Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

A comprehensive Multi-Agent Workflow Assistant designed to streamline enterprise tasks, information retrieval, and process automation. This project leverages Large Language Models (LLMs), Retrieval Augmented Generation (RAG), and a Multi-Agent architecture to unify company knowledge (Confluence documents) and operational workflows (Jira, Expert Discovery) into a single, satisfying chat experience.

## Live Demo
**[www.workflowassistant.app](https://www.workflowassistant.app)**

## Demo Video
[![Watch the video](video-thumbnail.jpg)](https://youtu.be/video-link)

## Tech Stack
- **Backend:** Python, LangChain, FastAPI, Huggingface (Embeddings), SQLAlchemy (ORM)
- **Database:** PostgreSQL
- **Vector DB:** Qdrant
- **Frontend:** Next.js, React, TypeScript
- **Deployment:** Docker Compose, Azure Container Registry, Azure Virtual Machine, Nginx
- **Authentication:** JWT, Refresh Tokens
- **Integrations:** Confluence API (Automated documentation fetching), Supabase API (Cloud Storage), Groq API (LLMs)
- **Package Manager:** Poetry

## The Challenge
In modern enterprises, **Knowledge is Fragmented**. Vital information is locked in static documentation (like Confluence), task trackers (Jira), or inside the heads of specific employees. Finding the right answer, or the right person to ask, often takes longer than the task itself.
*   **Dispersed Data:** Data exists in separate, non-integrated systems.
*   **Productivity Loss:** Employees spend up to 20% of their time just *searching* for info.
*   **Slow Onboarding:** New hires struggle to navigate complex internal systems without guidance.

## The Solution
The **Multi-Agent Workflow Assistant** serves as a "Central Nervous System" for enterprise data. It moves beyond simple Q&A by orchestrating specialized agents to solve complex problems:

1.  **Stop Searching, Start Asking:** Uses **RAG (Retrieval-Augmented Generation)** to fetch, synthesize, and cite real-time data from Confluence. No more digging through wikis.
2.  **Connect with Experts (Planned):** Instead of just reading a doc, the system will identify and connect you with the specific colleague who *wrote* it or knows the topic best.
3.  **Actionable Workflows (Planned):** Future agents will trigger real-world actions, such as creating Jira tickets or initiating HR processes, directly from the chat.

## Local Setup
Follow these steps to download and run the project locally.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/andrii-zapukhlyi/workflow-assistant.git
   cd workflow-assistant
   ```

2. **Configure Environment:**
   Navigate to the backend folder and create your `.env` file.
   ```bash
   cd backend

   # Linux/macOS:
   cp .env.example .env
   
   # Windows CMD:
   copy .env.example .env
   ```
   *Note: You will need to populate `.env` with your API keys (Confluence, Groq, Huggingface, etc.).*

3. **Run with Docker:**
   Return to the root directory and start the application.
   ```bash
   cd ..
   docker compose up --build
   ```
   *Note: Be sure to have Docker installed and running on your machine.*
   
   The application will be accessible at:
   `http://localhost`

## Future Plans
- **CI/CD Pipeline:** Implementation of a CI/CD pipeline with GitHub Actions to automate the deployment process.
- **Expert Finder Agent:** Implementation of an agent to help employees find experts within the company for specific tools or technologies.
- **Process Starter Agent:** Integration with Jira API to facilitate task management and process initiation through the chatbot.