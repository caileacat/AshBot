import discord
import asyncio

async def handle_admin_action(interaction, action_type, target_user, role_name, debug_channel):
    """Handles role assignments and administrative actions based on Ash's decisions."""
    guild = interaction.guild

    # Fetch debug channel and log the admin action
    if debug_channel:
        await debug_channel.send(f"🔍 **DEBUG:** Processing `{action_type}` for `{target_user.display_name}` with role `{role_name}`.")

    # **Find the role by searching through all roles**
    role = discord.utils.get(guild.roles, name=role_name)

    # If role not found, try case-insensitive match
    if not role:
        role = next((r for r in guild.roles if r.name.lower() == role_name.lower()), None)

    # **Log error if role is missing**
    if not role:
        error_msg = f"❌ ERROR: Role `{role_name}` not found in the server."
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg

    # **Ensure bot has permission to manage roles**
    if not guild.me.guild_permissions.manage_roles:
        error_msg = "❌ ERROR: Bot lacks `Manage Roles` permission."
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg

    # **Check if the bot's highest role is above the target role**
    bot_highest_role = max(guild.me.roles, key=lambda r: r.position)
    if role.position >= bot_highest_role.position:
        error_msg = f"❌ ERROR: Cannot assign `{role.name}` because it is equal to or higher than the bot's highest role."
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg

    # **Execute the action**
    if action_type == "add_role":
        return await execute_add_role(interaction, target_user, role, debug_channel)
    elif action_type == "remove_role":
        return await execute_remove_role(interaction, target_user, role, debug_channel)
    else:
        error_msg = f"❌ ERROR: Unknown action `{action_type}`."
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg

async def execute_add_role(interaction, target_user, role, debug_channel):
    """Adds a role to a user."""
    try:
        await target_user.add_roles(role)
        await asyncio.sleep(1)  # Ensure role change takes effect

        if role in target_user.roles:
            success_msg = f"✅ SUCCESS: `{role.name}` added to `{target_user.display_name}`."
            role_confirmation = f"✨ Poof! {target_user.display_name}, you are now part of `{role.name}`. Don't let the magic fade too soon! 😉"
        else:
            success_msg = f"❌ ERROR: `{role.name}` was NOT added to `{target_user.display_name}`."
            role_confirmation = f"❌ Uh-oh! It seems like something went wrong while adding `{role.name}`. Maybe try again?"

        print(success_msg)
        if debug_channel:
            await debug_channel.send(success_msg)

        return role_confirmation

    except Exception as e:
        error_msg = f"❌ ERROR: Failed to add `{role.name}` to `{target_user.display_name}`: {str(e)}"
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg

async def execute_remove_role(interaction, target_user, role, debug_channel):
    """Removes a role from a user."""
    try:
        await target_user.remove_roles(role)
        await asyncio.sleep(1)  # Ensure role change takes effect

        if role not in target_user.roles:
            success_msg = f"✅ SUCCESS: `{role.name}` removed from `{target_user.display_name}`."
            role_confirmation = f"🌙 And just like that, `{role.name}` has vanished from `{target_user.display_name}`. Hope you don’t miss it too much!"
        else:
            success_msg = f"❌ ERROR: `{role.name}` was NOT removed from `{target_user.display_name}`."
        
        print(success_msg)
        if debug_channel:
            await debug_channel.send(success_msg)

        return role_confirmation if role_confirmation else success_msg

    except Exception as e:
        error_msg = f"❌ ERROR: Failed to remove `{role.name}` from `{target_user.display_name}`: {str(e)}"
        print(error_msg)
        if debug_channel:
            await debug_channel.send(error_msg)
        return error_msg
