import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class NautobotClient:
    def __init__(self):
        self.base_url = os.getenv("NAUTOBOT_URL", "http://127.0.0.1:8080")
        self.token = os.getenv(
            "NAUTOBOT_TOKEN", "0123456789abcdef0123456789abcdef01234567"
        )

        if not self.base_url or not self.token:
            error_msg = "NAUTOBOT_URL and NAUTOBOT_TOKEN must be set"
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

        logger.info(f"Initialized NautobotClient with URL: {self.base_url}")

    def graphql_query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Execute a GraphQL query against Nautobot"""
        try:
            payload = {"query": query, "variables": variables or {}}

            logger.debug(f"Executing GraphQL query: {query[:100]}...")
            response = requests.post(
                f"{self.base_url}/api/graphql/",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()

            if result.get("errors"):
                error_msg = f"GraphQL errors: {result['errors']}"
                logger.error(error_msg)

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"GraphQL query failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def rest_get(self, endpoint: str) -> Dict:
        """Execute a REST GET request against Nautobot"""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.debug(f"Executing REST GET: {url}")

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            error_msg = f"REST request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def rest_post(self, endpoint: str, data: Dict[str, Any]) -> Dict:
        """Execute a REST POST request against Nautobot"""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.debug(f"Executing REST POST: {url}")

            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            error_msg = f"REST POST request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def test_connection(self) -> bool:
        """Test the connection to Nautobot"""
        try:
            # Simple query to test connection
            test_query = """
            query {
                __schema {
                    types {
                        name
                    }
                }
            }
            """
            result = self.graphql_query(test_query)
            if result.get("data"):
                logger.info("Successfully connected to Nautobot")
                return True
            else:
                logger.error("Failed to connect to Nautobot")
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
