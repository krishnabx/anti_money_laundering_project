import logging
import dask.dataframe as dd

# Configure logging
logging.basicConfig(filename='merge_transactions_with_graph_features.log', level=logging.INFO)
# Define a stream handler to write log messages to the terminal
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# Create a formatter and set it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)

# Add the handler to the root logger
logging.getLogger('').addHandler(console)

def merge_trans_with_gf(transactions_ddf, graph_features_ddf):
    logging.info("Starting merging transactions with graph features")

    try:
        transactions_ddf = kwargs['task_instance'].xcom_pull(task_ids='create_graph', key='G_data')['ddf']
        graph_features_ddf = kwargs['task_instance'].xcom_pull(task_ids='create_dask_dataframe', key='graph_features_ddf')
        # Merge on From_ID
        merged_ddf = dd.merge(transactions_ddf, graph_features_ddf, left_on='From_ID', right_on='Node', how='left')

        # Rename columns to avoid conflicts
        merged_ddf = merged_ddf.rename(columns={
            'degree': 'from_degree',
            'in_degree': 'from_in_degree',
            'out_degree': 'from_out_degree',
            'clustering_coefficient': 'from_clustering_coeff',
            'degree_centrality': 'from_degree_centrality'
        })

        # Merge on To_ID
        merged_ddf = dd.merge(merged_ddf, graph_features_ddf, left_on='To_ID', right_on='Node', how='left')

        # Rename columns again
        merged_ddf = merged_ddf.rename(columns={
            'degree': 'to_degree',
            'in_degree': 'to_in_degree',
            'out_degree': 'to_out_degree',
            'clustering_coefficient': 'to_clustering_coeff',
            'degree_centrality': 'to_degree_centrality'
        })

        # Drop redundant columns
        merged_ddf = merged_ddf.drop(columns=['Node_x', 'Node_y'])
        
        logging.info("Merging transactions with graph features finished")
        logging.info("merged_ddf head after merge: %s", str(merged_ddf.head(1)))
        kwargs['task_instance'].xcom_push(key='merged_ddf', value=merged_ddf)
        return merged_ddf

    except Exception as e:
        logging.error(f"An error occurred during merging transactions with graph features: {e}")
        return None
