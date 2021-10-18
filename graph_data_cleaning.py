'''
Script to prepare data for the post-centric network graph 'time_elapsed.csv', where invalid post_times are replaced with the earliest comment_time available
'''

import pandas as pd
import numpy as np

def prepare_network_data():
    data = pd.read_pickle('hashed_0_data.h5') 

    #Remove null post id
    post_data = data[data['hashed_post_id'] != 0]

    post_data=post_data.dropna(subset=['post_text','time'])

    #Get the latest information (likes, comments, shares) for each post
    post_latest=post_data.loc[post_data.groupby('hashed_post_id').time.idxmax()].reset_index(drop = True)

    #Get the oldest time recorded for each post (actual post creation date)
    post = post_data.loc[post_data.groupby('hashed_post_id').time.idxmin()].reset_index(drop = True)

    #Add the oldest post_times to the full dataset
    data_new = pd.merge(post_data, post[['hashed_post_id', 'time']], on = 'hashed_post_id')
    data_new = data_new.rename(columns = {'time_y':"post_time"})

    #Clean up the data by removing null entries and duplicates, and concatenate replies and comments together

    comment_data = data_new[data_new['hashed_comment_id'] != 0]
    comment_data=comment_data.dropna(subset=['comment_text','comment_time'])
    comment_data=comment_data[comment_data['comment_text']!= ""]
    comment_sorted=comment_data.loc[comment_data.groupby('hashed_comment_id').comment_time.idxmin()].reset_index(drop = True)
    comment_sorted=comment_sorted[['group','likes','comments','shares','reactions','reaction_count','hashed_post_id', 'post_text',
                    'hashed_comment_id','hashed_commenter_name','comment_text','post_time','comment_time','comment_text_pred','comment_text_pred_prob']]
                

    reply_data = comment_data[comment_data['hashed_reply_comment_id'] != 0]
    reply =reply_data.dropna(subset=['reply_comment_text','reply_comment_time'])
    reply =reply[reply['reply_comment_text']!= ""]
    reply=reply.loc[reply.groupby('reply_comment_text').reply_comment_time.idxmin()].reset_index(drop = True)
    reply=reply[['group','likes','comments','shares','reactions','reaction_count','hashed_post_id','post_text',
                    'hashed_reply_comment_id','hashed_reply_commenter_name','reply_comment_text', 'post_time',
                    'reply_comment_time','reply_comment_text_pred','reply_comment_text_pred_prob']]
    reply = reply.rename(columns = {"hashed_reply_comment_id":"hashed_comment_id", "hashed_reply_commenter_name":"hashed_commenter_name", "reply_comment_text":"comment_text",
                    "reply_comment_time":"comment_time", "reply_comment_text_pred":"comment_text_pred", "reply_comment_text_pred_prob":"comment_text_pred_prob"})

    responses = pd.concat([comment_sorted, reply]).reset_index(drop = True)

    #Get the earliest comment time for each post
    checkData = responses[['hashed_post_id', 'post_time', 'comment_time']].groupby('hashed_post_id').min().reset_index()
    responses_new = pd.merge(responses, checkData[['hashed_post_id', 'comment_time']], on = 'hashed_post_id', suffixes = [None, "_new"])

    #Replace the invalid post_times which occur before the earliest comments, with the respective earliest comment times.
    responses_new['post_time'] = responses_new.apply(lambda x:x['comment_time_new'] if x['comment_time_new'] < x['post_time'] else x['post_time'], axis = 1)

    responses_new['time_elapsed'] = responses_new['comment_time'] - responses_new['post_time']

    #Save to CSV
    responses_new.to_csv('time_elapsed.csv', index = False)
if __name__ == "__main__":
    prepare_network_data()
