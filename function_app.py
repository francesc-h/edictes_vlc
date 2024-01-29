# https://github.com/Azure/azure-functions-core-tools/issues/1821#issuecomment-610060492
from typing import List, Set, Dict, Tuple
import azure.functions as func

from twitter_wrapper import post_tweets
from helpers import process_url

from bs4 import BeautifulSoup
import requests, logging

LIST_URL = "https://sede.valencia.es/sede/edictos/index/materia/LA"


def process_db(prevDocuments: func.DocumentList) -> Tuple[Set[str], List[func.Document]]:
    # Old docs that have been tweeted or are pending
    ids = []
    pending = []
    
    for doc in prevDocuments:
        # If doc has already been tweeted, ignore it
        if (doc.get("tweet", False)):
            ids.append(doc.get("id"))
        else:
            # else, take it into account
            pending.append(doc)

    ids = set(ids)

    logging.info(f"Prev docs ({len(ids)}): {ids}")
    logging.info(f"Docs pending to be tweeted (({len(pending)})): {pending}")

    return ids, pending


def get_published() -> List[Dict]:
    req = requests.get(LIST_URL)
    doc = BeautifulSoup(req.text, 'html.parser')

    edictes = doc.select('.rotuloAnuncio a')
    links = [e["href"] for e in edictes]
    
    published = [process_url(url) for url in links]
    logging.info(f"Edictes publicats: {published}")
    
    return published


app = func.FunctionApp()
@app.schedule(schedule="0 9 1-31 1-12 *", arg_name="myTimer", run_on_startup=True, use_monitor=False) 
@app.cosmos_db_input(
    arg_name="prevDocuments", 
    database_name="edictes",
    container_name="container_edictes",
    #partition_key="{msg.payload_property}",
    connection="DB_connection"
)
@app.cosmos_db_output(
    arg_name="newDocuments", 
    database_name="edictes",
    container_name="container_edictes",
    connection="DB_connection"
)
def timer_trigger(
    myTimer: func.TimerRequest,
    prevDocuments: func.DocumentList,
    newDocuments: func.Out[func.DocumentList]
    ) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    ids, pending = process_db(prevDocuments)
    published = get_published()

    # Filter out docs that have already been published
    new_docs = [doc for doc in published if doc["id"] not in ids]
    logging.info(f"Edictes nous: {new_docs}")
    
    # Extend new docs with pending to tweet ones
    new_docs.extend(pending)
    logging.info(f"Edictes to tweet: {new_docs}")

    if (len(new_docs) > 0):
        tweet_successful = False

        try:
            post_tweets(new_docs)
            tweet_successful = True
            logging.info("Tweet successful!")
        except Exception as e:
            logging.error(e)
            pass

        documents = func.DocumentList()
        for edicte in new_docs:
            # Remove the image attribute as we don't want
            # to push it to the DB (nor it's supported)
            if ("img" in edicte):
                edicte.pop("img")
            
            edicte["tweet"] = tweet_successful
            
            documents.append(
                func.Document.from_dict(edicte)
            )
        
        newDocuments.set(documents)
    else:
        logging.info("No new docs to tweet or save to DB")
        pass
    
    logging.info('Function finished.')