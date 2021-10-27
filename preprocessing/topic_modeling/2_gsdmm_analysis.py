import pickle
import pandas as pd
from gsdmm.gsdmm import MovieGroupProcess

# Loading pickles
dictionary = pickle.load(open("dictionary2_.p", 'rb'))
doc_term_matrix = pickle.load(open("doc_term_matrix2_.p", 'rb'))

# Data preparation
vocab = list(dictionary.token2id.keys())
vocab_size = len(vocab)
# [['free_trade', 'singapore'], []]
unique_id_matrix = [[s[0] for s in l] for l in doc_term_matrix]
unique_tokens_matrix = [[dictionary[t] for t in l] for l in unique_id_matrix]

for n in range(3,12):
    # Initialising a MovieGroupProcess
    mgp = MovieGroupProcess(K=n, alpha=0.1, beta=0.1, n_iters=30) # K should be larger than the number of clusters you expect to exist in your data, as algo can never return more than K clusters.
    # Model fitting
    gsdmm_model = mgp.fit(unique_tokens_matrix, vocab_size=vocab_size)
    # Structuring model results
    topic_df_dict = {'topic_no': [], 'topic_words': [], 'word_weights': []}
    for c in range(n):
        temp = sorted(mgp.cluster_word_distribution[c].items(), key=lambda k: k[1], reverse=True)[:30]
        # mgp.cluster_word_distribution[c].items() looks like [('pap', 1004), ('vote', 964)]
        temp_sum_weight = sum(j for i,j in temp)
        topic_df_dict['topic_no'].append(c)
        topic_df_dict['topic_words'].append(','.join([i[0] for i in temp]))
        topic_df_dict['word_weights'].append(','.join([str(float(i[1]) / temp_sum_weight) for i in temp]))

    topic_df = pd.DataFrame(topic_df_dict)
    # Predicting cluster for each text in the test dataset
    df = pickle.load(open("altered_df.p", 'rb'))
    gsdmm_est_topics = []
    gsdmm_est_scores = []
    param = 1/n # Higher the param, more likely the document belongs to None of the Above.
    for t in range(len(unique_tokens_matrix)):
        topic_weights = mgp.score(unique_tokens_matrix[t]) # need to use tokenised text
        max_weight = max(topic_weights)
        if max_weight <= param: 
            gsdmm_est_topics.append(None) # "None of the above" topic -- no majority for any of the topics
            gsdmm_est_scores.append(0)
        else:
            gsdmm_est_scores.append(max_weight)
            gsdmm_est_topics.append(gsdmm_model[t]) # the classified result for each of the sentences in unique_tokens_matrix
            
    df['topic_pred'] = gsdmm_est_topics
    df['topic_pred_score'] = gsdmm_est_scores

    df.to_csv('outputs/topic_modeling/gsdmm_outputs/text_data' + str(n) + '.csv',index=False)
    topic_df.to_csv('outputs/topic_modeling/gsdmm_outputs/topic_data' + str(n) + '.csv',index=False)
    pickle.dump(mgp, open("outputs/topic_modeling/gsdmm_outputs/gsdmm_mgp" + str(n), "wb"))