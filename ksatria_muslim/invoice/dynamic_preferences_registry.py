from dynamic_preferences.types import StringPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.users.registries import user_preferences_registry

api_keys_section = Section("api_keys", "API Keys")


@user_preferences_registry.register
class Clockify(StringPreference):
    section = api_keys_section
    name = "clockify_api_key"
    default = ""
    description = "Open https://app.clockify.me/user/settings to get your API key"
