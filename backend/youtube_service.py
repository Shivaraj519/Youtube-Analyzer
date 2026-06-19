from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

def get_youtube_client(credentials):
    """
    Builds and returns an authorized YouTube client.
    """
    return build('youtube', 'v3', credentials=credentials)

def get_user_subscriptions(credentials, max_results=100):
    """
    Retrieves the user's subscribed channels (titles and descriptions).
    """
    try:
        youtube = get_youtube_client(credentials)
        subscriptions = []
        next_page_token = None
        
        while len(subscriptions) < max_results:
            request = youtube.subscriptions().list(
                part='snippet',
                mine=True,
                maxResults=min(50, max_results - len(subscriptions)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                subscriptions.append({
                    'id': snippet.get('resourceId', {}).get('channelId'),
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'type': 'subscription'
                })
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return subscriptions
    except Exception as e:
        logger.error(f"Error fetching YouTube subscriptions: {str(e)}")
        return []

def get_user_liked_videos(credentials, max_results=100):
    """
    Retrieves the user's liked videos (titles, descriptions, tags, and categoryIds).
    """
    try:
        youtube = get_youtube_client(credentials)
        liked_videos = []
        next_page_token = None
        
        while len(liked_videos) < max_results:
            # First, get liked video IDs using myRating='like'
            request = youtube.videos().list(
                part='snippet,topicDetails',
                myRating='like',
                maxResults=min(50, max_results - len(liked_videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            items = response.get('items', [])
            if not items:
                break
                
            for item in items:
                snippet = item.get('snippet', {})
                topic_details = item.get('topicDetails', {})
                
                # Fetch categories and topic tags if available
                categories = []
                if topic_details:
                    # Relevant topic categories
                    categories = topic_details.get('topicCategories', [])
                
                liked_videos.append({
                    'id': item.get('id'),
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'youtube_category_id': snippet.get('categoryId'),
                    'tags': snippet.get('tags', []),
                    'topic_categories': categories,
                    'type': 'like'
                })
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return liked_videos
    except Exception as e:
        logger.error(f"Error fetching YouTube liked videos: {str(e)}")
        return []
