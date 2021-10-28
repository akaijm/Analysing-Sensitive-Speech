import pickle
import gensim
from gensim.models.wrappers import LdaMallet
from gensim.models import CoherenceModel
from operator import itemgetter
import pandas as pd

mallet_path = 'mallet-2.0.8/bin/mallet' # also need to add environment variable MALLET_HOME on system as path to mallet-2.0.8

# Loading pickles
dictionary = pickle.load(open("dictionary2_.p", 'rb'))
doc_term_matrix = pickle.load(open("doc_term_matrix2_.p", 'rb'))

# Default values of o and n
o = 0 # optimize_interval=o, modify this to change optimize_interval
# Precalculations for all the models from n = 3 to n = 11.

for n in range(3,12):
  # Loading altered_df
  df = pickle.load(open("altered_df.p", 'rb'))
  lda_mallet = LdaMallet(mallet_path, corpus=doc_term_matrix, num_topics=n, optimize_interval=o, id2word=dictionary, random_seed=15) # LDA Mallet model
  lda_model = gensim.models.wrappers.ldamallet.malletmodel2ldamodel(lda_mallet) # LDA model 
  topics_list = lda_mallet.show_topics(formatted=False, num_words=30, num_topics=-1) # List of topics with top 30 most important tokens. [(0, [('token', weight),...]), (1, [])]

  # Use the lda_model to predict topic distribution for all texts.
  lda_est_topics = []
  lda_est_scores = []
  param = 1/n # Higher the param, more likely the document belongs to None of the Above.
  for i in range(len(doc_term_matrix)):
    topic_weights = lda_model.get_document_topics(doc_term_matrix[i])
    if max(topic_weights,key=itemgetter(1))[1] <= param: 
      lda_est_topics.append(None) # "None of the above" topic -- no majority for any of the topics
      lda_est_scores.append(0)
    else:
      lda_est_topics.append(max(topic_weights,key=itemgetter(1))[0]) # appending the topic the document belongs to, restricts the topic of the document to 1
      lda_est_scores.append(max(topic_weights,key=itemgetter(1))[1])

  df['topic_pred'] = lda_est_topics
  df['topic_pred_score'] = lda_est_scores
  #df['short_text'] = [t[:200] + "..." if len(t) > 500 else t for t in df['text']] # not necessary the next time ran

  topic_df_dict = {'topic_no': [], 'topic_words': [], 'word_weights': []}

  for i in range(n): # 0,1,2,3,4 in the case of 5
      topic_df_dict['topic_no'].append(topics_list[i][0])
      topic_df_dict['topic_words'].append(','.join([t[0] for t in topics_list[i][1]]))
      topic_df_dict['word_weights'].append(','.join([str(t[1]) for t in topics_list[i][1]]))

  topic_df = pd.DataFrame(topic_df_dict)
  df.to_csv('outputs/topic_modeling/text_data' + str(n) + '.csv',index=False)
  topic_df.to_csv('outputs/topic_modeling/topic_data' + str(n) + '.csv',index=False)
  lda_model.save("outputs/topic_modeling/lda_model" + str(n))