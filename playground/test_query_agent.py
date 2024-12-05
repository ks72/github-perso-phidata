import logging
import sys
from ecommerce_agents.agents.query_agent import UserQueryAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('query_agent.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize the agent with debug logging
        agent = UserQueryAgent(monitoring=True)
        logger.info("Agent initialized successfully")

        # Test query
        query = "What are the innovative trends in Nike athletic footwear globally for 2024?"
        logger.info(f"Processing query: {query}")
        
        result = agent.process_query(query)
        
        # Log the result structure
        logger.info("Query processed successfully")
        logger.debug(f"Result structure: {result}")
        
        # Print components in a readable format
        if "components" in result:
            components = result["components"]
            print("\nExtracted Components:")
            print(f"Focus: {components.focus.brand} - {components.focus.product}")
            print(f"Objective: {components.objective}")
            print(f"Context: {components.context.location} ({components.context.time})")
            print(f"Scope: {components.scope}")
            
            print("\nSearch Queries:")
            for query_type, queries in result["search_queries"].items():
                print(f"\n{query_type.title()}:")
                for q in queries:
                    print(f"- {q}")
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
