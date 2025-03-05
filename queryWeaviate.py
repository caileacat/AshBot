import requests

# Set Weaviate API endpoint
url = "http://localhost:8080/v1/graphql"

# Define GraphQL query
query = {
    "query": "{ Get { UserMemory { user_id memory_text } } }"
}

# Send request
response = requests.post(url, json=query)

# Print results
if response.status_code == 200:
    print("✅ Weaviate Response:\n", response.json())
else:
    print(f"❌ ERROR: {response.status_code} - {response.text}")
