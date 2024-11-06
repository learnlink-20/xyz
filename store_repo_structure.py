import os
import json
from github import Github
from pymongo import MongoClient
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

def fetch_repo_structure(repo_name, owner='learnlink-20'):
    """
    Fetch the repository structure for a given repository.
    
    Args:
        repo_name (str): Name of the repository
        owner (str): Owner of the repository
    
    Returns:
        dict: Repository structure
    """
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f'{owner}/{repo_name}')
    return process_folder(repo)

def process_folder(repo, path=''):
    """
    Process a folder in the repository and return its structure.
    
    Args:
        repo: GitHub repository object
        path (str): Path within the repository
    
    Returns:
        dict: Folder structure
    """
    contents = repo.get_contents(path)
    folder_structure = {
        'readme': None,
        'media': [],
        'assets': []
    }
    
    for item in contents:
        if item.type == 'file':
            raw_url = item.download_url
            if item.name.lower() == 'readme.md':
                folder_structure['readme'] = raw_url
            elif item.name.endswith(('.mp4', '.jpg', '.jpeg', '.png')):
                folder_structure['media'].append(raw_url)
            else:
                folder_structure['assets'].append(raw_url)
        elif item.type == 'dir':
            folder_structure[item.name] = process_folder(repo, item.path)
    
    return folder_structure

def store_in_mongodb(repo_name, structure):
    """
    Store the repository structure in MongoDB.
    
    Args:
        repo_name (str): Name of the repository
        structure (dict): Repository structure to store
    """
    client = MongoClient(MONGODB_URI)
    db = client['myDatabase']
    collection = db['repoStructures']
    
    collection.update_one(
        {'repo': repo_name},
        {
            '$set': {
                'structure': structure,
                'lastUpdated': datetime.datetime.utcnow()
            }
        },
        upsert=True
    )
    print('Repository structure stored successfully')

def main():
    repo_name = 'lab-1'  # Specify your repository name
    structure = fetch_repo_structure(repo_name)
    store_in_mongodb(repo_name, structure)

if __name__ == '__main__':
    main()
