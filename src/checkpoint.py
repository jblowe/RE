import pickle

# All the data needed to reconstruct a Checkpoint.
class CheckpointData:
    def __init__(self, lexicons, parameter_tree):
        self.lexicons = lexicons
        self.parameter_tree = parameter_tree

def save_checkpoint_to_path(path, checkpoint_data):
    with open(path, 'wb') as f:
        pickle.dump(checkpoint_data, f)
    return path

def load_checkpoint_from_path(path):
    with open(path, "rb") as f:
        checkpoint_data = pickle.load(f)
    return checkpoint_data
