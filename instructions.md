
# My ecommerce trend setting agent requirements

## Overview

Your goal is to create a multi-agent, multi-language solution that conducts relevant searches on the web and social media, analyzes eCommerce product trends, and creates engaging content such as blogs, images, and videos. These trends can be categorized in a few areas (but not only) such as functionality, aesthetic appeal, sustainability, technology integration, health and wellness, affordability, seasonality, exclusivity, cultural alignment, and innovation.The solution will leverage PhiData's out-of-the-box infrastructure (frontend/backend), agents, tools, and workflows. When needed, custom components and features will be developed to enhance the multi-agent's capabilities. The solution will first be developed for a local environment and later adapted for production-ready deployment.

## Functional Requirements

### 1. User Interactions
- **Query Submission**: Users interact via a chat interface to send queries.
- **Agent Responses**: Users receive agent responses, including detailed answers and final content displayed on a side canvas.
- **Admin Menu/Panel**: Users can modify fixed data variables:
  - Name, first name, e-commerce business name, URLs, target countries, competitors, and main URLs.
- **Chat History**: Users have access to their previous interactions.
- **Multi-Language Support**: Responses match the query language.

### 2. Agent Capabilities
#### [User Query Agent]
- **Goal**: Transform user input into structured, trend research-oriented queries.
- **Model**: GPT-4o
- **Instructions**:
  1. Set the current date and detect input language and set them as variables.
  2. Enforce guardrails such as:
    -  Goal: Align user queries with the platform's research focus.
    - Instructions:
      - Analyze Query:
        - Classify the query as research-related or not using the LLM.
        - Determine if it is vague, off-topic, or on-scope.
      - Enforce Research Scope:
        - For off-scope queries, reframe them into research-oriented alternatives:
          - Example:
            - Input: "How to assemble a sofa?"
            - Response: "This query is outside the research scope. Did you mean 'recent trends in sofa design'?"
      - Handle Non-Research Queries:
        - Inform users about scope limitations and suggest rephrasing.
        - Example:
          - Input: "Where can I buy a sofa?"
          - Response: "This platform focuses on market research. Please rephrase your query to explore sofa market trends or design predictions."
      - Address Vague Queries:
        - Prompt users for clarification:
        - Example:
          - Input: "Tech trends."
          - Response: "What specific technology or market are you interested in? For example, AI, IoT, or 5G. Any additional context?"
      - User Feedback Loop:
        - Allow users to refine their queries interactively based on LLM suggestions.
        - Example:
          - Input: "Furniture."
          - Interaction: "Would you like to explore furniture market trends, designs, or materials in the past year?"
      - Forward Validated Query:
        - Pass refined and validated queries to the next step for processing
  3. Parse user query output from step 2.
    - Goal: Parse queries into key components using Named Entity Recognition (NER) (focus, context, objective, scope).
    - Instructions:
      - Retrieve the current date and language.
      - Extract:
       - Focus: Identify products, industries, or topics.
       - Context: Extract geographic or temporal details.
       - Objective: Classify intent (e.g., trends, predictions).
       - Scope: Define key areas of the objective to identify
      - If key elements are missing, define the extraction parameters to the most general parameters like global for geography, trend for objective and the current year or recent for time.
      - Never return anything to the user or ask for any feedback.
  4. Restructure parsed query components from step 3 into trend research-focused templates.
    - Goal: Format parsed queries into trend research-focused templates.
    - Instructions:
      - Map extracted components into structured templates:
      - Template: `[Objective] + [Focus] + [Context] + [Scope]`
      - Example: 
        - Input: "Furniture trends in France."
        - Output: "What are the recent trends in the furniture market in France?"
    - Ensure specificity and clarity, and use the query's chosen language.
  5. Enrich step 4 outputs with synonyms, related terms and contextual details.
      - Goal: Enrich queries with synonyms, related terms and context details for enriching the search processes.
      - Instructions:
        - Add synonyms using the LLM model:
          - Example: "AI" → "Artificial Intelligence" OR "Machine Learning."
        - Include broader or related terms to cover adjacent topics:
          - Example: "Sofas" → "Sofas OR couches OR seating."
        - Rephrase the query as different types of questions
          - Example:
            - Original processed query: "what are the latest trends in sofa beds?"
            - Other questions:
              - What are the most popular sofa bed styles for small apartments?
              - How are designers improving sofa bed comfort in 2024?
              - Which materials are trending for sofa beds this season?
      -  Assess your outputs, amend and finalize
  6. Ensure processed and enriched queries are ready for search execution
    - Goal: Ensure queries are both ready for keyword and semantic search queries.
    - Instructions:
      - Create a set of keyword-based searches
      - Create a set of semantic-based searches
      - Construct search queries - data and metadata - for DuckDuckGo API (keyword-based) and Exa API formats (semantic-based)
  7. Store queries for further use.

#### [Dynamic Research Web Agent]
- **Goal**: Perform open searches based on User Query Agent outputs.
- **Tools**: Exa AI search tool (to be enhanced as PhiData's toolkit is limited).
- **Model**: GPT-4o mini
- **Instructions**:.
   1. Import the exa AI-compatible search queries stored from the outputs of the User Query Agent
   2. Run the semantic searches while excluding the ecommerce website URL and main competitors
   3. Collect and store the top 15 results while keeping URL sources in memory.

#### [Static Research Web Agent]
- **Goal**: Perform searches across pre-defined websites based on User Query Agent outputs.
- **Tools**: DuckDuckGo search tool (to be enhanced as PhiData's toolkit is limited).
- **Model**: GPT-4o mini
- **Instructions**:.
  1. Import the DuckDuckGo-compatible search terms and keywords stored from the outputs of the User Query Agent.
  2. Run the searches for defined websites for specific business domains below

{
  "categories": [
    {
      "category": "Fashion",
      "resources": [
        {
          "url": "https://www.vogue.com",
          "tags": ["Industry Website", "Media"]
        },
        {
          "url": "https://www.businessoffashion.com",
          "tags": ["Industry Website", "Market Research"]
        },
        {
          "url": "https://www.fashionunited.com",
          "tags": ["Industry Website", "News"]
        },
        {
          "url": "https://www.fashionista.com",
          "tags": ["Industry Blog", "Trends"]
        },
        {
          "url": "https://www.wgsn.com",
          "tags": ["Market Research", "Trends"]
        },
        {
          "url": "https://www.premierevision.com",
          "tags": ["Industry Event", "Exhibition"]
        },
        {
          "url": "https://www.parisfashionweek.fhcm.paris",
          "tags": ["Industry Event", "Fashion Show"]
        },
        {
          "url": "https://www.nike.com",
          "tags": ["Key Player", "Brand"]
        },
        {
          "url": "https://www.zara.com",
          "tags": ["Key Player", "Retailer"]
        },
        {
          "url": "https://www.hm.com",
          "tags": ["Key Player", "Retailer"]
        }
      ]
    },
    {
      "category": "Electronics",
      "resources": [
        {
          "url": "https://www.cnet.com",
          "tags": ["Industry Website", "Reviews"]
        },
        {
          "url": "https://www.techcrunch.com",
          "tags": ["Industry Website", "News"]
        },
        {
          "url": "https://www.theverge.com",
          "tags": ["Industry Blog", "Technology"]
        },
        {
          "url": "https://www.gartner.com/en/industries/high-tech",
          "tags": ["Market Research", "Analysis"]
        },
        {
          "url": "https://www.ces.tech",
          "tags": ["Industry Event", "Exhibition"]
        },
        {
          "url": "https://www.ifixit.com",
          "tags": ["Industry Blog", "DIY"]
        },
        {
          "url": "https://www.apple.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.samsung.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.sony.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.xiaomi.com",
          "tags": ["Key Player", "Manufacturer"]
        }
      ]
    },
    {
      "category": "Home Goods",
      "resources": [
        {
          "url": "https://www.houzz.com",
          "tags": ["Industry Website", "Design"]
        },
        {
          "url": "https://www.architecturaldigest.com",
          "tags": ["Industry Website", "Media"]
        },
        {
          "url": "https://www.apartmenttherapy.com",
          "tags": ["Industry Blog", "Lifestyle"]
        },
        {
          "url": "https://www.ikea.com",
          "tags": ["Key Player", "Retailer"]
        },
        {
          "url": "https://www.wayfair.com",
          "tags": ["Key Player", "Retailer"]
        },
        {
          "url": "https://www.homedepot.com",
          "tags": ["Key Player", "Retailer"]
        },
        {
          "url": "https://www.leroymerlin.fr",
          "tags": ["Key Player", "Retailer (France)"]
        },
        {
          "url": "https://www.conforama.fr",
          "tags": ["Key Player", "Retailer (France)"]
        },
        {
          "url": "https://www.maison-objet.com",
          "tags": ["Industry Event", "Exhibition (France)"]
        },
        {
          "url": "https://www.npd.com/industries/home/",
          "tags": ["Market Research", "Analysis"]
        }
      ]
    },
    {
      "category": "Health & Beauty",
      "resources": [
        {
          "url": "https://www.allure.com",
          "tags": ["Industry Website", "Media"]
        },
        {
          "url": "https://www.beautyindependent.com",
          "tags": ["Industry Blog", "Trends"]
        },
        {
          "url": "https://www.cosmeticsdesign.com",
          "tags": ["Industry Website", "News"]
        },
        {
          "url": "https://www.loreal.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.esteelauder.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.sephora.com",
          "tags": ["Key Player", "Retailer"]
        },
        {
          "url": "https://www.npd.com/industries/beauty/",
          "tags": ["Market Research", "Analysis"]
        },
        {
          "url": "https://www.in-cosmetics.com",
          "tags": ["Industry Event", "Exhibition"]
        },
        {
          "url": "https://www.cosmoprof.com",
          "tags": ["Industry Event", "Exhibition"]
        },
        {
          "url": "https://www.glossy.co",
          "tags": ["Industry Blog", "Media"]
        }
      ]
    },
    {
      "category": "Food & Beverage",
      "resources": [
        {
          "url": "https://www.foodnavigator.com",
          "tags": ["Industry Website", "News"]
        },
        {
          "url": "https://www.beveragedaily.com",
          "tags": ["Industry Website", "News"]
        },
        {
          "url": "https://www.foodbusinessnews.net",
          "tags": ["Industry Website", "News"]
        },
        {
          "url": "https://www.nestle.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.coca-cola.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.pepsico.com",
          "tags": ["Key Player", "Manufacturer"]
        },
        {
          "url": "https://www.mintel.com/food-and-drink",
          "tags": ["Market Research", "Analysis"]
        },
        {
          "url": "https://www.sialparis.com",
          "tags": ["Industry Event", "Exhibition (France)"]
        },
        {
          "url": "https://www.anuga.com",
          "tags": ["Industry Event", "Exhibition"]
        },
        {
          "url": "https://www.foodandwine.com",
          "tags": ["Industry Blog", "Media"]
        }
      ]
    }
  ]
}
  3. Collect and store the top ten search results in a structured json format.

#### [Pre-Ranking Agent]
- **Goal**: Retrieve all results from web searches and rank them
- **Tools**: None.
- **Model**: GPT-4
- **Instructions**
   1. Remove URL duplicates within the combined search results.
   2. Prioritize freshness
   3. Score results based on the following heuristic:
      - For keyword-based search results, boost exact keywords in the snippets
      - For semantic search results, boost highlight scores 
   4. Select the top 7 URL results

#### [Scraping Agent]
- **Goal**: Scrape text and images from the URL results
- **Tools**: Firecrawl tool
- **Model**: GPT-4
- **Instructions**
   1. Remove URL duplicates within the combined search results.
   2. Prioritize freshness

#### Other Agents
- **Blog Writer Agent**: Generate blog content.
- **Image Creation Agent**: Create visuals.
- **Video Creation Agent**: Develop video content.

### 3. Tool Capabilities
#### DuckDuckGo search tool
- **Goal**: Performs DuckDuckGo searches and returns and store results
- **Instructions**:
   - Retrieve searches and terms from the memory or storage
   - Run the searches
   - Returns the results that should include at least title, URL, description/snippet, date of publication, and keywords.
   - Store the results in a structured json format

#### Exa search tool
- **Goal**: Performs Exa searches and returns and store results
- **Instructions**:
   - Retrieve searches and terms from the memory or storage
   - Run the searches
   - Returns the results. Basic output format should include at least: Score, Title, Date of Publication, Id, URL, Highlight, Highlight score
   - Store the results in a structured json format

### 4. Knowledge & Memory
- **Information Storage**: Define what agents should retain.
- **Knowledge Bases**: Specify resources for agents.

### 5. Custom Features
- A workflow should be implemented with monitoring capabilities, as follows:
   - The user enters his query
   - The user query agent answers or validates the query
   - The static and dynamic search agents run in parallel
   - The pre-ranking agent ranks the URL results for the parsing agent
   - The parsing agent parses the final URL results
   - The blog writer writes a blog to answer the validated user query, while keeping sources
   - The user can edit the blog in a canva 
- Any workflow issue should be explicity flagged to the user

## Technical Requirements

### 1. Models
- **Preferred Models**: GPT-4o, GPT-4o mini or local models.
- **Parameters**: to be defined

### 2. Infrastructure
- **Database**: Choose the simplest option from out-of-the box database provided by phidata
- **Storage**: Choose the simplest option from out-of-the box storage provided by phidata
- **APIs**: Integrate necessary data sources.


## Important Notes
- Always follow the phidata documentation here: [text](https://docs.phidata.com/agents)
- Always start from the existing repository code and in particular, the github-perso-phidata\cookbook where there many real life examples for agents, tools and workflows and related READ.me file documentation
- Set the monitoring to TRUE for the whole project
- Let me know when you are not sure about something