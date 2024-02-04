# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import streamlit as st
from streamlit.logger import get_logger
from googleapiclient.discovery import build
from datetime import datetime

LOGGER = get_logger(__name__)
# Initialize connection.
# Uses st.cache_resource to only run once.

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = 'AIzaSyDaQNEEq_bwQOoZehAWoFzWLnp4lNuw0Pc'
youtube = build('youtube', 'v3', developerKey=API_KEY)

@st.cache_resource
def init_connection():
    uri = "mongodb+srv://jeyakartheesan7:0KvxnDJSDzn6pDkn@cluster0.335x0gh.mongodb.net/?retryWrites=true&w=majority"
    return MongoClient(uri, server_api=ServerApi('1'))


def test_jk():
    st.warning("jk")

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    
    @st.cache_data(ttl=600)
    def get_data():
        client = init_connection()
        db = client.youtube
        items = db.video.find()
        items = list(items)  # make hashable for st.cache_data
        return items
    items = get_data()
    # Print results.
    # for item in items:
    #    st.write(f"{item}")
    # Create an input field
    user_input = st.text_input("Enter Channel Id", "")

    # Create a button
    if st.button("Channel"):
        # Check if the button is clicked and call the function
        output_result = process_input(user_input)
        insert_channel_info(user_input)


    if st.button("Playlist"):
        # Check if the button is clicked and call the function
        output_result = process_input(user_input)
        insert_channel_playlists(user_input)

    if st.button("Video"):
        # Check if the button is clicked and call the function
        output_result = process_input(user_input)
        for playlist_id in get_playlist_ids(user_input):
            insert_playlist_videos(playlist_id)
    if st.button("Comment"):
        # Check if the button is clicked and call the function
        output_result = process_input(user_input)
        #get_video_comments("aANP9zUCXlI")
        for playlist_id in get_playlist_ids(user_input):
            for video_id in get_video_ids(playlist_id):
                insert_video_comments(video_id=video_id, playlist_id=playlist_id, channel_id=user_input)
    if st.button("Question1"):
        #question_num_1()
        question_1()
    if st.button("Question2"):
        question_2()
    if st.button("Question3"):
        question_3()
    if st.button("Question4"):
        question_4()
    if st.button("Question5"):
        question_5()
    if st.button("Question6"):
        question_6()
    if st.button("Question7"):
        question_7()
    if st.button("Question8"):
        question_8()
    if st.button("Question9"):
        question_9()
    if st.button("Question10"):
        question_10()

def process_input(input_text):
    # Add your logic or function call here
    result = f"Processed input: {input_text.upper()}"
    
    return result





def insert_channel_info(channel_id):
    # Step 1: Get channel details
    channel_request = youtube.channels().list(
        part='id,snippet,contentDetails,statistics,status',
        id=channel_id
    )

    channel_response = channel_request.execute()
    #print(channel_response)

    # Check if the channel exists
    if 'items' in channel_response:
        channel_info = channel_response['items'][0]

        # Extract channel details
        channel_id = channel_info['id']
        channel_name = channel_info['snippet']['title']
        channel_type = 'User' if channel_id.startswith('UC') else 'Brand'
        channel_views = channel_info['statistics']['viewCount']
        channel_description = channel_info['snippet']['description']
        channel_status = channel_info['status']['privacyStatus']

        #print(channel details)
        print(f"Channel ID: {channel_id}")
        print(f"Channel Name: {channel_name}")
        print(f"Channel Type: {channel_type}")
        print(f"Channel Views: {channel_views}")
        print(f"Channel Description: {channel_description}")
        print(f"Channel Status: {channel_status}")
        client = init_connection()
        db = client.youtube
        db.channel.insert_one({
        "_id": channel_id,
        "channel_id": channel_id,
        "channel_name": channel_name,
        "channel_type": channel_type,
        "channel_views": channel_views,
        "channel_description": channel_description,
        "channel_status": channel_status
        })
    else:
        print("Channel not found.")


def insert_channel_playlists(channel_id):
    # Step 1: Get all playlist IDs from the channel
    playlists_request = youtube.playlists().list(
        part='id,snippet',
        channelId=channel_id,
        maxResults=50  # You can adjust this based on the number of playlists
    )
    playlists_response = playlists_request.execute()

    # Check if the channel has playlists
    if 'items' in playlists_response:
        # Extract playlist details
        playlists = playlists_response['items']
        client = init_connection()
        db = client.youtube
        # Print playlist IDs and names
        print("Playlist IDs and Names:")
        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_name = playlist['snippet']['title']
            print(f"Playlist ID: {playlist_id}, Playlist Name: {playlist_name}")
            db.playlist.insert_one({
                "_id": playlist_id,
                "playlist_id": playlist_id,
                "playlist_name": playlist_name,
                "channel_id": channel_id,
            })

    else:
        print("No playlists found for the channel.")



def insert_playlist_videos(playlist_id):
    # Step 1: Get all video IDs from the playlist
    playlist_items_request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50  # You can adjust this based on the number of videos
    )
    playlist_items_response = playlist_items_request.execute()

    # Check if the playlist has videos
    if 'items' in playlist_items_response:
        video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]

        # Step 2: Get video details for each video ID
        videos_request = youtube.videos().list(
            part='id,snippet,contentDetails,statistics,status',
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()

        # Print video details
        #print("Video Details:",videos_response )
        for video in videos_response['items']:
            video_id = video['id']
            video_name = video['snippet']['title']
            video_description = video['snippet']['description']
            publish_date = video['snippet']['publishedAt']
            #print(video['statistics'])
            view_count = video['statistics']['viewCount']
            like_count = video['statistics'].get('likeCount', 0)
            dislike_count = video['statistics'].get('dislikeCount', 0)
            favorite_count = video['statistics'].get('favoriteCount', 0)
            comment_count = video['statistics'].get('commentCount', 0)
            duration = video['contentDetails']['duration']
            thumbnail_url = video['snippet']['thumbnails']['default']['url']
            caption_status = video['status'].get('uploadStatus', 'Not available')

            # Print video information
            print(f"Video ID: {video_id}")
            print(f"Video Name: {video_name}")
            print(f"Video Description: {video_description}")
            print(f"Published Date: {publish_date}")
            print(f"View Count: {view_count}")
            print(f"Like Count: {like_count}")
            print(f"Dislike Count: {dislike_count}")
            print(f"Favorite Count: {favorite_count}")
            print(f"Comment Count: {comment_count}")
            print(f"Duration: {duration}")
            print(f"Thumbnail URL: {thumbnail_url}")
            print(f"Caption Status: {caption_status}")
            print("\n")
            client = init_connection()
            db = client.youtube
            db.video.insert_one({
                "_id": playlist_id+"_"+video_id,
                "video_id": video_id,
                "video_name": video_name,
                "playlist_id": playlist_id,
                "video_description": video_description,
                "publish_date": datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%SZ"),
                "view_count" : view_count,
                "like_count":like_count,
                "dislike_count":dislike_count,
                "favorite_count":favorite_count,
                "comment_count":comment_count,
                "duration":duration,
                "thumbnail_url": thumbnail_url,
                "caption_status": caption_status
            })

    else:
        print("No videos found in the playlist.")

def get_playlist_ids(channel_id):
    client = init_connection()
    db = client.youtube
    playlist_ids = [playlist["playlist_id"] for playlist in list(db.playlist.find({"channel_id":channel_id}))]
    print(channel_id)
    print(playlist_ids)
    return playlist_ids
def get_video_ids(playlist_id):
    client = init_connection()
    db = client.youtube
    video_ids = [video["video_id"] for video in list(db.video.find({"playlist_id":playlist_id}))]
    print(video_ids)
    return video_ids

def insert_video_comments(video_id, playlist_id, channel_id):
    # Step 1: Get all comment threads for the video
    comments_request = youtube.commentThreads().list(
        part='id,snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=50  # You can adjust this based on the number of comments
    )
    comments_response = comments_request.execute()

    # Check if there are comments
    if 'items' in comments_response:
        comments = comments_response['items']

        # Print comment details
        client = init_connection()
        db = client.youtube
        print("Comment Details:")
        for comment in comments:
            comment_id = comment['id']
            comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comment_publish_date = comment['snippet']['topLevelComment']['snippet']['publishedAt']

            # Print comment information
            print(f"Comment ID: {comment_id}")
            print(f"Comment Text: {comment_text}")
            print(f"Comment Author: {comment_author}")
            print(f"Comment Publish Date: {comment_publish_date}")
            print("\n")
            db.comment.insert_one({
                "_id": channel_id + "_" + playlist_id +"_" + video_id + "_" + comment_id,
                "comment_id": comment_id,
                "video_id": video_id,
                "comment_text": comment_text,
                "comment_author": comment_author,
                "comment_publish_date": comment_publish_date,
            })

    else:
        print("No comments found for the video.")
    
    min_conv()



def question_num_1():
    client = init_connection()
    db = client.youtube
    result_1 = db.video.aggregate([
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$project': {
                'video_name': 3,
                'channel_name': '$channel_info.channel_name'
            }
        }
    ])
    print("Question 1:")
    st.write("Question 1:")
    
    # for doc in result_1:
    #     print(doc)
    result_table_1 = [{"playlist_id":doc["_id"].split("_")[0],"Video Name": doc['video_name']} for doc in result_1]
    print(result_table_1)
    st.table(result_table_1)

def question_2():
    client = init_connection()
    db = client.youtube
    result_2 = db.video.aggregate([
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$unwind': '$playlist_info'
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$group': {
                '_id': '$channel_info.channel_id',
                'channel_name': {'$first': '$channel_info.channel_name'},
                'video_count': {'$sum': 1}
            }
        },
        {
            '$sort': {'video_count': -1}
        },
        {
            '$limit': 1
        }
    ])
    st.write("\nQuestion 2:")
    result_table_2 = [{
        "Channel Name": doc['channel_name'][0],
        "Video Count": doc['video_count']
    } for doc in result_2]

    st.table(result_table_2)

def question_3():
    client = init_connection()
    db = client.youtube
    result_3 = db.video.aggregate([
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$unwind': '$playlist_info'
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$sort': {'view_count': -1}
        },
        {
            '$limit': 10
        },
        {
            '$project': {
                'video_name': 1,
                'channel_name': '$channel_info.channel_name',
                'view_count': 1
            }
        }
    ])


    st.write("\nQuestion 3:")
    result_list_sorted = sorted(result_3, key=lambda x: int(x['view_count']), reverse=True)
    print(f"result_list_sorted::{result_list_sorted}")
    result_table_3 = [{
         "Channel Name": doc['channel_name'][0],
        "Video Name": doc['video_name'],
        "View Count": int(doc['view_count'])
    } for doc in result_list_sorted]

    st.table(result_table_3)
def question_1():
    client = init_connection()
    db = client.youtube
    result = db.video.aggregate([
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$unwind': '$playlist_info'
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$unwind': '$channel_info'
        },
        {
            '$project': {
                'video_name': '$video_name',
                'channel_name': '$channel_info.channel_name',
                'playlist_name': '$playlist_info.playlist_name'
            }
        }
    ])

    # Print the result
    result = [{"Channel Name":doc["channel_name"],"Playlist Name":doc["playlist_name"],"Video Name": doc['video_name']} for doc in result]
    #print(result)
    st.table(result)
def question_4():
    client = init_connection()
    db = client.youtube
    result_4 = db.comment.aggregate([
        {
            '$group': {
                '_id': '$video_id',
                'comment_count': {'$sum': 1}
            }
        },
        {
            '$lookup': {
                'from': 'video',
                'localField': '_id',
                'foreignField': 'video_id',  # Corrected field to match with video collection
                'as': 'video_info'
            }
        },
        {
            '$project': {
                'video_name': '$video_info.video_name',
                'comment_count': 1
            }
        }
    ])

    st.write("\nQuestion 4:")
    
    # Print the results
    # for result in result_4:
    #     print(result)
    result_table_4 = [{
        "Video Name": result.get('video_name', 'N/A')[0],
        "Comment Count": result['comment_count']
    } for result in result_4]

    st.table(result_table_4)

# Example: Question 5
def question_5():
    client = init_connection()
    db = client.youtube
    result_5 = db.video.aggregate([
        {
            '$sort': {'like_count': -1}
        },
        {
            '$limit': 10
        },
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$unwind': '$playlist_info'
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$project': {
                'video_name': '$video_name',
                'channel_name': '$channel_info.channel_name',
                'like_count': 1
            }
        }
    ])

    st.write("\nQuestion 5:")
    
    # Print the results
    # for result in result_5:
    #     print(result)

    
    result_list_sorted = sorted(result_5, key=lambda x: (x['like_count']), reverse=True)
    #print(f"result_list_sorted::{result_list_sorted}")
    result_table_5 = [{
        "Channel Name": result.get('channel_name', 'N/A')[0],
        "Video Name": result.get('video_name', 'N/A'),
        "Like Count": (result['like_count'])
    } for result in result_list_sorted]

    st.table(result_table_5)

# Example: Question 6
def question_6():
    client = init_connection()
    db = client.youtube
    result_6 = db.video.aggregate([
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$unwind': '$playlist_info'
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$project': {
                'video_name': '$video_name',
                'channel_name': '$channel_info.channel_name',
                'like_count': 1,
                'dislike_count': 1
            }
        }
    ])

    st.write("\nQuestion 6:")
    
    # Print the results
    # for result in result_6:
    #     print(result)

    result_table_6 = [{
        "Channel Name": result.get('channel_name', 'N/A')[0],
        "Video Name": result.get('video_name', 'N/A'),
        "Like Count": result.get('like_count', 0),
        "Dislike Count": result.get('dislike_count', 0)
    } for result in result_6]

    st.table(result_table_6)

# Example: Question 7
def question_7():
    client = init_connection()
    db = client.youtube
    result_7 = db.channel.find({}, {'channel_name': 1, 'channel_views': 1})

    st.write("\nQuestion 7:")
    
    # Print the results
    # for result in result_7:
    #     print(result)

    result_table_7 = [{
        "Channel Name": result.get('channel_name', 'N/A'),
        "Total Views": result.get('channel_views', 0)
    } for result in result_7]

    st.table(result_table_7)

# Example: Question 8
def update_video_dates():
    client = init_connection()
    db = client.youtube
    videos = db.video.find()

    for video in videos:
        # Convert the string date to a datetime object
        try:
            new_publish_date = datetime.strptime(video['publish_date'], "%Y-%m-%dT%H:%M:%SZ")

            # Update the document with the new date format
            db.video.update_one(
                {'_id': video['_id']},
                {'$set': {'publish_date': new_publish_date}}
            )
        except:
            pass

    print("Update complete.")
def question_8():
    #update_video_dates()
    client = init_connection()
    db = client.youtube
    num_documents = db.video.count_documents({
        'publish_date': {
            '$gte': datetime(2022, 1, 1),
            '$lt': datetime(2023, 1, 1)
        }
    })
    print(f"Number of documents in the date range: {num_documents}")

    result_8 = db.video.aggregate([
        {
            '$match': {
                'publish_date': {
                    '$gte': datetime(2022, 1, 1),
                    '$lt': datetime(2023, 1, 1)
                }
            }
        },
        {
            '$project': {
                '_id': 0,
                'video_name': 1
            }
        }
    ])

    st.write("\nQuestion 8:")
    
    # Debug print: Check the aggregation pipeline result
    pipeline_result = list(result_8)
    print(f"Aggregation result: {pipeline_result}")

    # Print the results
    for result in pipeline_result:
        print(result)

    result_table_8 = [{
        "Video Name": result.get('video_name', 'N/A')
    } for result in pipeline_result]

    st.table(result_table_8)

def min_conv():
    from datetime import datetime, timedelta
    client = init_connection()
    db = client.youtube
    documents = db.video.find({ "duration": { "$exists": True } })
    for doc in documents:
        duration_str = doc["duration"]
        try:
            if 'H' in duration_str and 'M' in duration_str and 'S' in duration_str:
                # Hours, minutes, and seconds format "PT1H7M57S"
                duration_obj = timedelta(
                    hours=int(duration_str.split('H')[0].replace("PT", "")),
                    minutes=int(duration_str.split('H')[1].split('M')[0]),
                    seconds=int(duration_str.split('M')[1].split('S')[0])
                )
                duration_minutes = duration_obj.total_seconds() / 60.0
            elif 'M' in duration_str and 'S' in duration_str:
                # Minutes and seconds format "PT5M32S"
                duration_obj = datetime.strptime(duration_str, "PT%MM%SS")
                duration_minutes = duration_obj.minute + duration_obj.second / 60.0
            elif 'M' in duration_str:
                # Only minutes format "PT25M"
                duration_obj = timedelta(minutes=int(duration_str.replace("PT", "").replace("M", "")))
                duration_minutes = duration_obj.total_seconds() / 60.0
            else:
                # Only seconds format "PT8S"
                duration_obj = timedelta(seconds=int(duration_str.replace("PT", "").replace("S", "")))
                duration_minutes = duration_obj.total_seconds() / 60.0
            db.video.update_one(
                { "_id": doc["_id"] },  # Assuming you have an "_id" field as the document identifier
                { "$set": { "duration": duration_minutes } }
            )
        except:
            pass

# Example: Question 9
def question_9():
    #min_conv()
    client = init_connection()
    db = client.youtube
    result = db.video.aggregate([
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$group': {
                '_id': '$channel_info.channel_id',
                'average_duration': {'$avg': {'$toDouble': '$duration'}}
            }
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': '_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$project': {
                'channel_name': '$channel_info.channel_name',
                'average_duration': 1
            }
        }
    ])

    # Print the results
    # for doc in result:
    #     print(f"Channel: {doc['channel_name']}, Average Duration: {doc['average_duration']} minutes")
    result_table = [{"Channel Name": doc['channel_name'][0], "Average Duration": doc['average_duration']} for doc in result]
    st.table(result_table)

# Example: Question 10
def question_10():
    client = init_connection()
    db = client.youtube
    result_10 = db.comment.aggregate([
        {
            '$group': {
                '_id': '$video_id',
                'comment_count': {'$sum': 1}
            }
        },
        {
            '$sort': {'comment_count': -1}
        },
        {
            '$limit': 10
        },
        {
            '$lookup': {
                'from': 'video',
                'localField': '_id',
                'foreignField': 'video_id',
                'as': 'video_info'
            }
        },
        {
            '$lookup': {
                'from': 'playlist',
                'localField': 'video_info.playlist_id',
                'foreignField': 'playlist_id',
                'as': 'playlist_info'
            }
        },
        {
            '$lookup': {
                'from': 'channel',
                'localField': 'playlist_info.channel_id',
                'foreignField': 'channel_id',
                'as': 'channel_info'
            }
        },
        {
            '$project': {
                'video_name': '$video_info.video_name',
                'channel_name': '$channel_info.channel_name',
                'comment_count': 1
            }
        }
    ])

    st.write("\nQuestion 10:")
    
    # Print the results
    # for result in result_10:
    #     print(result)

    # Display the results in a table using Streamlit
    result_table_10 = [{
        "Channel Name": result['channel_name'][0],
        "Video Name": result['video_name'][0],
        
        "Comment Count": result['comment_count']
    } for result in result_10]

    st.table(result_table_10)


if __name__ == "__main__":
    run()
