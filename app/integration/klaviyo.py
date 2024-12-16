from klaviyo_api import KlaviyoAPI



klaviyo = KlaviyoAPI()

klaviyo.Profiles.get_profiles(filter="email")