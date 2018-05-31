from skafossdk import *
from helpers import get_logger
from social.entity import SocialStatements
from tubefilter.tubefilter_proccessor import TubefilterProcessor

# Initialize the skafos sdk
ska = Skafos()

ingest_log = get_logger('user-fetch')

if __name__ == "__main__":
    ingest_log.info('Starting job')

    ingest_log.info('Fetching tubefilter user data')
    entity = SocialStatements(ingest_log, ska.engine) #
    processor = TubefilterProcessor(entity, ingest_log).fetch()
