import weaviate as wvc
import json

# ✅ Connect to Weaviate
client = wvc.connect_to_custom(
    http_host="localhost", http_port=8080, http_secure=False,
    grpc_host="localhost", grpc_port=50051, grpc_secure=False,
    skip_init_checks=True
)

# ✅ Function to save user memory with Debugging
async def save_user_memory(user_id, memory_data, debug_channel=None):
    """Saves a user's memory to Weaviate, avoiding duplicates."""
    try:
        # Convert memory data to JSON format
        memory_json = json.dumps(memory_data)

        # Check if the user already has saved memory
        existing_memory = await load_user_memory(user_id, debug_channel)
        if existing_memory == memory_data:
            debug_msg = f"⚠️ **No changes detected for user `{user_id}`, skipping save.**"
            print(debug_msg)
            if debug_channel:
                await debug_channel.send(debug_msg)
            return  # No need to overwrite identical data

        # Insert or update data into Weaviate
        client.collections.get("UserMemory").data.insert({
            "user_id": user_id,
            "memory_text": memory_json
        })

        debug_msg = f"✅ **Memory saved for user `{user_id}`.**"
        print(debug_msg)
        if debug_channel:
            await debug_channel.send(debug_msg)

    except Exception as e:
        error_msg = f"❌ ERROR: Failed to save memory for user `{user_id}`: {str(e)}"
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)

# ✅ Function to load user memory with Debugging
async def load_user_memory(user_id, debug_channel=None):
    """Retrieves a user's memory from Weaviate using correct API calls."""
    try:
        # Fetch data from Weaviate
        result = client.collections.get("UserMemory").query.fetch_objects(
            filters={"path": ["user_id"], "operator": "Equal", "valueText": user_id}
        )

        if result.objects:
            memory_data = json.loads(result.objects[0].properties["memory_text"])
            debug_msg = f"✅ **Memory loaded for user `{user_id}`.**"
            print(debug_msg)
            if debug_channel:
                await debug_channel.send(debug_msg)
            return memory_data

        debug_msg = f"⚠️ **No memory found for user `{user_id}`.**"
        print(debug_msg)
        if debug_channel:
            await debug_channel.send(debug_msg)
        return {}

    except Exception as e:
        error_msg = f"❌ ERROR: Failed to load memory for user `{user_id}`: {str(e)}"
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return {}

# ✅ Function to set up Weaviate Schema (Run Once)
async def setup_weaviate(debug_channel=None):
    """Creates the UserMemory collection in Weaviate."""
    try:
        if "UserMemory" not in client.collections.list_all():
            client.collections.create(
                name="UserMemory",
                properties=[
                    {"name": "user_id", "dataType": "string"},
                    {"name": "memory_text", "dataType": "string"}
                ]
            )
            debug_msg = "✅ **Created `UserMemory` collection in Weaviate.**"
            print(debug_msg)
            if debug_channel:
                await debug_channel.send(debug_msg)
        else:
            debug_msg = "✅ **`UserMemory` collection already exists.**"
            print(debug_msg)
            if debug_channel:
                await debug_channel.send(debug_msg)

    except Exception as e:
        error_msg = f"❌ ERROR: Failed to set up Weaviate schema: {str(e)}"
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
