import json
import os
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from .models import Show, Episode

def slugify(text):
    """Convert text into a slug format"""
    return text.lower().replace(" ", "_")

def generate_firetv_feed():
    """Generate a JSON feed for Amazon Fire TV"""
    shows = Show.objects.prefetch_related('episodes').all()

    feed = {
        "providerName": "TaterTot Kids Club",
        "lastUpdated": datetime.utcnow().isoformat() + "+00:00",
        "language": "en-US",
        "tvSpecials": [],
        "categories": []
    }

    category_names = set()

    for show in shows:
        for episode in show.episodes.all():
            episode_data = {
                "id": str(episode.id),
                "title": episode.title,
                "content": {
                    "dateAdded": datetime.utcnow().isoformat() + "+00:00",
                    "videos": [{
                        "url": episode.m3u8_url.strip(),
                        "quality": "HD",
                        "videoType": "HLS"
                    }],
                    "duration": int(float(episode.duration)) if episode.duration else 1,
                    "language": "en-US"
                },
                "genres": ["faith"],
                "tags": [episode.title],  # Episode title as a tag
                "thumbnail": episode.thumbnail_url,
                "releaseDate": datetime.utcnow().strftime("%Y-%m-%d"),
                "shortDescription": episode.title,
                "longDescription": episode.title
            }

            feed["tvSpecials"].append(episode_data)
            category_names.add(episode.title)  # Use episode titles for categories

    # Generate categories dynamically
    feed["categories"] = [
        {"name": name, "query": name, "order": "most_recent"}
        for name in sorted(category_names)  # Ensure order consistency
    ]

    return feed

def publish_firetv_feed():
    """Generate and save Fire TV JSON feed locally"""
    feed = generate_firetv_feed()
    feed_path = os.path.join(settings.BASE_DIR, "firetv-feed.json")

    try:
        with open(feed_path, 'w', encoding='utf-8') as f:
            json.dump(feed, f, indent=2)
        print(f"✅ Fire TV feed successfully saved to {feed_path}")
    except IOError as e:
        print(f"❌ Error saving Fire TV feed: {e}")

    return feed_path

class FireTVFeedAPI(View):
    """API Endpoint: Returns the Fire TV JSON feed from a saved file"""

    def get(self, request, *args, **kwargs):
        feed_path = os.path.join(settings.BASE_DIR, "firetv-feed.json")
        
        if not os.path.exists(feed_path):
            return JsonResponse({"error": "Feed not available. Please publish first."}, status=404)

        try:
            with open(feed_path, 'r', encoding='utf-8') as f:
                feed_data = json.load(f)
            return JsonResponse(feed_data, safe=False, json_dumps_params={'indent': 2})
        except IOError:
            return JsonResponse({"error": "Unable to read feed file."}, status=500)
